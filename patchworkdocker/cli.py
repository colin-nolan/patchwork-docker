import dataclasses
import json
import logging
import sys
from argparse import ArgumentParser
from dataclasses import dataclass
from enum import Enum, unique
from typing import List, Dict, Optional, Union

import logzero
from logzero import logger

from patchworkdocker._external.key_value_string_parser import KeyValueStringParserAction
from patchworkdocker._external.verbosity_argument_parser import verbosity_parser_configuration, VERBOSE_PARAMETER_KEY, \
    get_verbosity, DEFAULT_LOG_VERBOSITY_KEY
from patchworkdocker.core import PatchworkDocker
from patchworkdocker.meta import EXECUTABLE_NAME, DESCRIPTION, VERSION

ACTION_PARAMETER = "action"
IMPORT_REPOSITORY_FROM_PARAMETER = "context"
ADDITIONAL_FILES_LONG_PARAMETER = "additional-file"
ADDITIONAL_FILES_SHORT_PARAMETER = "f"
PATCHES_LONG_PARAMETER = "patch"
PATCHES_SHORT_PARAMETER = "p"
DOCKERFILE_LOCATION_LONG_PARAMETER = "dockerfile"
DOCKERFILE_LOCATION_SHORT_PARAMETER = "d"
IMAGE_NAME_PARAMETER = "image-name"
BUILD_LOCATION_LONG_PARAMETER = "build-location"
BUILD_LOCATION_SHORT_PARAMETER = "b"
VERBOSITY_SHORT_PARAMETER = verbosity_parser_configuration[VERBOSE_PARAMETER_KEY]
DRY_RUN_LONG_PARAMETER = "dry-run"
BASE_IMAGE_SHORT_PARAMETER = "i"
BASE_IMAGE_LONG_PARAMETER = "base-image"

DEFAULT_ADDITIONAL_FILES = {}
DEFAULT_PATCHES = {}
DEFAULT_DOCKERFILE_LOCATION = "Dockerfile"
DEFAULT_VERBOSITY = verbosity_parser_configuration[DEFAULT_LOG_VERBOSITY_KEY]


@unique
class ActionValue(Enum):
    """
    Program action.
    """
    BUILD = "build"
    PREPARE = "prepare"


@dataclass
class BaseCliConfiguration:
    """
    Base CLI configuration.
    """
    log_verbosity: int
    dry_run: bool


@dataclass
class SubcommandCliConfiguration(BaseCliConfiguration):
    """
    CLI configuration for subcommands.
    """
    additional_files: Dict[str, str]
    patches: Dict[str, str]
    dockerfile_location: str
    build_location: Optional[str]
    import_from: str
    base_image: str


@dataclass
class PrepareCliConfiguration(SubcommandCliConfiguration):
    """
    CLI configuration for preparing a patchwork Docker build.
    """


@dataclass
class BuildCliConfiguration(SubcommandCliConfiguration):
    """
    CLI configuration for building a patchwork Docker image.
    """
    image_name: str


def _create_parser() -> ArgumentParser:
    """
    Creates an argument parser.
    :return: the created parser
    """
    parser = ArgumentParser(prog=EXECUTABLE_NAME, description=f"{DESCRIPTION} (v{VERSION})")
    parser.add_argument(f"-{VERBOSITY_SHORT_PARAMETER}", action="count", default=0,
                        help="increase the level of log verbosity (add multiple increase further)")
    parser.add_argument(f"--{DRY_RUN_LONG_PARAMETER}", action="store_true", default=False, help="")
    subparsers = parser.add_subparsers(dest=ACTION_PARAMETER, help="TODO")

    def take_context_arguments(parser: ArgumentParser):
        parser.add_argument(IMPORT_REPOSITORY_FROM_PARAMETER, help="TODO")

    def take_common_arguments(parser: ArgumentParser):
        parser.add_argument(f"-{ADDITIONAL_FILES_SHORT_PARAMETER}", f"--{ADDITIONAL_FILES_LONG_PARAMETER}",
                            action=KeyValueStringParserAction, default=DEFAULT_ADDITIONAL_FILES,
                            help="Files to add to the build context (will override existing files). Input in the form:")
        parser.add_argument(f"-{PATCHES_SHORT_PARAMETER}", f"--{PATCHES_LONG_PARAMETER}",
                            action=KeyValueStringParserAction, help="TODO", default=DEFAULT_PATCHES)
        parser.add_argument(f"-{DOCKERFILE_LOCATION_SHORT_PARAMETER}", f"--{DOCKERFILE_LOCATION_LONG_PARAMETER}",
                            help="TODO", default=DEFAULT_DOCKERFILE_LOCATION)
        parser.add_argument(f"-{BUILD_LOCATION_SHORT_PARAMETER}", f"--{BUILD_LOCATION_LONG_PARAMETER}",
                            help="TODO", default=None)
        parser.add_argument(f"-{BASE_IMAGE_SHORT_PARAMETER}", f"--{BASE_IMAGE_LONG_PARAMETER}",
                            help="TODO", default=None)

    build_parser = subparsers.add_parser(ActionValue.BUILD.value, help="TODO")
    take_context_arguments(build_parser)
    build_parser.add_argument(IMAGE_NAME_PARAMETER, help="TODO")
    take_common_arguments(build_parser)

    prepare_parser = subparsers.add_parser(ActionValue.PREPARE.value, help="TODO")
    take_context_arguments(prepare_parser)
    take_common_arguments(prepare_parser)

    return parser


