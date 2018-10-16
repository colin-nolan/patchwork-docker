import json
import logging
import sys
from argparse import ArgumentParser, Action
from dataclasses import dataclass
from enum import Enum, unique
from json import JSONDecodeError
from typing import List, Dict, Optional

import logzero
from logzero import logger

from patchworkdocker.core import get_input_files, Core
from patchworkdocker.meta import EXECUTABLE_NAME, DESCRIPTION, VERSION
from patchworkdocker._external.verbosity_argument_parser import verbosity_parser_configuration, VERBOSE_PARAMETER_KEY, \
    get_verbosity

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
VERBOSITY_PARAMETER = verbosity_parser_configuration[VERBOSE_PARAMETER_KEY]

DEFAULT_ADDITIONAL_FILES = {}
DEFAULT_PATCHES = {}
DEFAULT_DOCKERFILE_LOCATION = "Dockerfile"


@unique
class ActionValue(Enum):
    """
    TODO
    """
    INPUT_FILES = "inputfiles"
    BUILD = "build"
    PREPARE = "prepare"


@dataclass
class BaseCliConfiguration:
    """
    Base CLI configuration.
    """
    log_verbosity: int


@dataclass
class SubcommandCliConfiguration(BaseCliConfiguration):
    """
    TODO
    """
    additional_files: Dict[str, str]
    patches: Dict[str, str]
    dockerfile_location: str
    build_location: Optional[str]


@dataclass
class ContextUsingCliConfiguration:
    """
    TODO
    """
    import_from: str


@dataclass
class InputFilesCliConfiguration(SubcommandCliConfiguration):
    """
    TODO
    """


@dataclass
class PrepareCliConfiguration(SubcommandCliConfiguration, ContextUsingCliConfiguration):
    """
    TODO
    """


@dataclass
class BuildCliConfiguration(SubcommandCliConfiguration, ContextUsingCliConfiguration):
    """
    TODO
    """
    image_name: str


class _StringDictParseAction(Action):
    """
    TODO
    """
    def __call__(self, parser, namespace, values, option_string=None):
        try:
            value_as_json = json.loads(values)
            if type(value_as_json) is not dict:
                raise ValueError(f"Not an acceptable JSON value: {values}")
            getattr(namespace, self.dest, {}).update(value_as_json)
        except JSONDecodeError:
            if ":" not in values:
                raise ValueError(f"Unable to parse: {values}")
            key, value = values.split(":")
            getattr(namespace, self.dest, {})[key] = value


def _create_parser() -> ArgumentParser:
    """
    TODO
    :return:
    """
    parser = ArgumentParser(prog=EXECUTABLE_NAME, description=f"{DESCRIPTION} (v{VERSION})")
    parser.add_argument(f"-{VERBOSITY_PARAMETER}", action="count", default=0,
                        help="increase the level of log verbosity (add multiple increase further)")
    subparsers = parser.add_subparsers(dest=ACTION_PARAMETER, help="TODO")

    def take_context_arguments(parser: ArgumentParser):
        parser.add_argument(IMPORT_REPOSITORY_FROM_PARAMETER,
                            help="TODO")

    def take_common_arguments(parser: ArgumentParser):
        parser.add_argument(f"-{ADDITIONAL_FILES_SHORT_PARAMETER}", f"--{ADDITIONAL_FILES_LONG_PARAMETER}",
                            action=_StringDictParseAction, help="TODO", default=DEFAULT_ADDITIONAL_FILES)
        parser.add_argument(f"-{PATCHES_SHORT_PARAMETER}", f"--{PATCHES_LONG_PARAMETER}",
                            action=_StringDictParseAction, help="TODO", default=DEFAULT_PATCHES)
        parser.add_argument(f"-{DOCKERFILE_LOCATION_SHORT_PARAMETER}", f"--{DOCKERFILE_LOCATION_LONG_PARAMETER}",
                            help="TODO", default=DEFAULT_DOCKERFILE_LOCATION)
        parser.add_argument(f"-{BUILD_LOCATION_SHORT_PARAMETER}", f"--{BUILD_LOCATION_LONG_PARAMETER}",
                            help="TODO", default=None)

    input_files_parser = subparsers.add_parser(ActionValue.INPUT_FILES.value, help="TODO")
    take_common_arguments(input_files_parser)

    build_parser = subparsers.add_parser(ActionValue.BUILD.value, help="TODO")
    build_parser.add_argument(IMAGE_NAME_PARAMETER, help="TODO")
    take_context_arguments(build_parser)
    take_common_arguments(build_parser)

    prepare_parser = subparsers.add_parser(ActionValue.PREPARE.value, help="TODO")
    take_context_arguments(prepare_parser)
    take_common_arguments(prepare_parser)

    return parser


