import os

from logzero import setup_logger
from thriftybuilder.build_configurations import DockerBuildConfiguration
from thriftybuilder.builders import BuildFailedError as ThriftyBuildFailedError
from thriftybuilder.builders import DockerBuilder
from thriftybuilder.builders import logger as thrifty_logger

from patchworkdocker._common import PatchworkDockerError

logger = setup_logger()


class DockerBuildError(PatchworkDockerError):
    """
    Docker build error.
    """


def build_docker_image(image_name: str, context: str, dockerfile: str):
    """
    Builds a Docker image with the given tag from the given Dockerfile in the given context.
    :param image_name: image tag (can optionally include a version tag)
    :param context: context to build the image in
    :param dockerfile: Dockerfile to build the image from
    :raises BuildFailedError: raised if an error occurs during the build
    """
    build_configuration = DockerBuildConfiguration(image_name, os.path.join(context, dockerfile), context)

    thrifty_logger.setLevel(logger.level)
    builder = DockerBuilder((build_configuration,))

    try:
        builder.build(build_configuration)
    except ThriftyBuildFailedError as e:
        raise DockerBuildError(f"Error building image: {image_name}") from e
