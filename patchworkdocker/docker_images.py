import os

import docker
from docker.errors import BuildError

from patchworkdocker.errors import PatchworkDockerError


class DockerBuildError(PatchworkDockerError):
    """
    Docker build error.
    """


def build_docker_image(image_name: str, context: str, dockerfile: str):
    """
    Builds a Docker image with the given tag from the given Dockerfile in the given context.
    :param image_name: image tag (can optionally include a version tag)
    :param context: context to build the image in (absolute file path)
    :param dockerfile: Dockerfile to build the image from (absolute file path)
    :raises BuildFailedError: raised if an error occurs during the build
    """
    if not os.path.isabs(context):
        raise ValueError(f"Context location must be absolute: {context}")
    if not os.path.isabs(dockerfile):
        raise ValueError(f"Dockerfile location must be absolute: {dockerfile}")

    client = docker.from_env()
    try:
        client.images.build(path=context, dockerfile=dockerfile, tag=image_name)
    except BuildError as e:
        raise DockerBuildError(f"Error building image: {image_name}") from e
