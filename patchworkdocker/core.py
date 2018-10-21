import os
import shutil
from typing import Dict, Optional

from frozendict import frozendict
from logzero import logger

from patchworkdocker.docker_images import build_docker_image
from patchworkdocker.importers import ImporterFactory
from patchworkdocker.modifiers import copy_file, apply_patch, change_base_image

_importer_factory = ImporterFactory()


class PatchworkDocker:
    """
    Builds patchwork Docker images.
    """
    @property
    def dockerfile_location(self) -> str:
        return self._dockerfile_location

    @dockerfile_location.setter
    def dockerfile_location(self, location: str):
        if os.path.isabs(location):
            raise ValueError(f"Dockerfile location must be relative to the context root: {location}")
        self._dockerfile_location = location

    def __init__(self, import_repository_from: str, *, additional_files: Dict[str, Optional[str]]=(),
                 patches: Dict[str, str]=frozendict(), dockerfile_location: str="Dockerfile", base_image: str=None):
        """
        Constructor.
        :param import_repository_from: where to import the starting materials for the image from
        :param additional_files: files to add to the build context, where the key is the location on the host and the
        value (if given) is the relative location in the build context (added in the order given, overwrites possible)
        :param patches: patches to apply to files in the build context, where the key is the location of the patch file
        and the value is the location of the file to apply it to, relative to the build context root (applied in the
        order given)
        :param dockerfile_location: location of the Dockerfile to build, relative to the root of the repository
        :param base_image: Docker base image to change to
        """
        self._dockerfile_location = None
        self.import_repository_from = import_repository_from
        self.additional_files = additional_files
        self.patches = patches
        self.dockerfile_location = dockerfile_location
        self.base_image = base_image

    def build(self, image_name: str, build_directory: str=None):
        """
        Builds the patchworked Docker image.
        :param image_name: image tag (can optionally include a version tag)
        :param build_directory: directory to build in
        """
        repository_location = self.prepare(build_directory)
        dockerfile_location = os.path.join(repository_location, self.dockerfile_location)
        try:
            build_docker_image(image_name, repository_location, dockerfile_location)
        finally:
            if build_directory is None:
                logger.info(f"Removing temp build directory: {repository_location}")
                shutil.rmtree(repository_location)
            else:
                logger.info(f"Not removing build directory as directory was given by the user: {repository_location}")

    def prepare(self, build_directory: str=None) -> str:
        """
        Prepare a directory with the patched build materials.
        :param build_directory: the directory to load the patched build context in
        :return: the location of the build directory
        """
        if build_directory is not None:
            build_directory = os.path.abspath(build_directory)
            if len(os.listdir(path=build_directory)) > 0:
                raise ValueError(f"Build directory {build_directory} is not empty")

        repository_location = _importer_factory.create(self.import_repository_from).load(
            self.import_repository_from, build_directory)
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

        if self.base_image is not None:
            logger.info(f"Setting base image to {self.base_image}")
            dockerfile_location = os.path.join(repository_location, self.dockerfile_location)
            change_base_image(dockerfile_location, self.base_image)

        return repository_location