def parse_cli_configuration(arguments: List[str]) -> BaseCliConfiguration:
    """
    Parses the given CLI arguments.
    :param arguments: the arguments from the CLI
    :return: parsed configuration
    """
    # XXX: Setting a value other than the display string seems to be non-trivial: https://bugs.python.org/issue23487
    parsed_arguments = _create_parser().parse_args(arguments)
    parsed_arguments = {x.replace("_", "-"): y for x, y in vars(parsed_arguments).items()}
    action_value = parsed_arguments[ACTION_PARAMETER]
    if action_value is None:
        logger.error("No action specified")
        _create_parser().print_help(sys.stderr)
        exit(1)
    parsed_arguments[ACTION_PARAMETER] = ActionValue(action_value)

    cli_configuration_class = {
        ActionValue.BUILD: BuildCliConfiguration,
        ActionValue.PREPARE: PrepareCliConfiguration
    }[parsed_arguments[ACTION_PARAMETER]]

    extra_configuration = {}
    if issubclass(cli_configuration_class, BuildCliConfiguration):
        extra_configuration["image_name"] = parsed_arguments[IMAGE_NAME_PARAMETER]

    cli_configuration = cli_configuration_class(
        log_verbosity=get_verbosity(parsed_arguments),
        dry_run=parsed_arguments[DRY_RUN_LONG_PARAMETER],
        additional_files=parsed_arguments[ADDITIONAL_FILES_LONG_PARAMETER],
        patches=parsed_arguments[PATCHES_LONG_PARAMETER],
        dockerfile_location=parsed_arguments[DOCKERFILE_LOCATION_LONG_PARAMETER],
        build_location=parsed_arguments[BUILD_LOCATION_LONG_PARAMETER],
        import_from=parsed_arguments[IMPORT_REPOSITORY_FROM_PARAMETER],
        base_image=parsed_arguments[BASE_IMAGE_LONG_PARAMETER],
        **extra_configuration
    )

    return cli_configuration


def _set_log_level(level: int):
    """
    Sets the log level to that given.
    :param level: log level to set
    """
    logzero.loglevel(level)
    if level == logging.WARNING:
        logger.warning("There are not likely to be many WARN level logs: consider increasing the verbosity by adding"
                       f"more -{VERBOSITY_SHORT_PARAMETER}")


def print_configuration(configuration: BaseCliConfiguration):
    """
    Prints information about the given configuration to stdout.
    :param configuration: configuration to output
    """
    configuration_as_json = json.dumps(dataclasses.asdict(configuration))
    print(configuration_as_json)


def build(core: PatchworkDocker, configuration: BuildCliConfiguration):
    """
    Builds patchwork Docker image with the given configuration.
    :param core: patchwork Docker core
    :param configuration: build configuration
    :return:
    """
    core.build(configuration.image_name, configuration.build_location)


def prepare(core: PatchworkDocker, configuration: PrepareCliConfiguration):
    """
    Prepares for patchwork Docker build.
    :param core: patchwork Docker core
    :param configuration: build configuration
    :return:
    """
    output = core.prepare(configuration.build_location)
    print(output)


def main(cli_arguments: List[str]):
    """
    Main.
    :param cli_arguments: arguments passed in via the CLI
    :raises SystemExit: always raised
    """
    cli_configuration = parse_cli_configuration(cli_arguments)

    if cli_configuration.log_verbosity:
        _set_log_level(cli_configuration.log_verbosity)

    if cli_configuration.dry_run:
        print_configuration(cli_configuration)
        exit(0)

    # XXX: Ideally, we would use `configuration: Intersect[ContextUsingCliConfiguration, SubcommandCliConfiguration]
    # but multiple bounds are sadly not supported in Python's type hinting: https://github.com/python/typing/issues/213
    def create_core(configuration: Union[PrepareCliConfiguration, BuildCliConfiguration]) -> PatchworkDocker:
        return PatchworkDocker(configuration.import_from, additional_files=configuration.additional_files,
                               patches=configuration.patches, dockerfile_location=configuration.dockerfile_location,
                               base_image=cli_configuration.base_image)

    {
        BuildCliConfiguration: lambda: build(create_core(cli_configuration), cli_configuration),
        PrepareCliConfiguration: lambda: prepare(create_core(cli_configuration), cli_configuration),
    }[type(cli_configuration)]()


def entrypoint():
    """
    Entry-point to be used by CLI.
    """
    logger.setLevel(DEFAULT_VERBOSITY)
    main(sys.argv[1:])


if __name__ == "__main__":
    entrypoint()
