import os
import unittest
from abc import abstractmethod
from pathlib import Path
from typing import TypeVar, Generic, Optional

from patchworkdocker.importers import GitImporter, Importer, FileSystemImporter
from patchworkdocker.tests._common import TestWithTempFiles

_EXAMPLE_GIT_REPOSITORY = "https://github.com/colin-nolan/test-repository.git"

ImporterType = TypeVar("ImporterType", bound=Importer)


class _TestImporter(Generic[ImporterType], TestWithTempFiles):
    """
    Tests for `ImporterType`.
    """
    @property
    @abstractmethod
    def importer(self) -> ImporterType:
        """
        Gets an instance of the importer under test.
        :return: the importer to test
        """

    def setUp(self):
        super().setUp()
        self._importer: Optional[Importer] = None

    def load(self, origin: str) -> str:
        """
        Uses the importer under test and calls loads with the given origin. The returned path is removed on tear down.
        :param origin: the origin to load from
        :return: the path of where the import has been loaded to
        """
        path = self.importer.load(origin)
        self._paths.append(path)
        return path


class TestGitImporter(_TestImporter[GitImporter]):
    """
    Tests for `GitImporter`.
    """
    @property
    def importer(self) -> ImporterType:
        if self._importer is None:
            self._importer = GitImporter()
        return self._importer

    def test_load(self):
        path = self.load(_EXAMPLE_GIT_REPOSITORY)
        self.assertTrue(os.path.exists(os.path.join(path, "a/d.txt")))

    def test_load_commit(self):
        path = self.load(f"{_EXAMPLE_GIT_REPOSITORY}#e22fcb940d5356f8dc57fa99d7a6cb4ecdc04b66")
        self.assertTrue(os.path.exists(os.path.join(path, "b.txt")))

    def test_load_branch(self):
        path = self.load(f"{_EXAMPLE_GIT_REPOSITORY}#develop")
        self.assertTrue(os.path.exists(os.path.join(path, "develop.txt")))

    def test_load_tag(self):
        path = self.load(f"{_EXAMPLE_GIT_REPOSITORY}#1.0")
        self.assertTrue(os.path.exists(os.path.join(path, "b.txt")))


class TestFileSystemImporter(_TestImporter[GitImporter]):
    """
    Tests for `FileSystemImporter`.
    """
    _EXAMPLE_FILE = "test.txt"

    @property
    def importer(self) -> ImporterType:
        if self._importer is None:
            self._importer = FileSystemImporter()
        return self._importer

    def setUp(self):
        super().setUp()
        self.test_directory = self.create_temp_directory()
        Path(os.path.join(self.test_directory, TestFileSystemImporter._EXAMPLE_FILE)).touch()

    def test_load(self):
        path = self.load(self.test_directory)
        self.assertTrue(os.path.exists(os.path.join(path, TestFileSystemImporter._EXAMPLE_FILE)))


if __name__ == "__main__":
    unittest.main()
