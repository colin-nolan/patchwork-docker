import os
import shutil
import unittest
from pathlib import Path

from patchworkdocker.modifiers import copy_file, apply_patch
from patchworkdocker.tests._common import TestWithTempFiles

_RESOURCES_LOCATION = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources")

_EXAMPLE_FILE_NAME = "test-file"
_EXAMPLE_FILE_NAME_2 = "test-file-2"


class TestCopyFile(TestWithTempFiles):
    """
    Tests for `copy_file`.
    """
    def setUp(self):
        super().setUp()
        self.src_directory = self.create_temp_directory()
        self.dest_directory = self.create_temp_directory()

    def test_empty_src_to_empty_dest(self):
        copy_file(self.src_directory, self.dest_directory)
        self.assertEquals(0, len(os.listdir(self.dest_directory)))

    def test_src_to_empty_dest(self):
        Path(os.path.join(self.src_directory, _EXAMPLE_FILE_NAME)).touch()
        copy_file(self.src_directory, self.dest_directory)
        self.assertTrue(os.path.exists(os.path.join(self.dest_directory, _EXAMPLE_FILE_NAME)))
        self.assertEquals(1, len(os.listdir(self.dest_directory)))

    def test_src_to_dest(self):
        Path(os.path.join(self.dest_directory, _EXAMPLE_FILE_NAME_2)).touch()
        Path(os.path.join(self.src_directory, _EXAMPLE_FILE_NAME)).touch()
        copy_file(self.src_directory, self.dest_directory)
        self.assertTrue(os.path.exists(os.path.join(self.dest_directory, _EXAMPLE_FILE_NAME)))
        self.assertEquals(2, len(os.listdir(self.dest_directory)))

    def test_src_to_dest_with_directory_merge(self):
        Path(os.path.join(self.dest_directory, _EXAMPLE_FILE_NAME_2)).touch()
        Path(os.path.join(self.src_directory, _EXAMPLE_FILE_NAME)).touch()
        copy_file(self.src_directory, self.dest_directory)
        self.assertTrue(os.path.exists(os.path.join(self.dest_directory, _EXAMPLE_FILE_NAME)))
        self.assertEquals(2, len(os.listdir(self.dest_directory)))

    def test_src_file_to_empty_dest(self):
        file_location = os.path.join(self.src_directory, _EXAMPLE_FILE_NAME)
        Path(file_location).touch()
        copy_file(file_location, self.dest_directory)
        self.assertTrue(os.path.exists(os.path.join(self.dest_directory, _EXAMPLE_FILE_NAME)))
        self.assertEquals(1, len(os.listdir(self.dest_directory)))

    def test_src_file_to_dest_with_overwrite(self):
        file_location = os.path.join(self.src_directory, _EXAMPLE_FILE_NAME)
        print("1", file=open(os.path.join(self.dest_directory, _EXAMPLE_FILE_NAME), "w"), end="")
        print("1", file=open(os.path.join(self.dest_directory, _EXAMPLE_FILE_NAME_2), "w"), end="")
        print("2", file=open(file_location, "w"), end="")
        copy_file(file_location, self.dest_directory)
        self.assertEquals("2", open(os.path.join(self.dest_directory, _EXAMPLE_FILE_NAME), "r").read())
        self.assertEquals(2, len(os.listdir(self.dest_directory)))


class TestApplyPatch(TestWithTempFiles):
    """
    Tests for `apply_patch`.
    """
    _DOCKERFILE_NAME = "Dockerfile.example"
    _EXAMPLE_DOCKERFILE_LOCATION = os.path.join(_RESOURCES_LOCATION, _DOCKERFILE_NAME)

    def setUp(self):
        super().setUp()
        temp_directory = self.create_temp_directory()
        self._dockerfile_location = os.path.join(temp_directory, TestApplyPatch._DOCKERFILE_NAME)
        shutil.copyfile(TestApplyPatch._EXAMPLE_DOCKERFILE_LOCATION, self._dockerfile_location)

    def test_change_from(self):
        patched_content = self._apply(f"{_RESOURCES_LOCATION}/patches/from-change.patch")
        self.assertTrue(patched_content.startswith("FROM arm32v7/ubuntu:16.04"))

    def test_add_and_remove(self):
        patched_content = self._apply(f"{_RESOURCES_LOCATION}/patches/add-and-remove.patch")
        self.assertTrue("RUN /other.sh" in patched_content)
        self.assertTrue("COPY . /data" not in patched_content)

    def _apply(self, patch_location: str) -> str:
        """
        Applies the given patch to the example Docker file.
        :param patch_location: the location of the patch to apply
        :return: the contents of the example Docker file after the patch has been applied
        """
        apply_patch(patch_location, self._dockerfile_location)
        with open(self._dockerfile_location, "r") as file:
            return file.read()


if __name__ == "__main__":
    unittest.main()
