import os
import shutil
from typing import Dict, Optional

from frozendict import frozendict
from logzero import logger

from patchworkdocker.docker_images import build_docker_image
from patchworkdocker.importers import ImporterFactory
from patchworkdocker.modifiers import copy_file, apply_patch

_importer_factory = ImporterFactory()


class Core:
    """
    TODO
    """
    def __init__(self, import_repository_from: str, *, additional_files: Dict[str, Optional[str]]=(),
                 patches: Dict[str, str]=frozendict(), dockerfile_location: str="Dockerfile"):
        """
        TODO
        :param import_repository_from:
        :param additional_files: (added in the order given, overwrites possible)
        :param patches: (applied in the order given)
        :param dockerfile_location: location of the Dockerfile to build, relative to the root of the repository
        """
        self.import_repository_from = import_repository_from
        self.additional_files = additional_files
        self.patches = patches
        self.dockerfile_location = dockerfile_location

    def build(self, image_name: str, build_directory: str=None):
        """
        TODO
        :param image_name: image tag (can optionally include a version tag)
        :param build_directory: TODO
        :return:
        """
        repository_location = self.prepare(build_directory)
        try:
            build_docker_image(image_name, repository_location, self.dockerfile_location)
        except Exception:
            if build_directory is None:
                logger.info("Removing temp build directory")
                shutil.rmtree(repository_location)
            else:
                logger.info("Not removing build directory as directory was given by the user")
            raise

    def prepare(self, build_directory: str=None) -> str:
        """
        TODO
        """
        repository_location = _importer_factory.create(self.import_repository_from).load(
            self.import_repository_from, build_directory)
        assert os.path.isabs(repository_location)
        logger.info(f"Imported repository at {self.import_repository_from} to {repository_location}")

        for src, dest in self.additional_files.items():
            src = os.path.abspath(src)
            if dest is None:
                dest = os.path.basename(src)
            if os.path.isabs(dest):
                raise ValueError(f"Destination must be relative to the root of the context: {dest}")
            dest = os.path.join(repository_location, dest)
            os.path.exists(src), os.path.exists(dest)
            logger.info(f"{'Overwriting' if os.path.exists(dest) else 'Creating'} {dest} with {src}")
            copy_file(src, dest)

        for src, dest in self.patches.items():
            src = os.path.abspath(src)
            dest = os.path.join(repository_location, dest)
            os.path.exists(src), os.path.exists(dest)
            logger.info(f"Patching {dest} with {src}")
            apply_patch(src, dest)

        return repository_location


def get_input_files(additional_files: Dict[str, Optional[str]], patches: Dict[str, str],
                    dockerfile_location: str, build_location: str) -> Dict:
    """
    TODO
    :param additional_files:
    :param patches:
    :param dockerfile_location:
    :return:
    """
    return {
        # TODO: Remove magic strings
        "additional-files": list({os.path.abspath(src) for src in additional_files.keys()}),
        "patches": list({os.path.abspath(src) for src in patches.keys()}),
        "dockerfile": dockerfile_location,
        "build-location": build_location
    }
