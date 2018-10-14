import logging
import os
import shutil
from typing import Dict, Tuple, Optional

import fire
from frozendict import frozendict
from logzero import setup_logger

from patchworkdocker.docker_images import build_docker_image
from patchworkdocker.importers import ImporterFactory
from patchworkdocker.modifiers import copy_file, apply_patch

logger = setup_logger()
_importer_factory = ImporterFactory()

logger.setLevel(logging.DEBUG)


def _process_source_and_destination(src: str, dest: Optional[str], repository_location: str) -> Tuple[str, str]:
    """
    TODO
    :param src:
    :param dest:
    :param repository_location:
    :return:
    """
    src = os.path.abspath(src)
    if not os.path.exists(src):
        raise ValueError(f"Source path does not exist: {src}")

    assert os.path.isabs(repository_location)
    if dest is None:
        # FIXME: Does not apply to patches!
        dest = os.path.basename(src)
    if os.path.isabs(dest):
        raise ValueError(f"Destinations should be relative: {dest}")
    dest = os.path.join(repository_location, dest)

    return src, dest


def run(image_name: str, import_repository_from: str, *, additional_files: Dict[str, Optional[str]]=(),
        patches: Dict[str, str]=frozendict(), dockerfile_location: str="Dockerfile"):
    """
    TODO
    :param image_name: image tag (can optionally include a version tag)
    :param import_repository_from:
    :param additional_files: (added in the order given, overwrites possible)
    :param patches: (applied in the order given)
    :param dockerfile_location: location of the Dockerfile to build, relative to the root of the repository
    :return:
    """
    if os.path.isabs(dockerfile_location):
        raise ValueError("Dockerfile location must be relative to the root of the repository")

    repository_location = _importer_factory.create(import_repository_from).load(import_repository_from)
    logger.info(f"Imported repository at {import_repository_from} to {repository_location}")

    for src, dest in (_process_source_and_destination(src, dest, repository_location)
                      for src, dest in additional_files.items()):
        logger.info(f"{'Overwriting' if os.path.exists(dest) else 'Creating'} {dest} with {src}")
        copy_file(src, dest)

    for src, dest in (_process_source_and_destination(src, dest, repository_location)
                      for src, dest in patches.items()):
        logger.info(f"Patching {dest} with {src}")
        apply_patch(src, dest)

    build_docker_image(image_name, repository_location, dockerfile_location)

    shutil.rmtree(repository_location)




if __name__ == "__main__":
    fire.Fire(run)