def parse_cli_configuration(arguments: List[str]) -> None:
    """
    Parses the given CLI arguments.
    :param arguments: the arguments from the CLI
    :return: parsed configuration
    """
    parsed_arguments = {x.replace("_", "-"): y for x, y in vars(_create_parser().parse_args(arguments)).items()}
    # XXX: Setting a value other than the display string seems to be non-trivial: https://bugs.python.org/issue23487
    parsed_arguments[ACTION_PARAMETER] = ActionValue(parsed_arguments[ACTION_PARAMETER])

    cli_configuration_class = {
        ActionValue.INPUT_FILES: InputFilesCliConfiguration,
        ActionValue.BUILD: BuildCliConfiguration,
        ActionValue.PREPARE: PrepareCliConfiguration
    }[parsed_arguments[ACTION_PARAMETER]]

    extra_configuration = {}
    if issubclass(cli_configuration_class, ContextUsingCliConfiguration):
        extra_configuration["import_from"] = parsed_arguments[IMPORT_REPOSITORY_FROM_PARAMETER]
    if issubclass(cli_configuration_class, BuildCliConfiguration):
        extra_configuration["image_name"] = parsed_arguments[IMAGE_NAME_PARAMETER]

    cli_configuration = cli_configuration_class(
        log_verbosity=get_verbosity(parsed_arguments),
        additional_files=parsed_arguments[ADDITIONAL_FILES_LONG_PARAMETER],
        patches=parsed_arguments[PATCHES_LONG_PARAMETER],
        dockerfile_location=parsed_arguments[DOCKERFILE_LOCATION_LONG_PARAMETER],
        build_location=parsed_arguments[BUILD_LOCATION_LONG_PARAMETER],
        **extra_configuration
    )

    return cli_configuration


def _set_log_level(level: int):
    """
    TODO
    :param level:
    :return:
    """
    logzero.loglevel(level)
    if level == logging.WARNING:
        logger.warning("There are not likely to be many WARN level logs: consider increasing the verbosity by adding"
                       f"more -{VERBOSITY_PARAMETER}")


def main(cli_arguments: List[str]):
    """
    Entrypoint.
    :param cli_arguments: arguments passed in via the CLI
    :raises SystemExit: always raised
    """
    cli_configuration = parse_cli_configuration(cli_arguments)

    if cli_configuration.log_verbosity:
        _set_log_level(cli_configuration.log_verbosity)

    if type(cli_configuration) is InputFilesCliConfiguration:
        input_files = get_input_files(cli_configuration.additional_files, cli_configuration.patches,
                                      cli_configuration.dockerfile_location, cli_configuration.build_location)
        print(json.dumps(input_files))
    else:
        core = Core(cli_configuration.import_from, additional_files=cli_configuration.additional_files,
                    patches=cli_configuration.patches, dockerfile_location=cli_configuration.dockerfile_location)

        if type(cli_configuration) is BuildCliConfiguration:
            core.build(cli_configuration.image_name, cli_configuration.build_location)




def entrypoint():
    """
    Entry-point to be used by CLI.
    """
    main(sys.argv[1:])


if __name__ == "__main__":
    entrypoint()


