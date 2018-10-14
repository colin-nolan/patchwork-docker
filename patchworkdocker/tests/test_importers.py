import os
import unittest
from abc import abstractmethod
from pathlib import Path

from typing import TypeVar, Generic, Optional

from patchworkdocker.importers import GitImporter, Importer, FileSystemImporter
from patchworkdocker.tests._common import TestWithTempFiles

_EXAMPLE_GIT_REPOSITORY = "https://github.com/wtsi-npg/baton.git"
_EXAMPLE_FILE = "ChangeLog"

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

    def load(self, origin: str):
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
        self.assertTrue(os.path.exists(os.path.join(path, _EXAMPLE_FILE)))

    def test_load_commit(self):
        path = self.load(f"{_EXAMPLE_GIT_REPOSITORY}#557f5f9a90cdc43a8e54ab1d2a1f91341c93f547")
        self.assertFalse(os.path.exists(os.path.join(path, _EXAMPLE_FILE)))

    def test_load_branch(self):
        path = self.load(f"{_EXAMPLE_GIT_REPOSITORY}#release-0.17.0")
        with open(os.path.join(path, _EXAMPLE_FILE), "r") as file:
            content = file.read()
        # FIXME: Test will pass even if v10
        self.assertIn("[0.17.0]", content)

    def test_load_tag(self):
        path = self.load(f"{_EXAMPLE_GIT_REPOSITORY}#0.17.1")
        with open(os.path.join(path, _EXAMPLE_FILE), "r") as file:
            content = file.read()
        self.assertIn("[0.17.1]", content)


class TestFileSystemImporter(_TestImporter[GitImporter]):
    """
    Tests for `FileSystemImporter`.
    """
    @property
    def importer(self) -> ImporterType:
        if self._importer is None:
            self._importer = FileSystemImporter()
        return self._importer

    def setUp(self):
        super().setUp()
        self.test_directory = self.create_temp_directory()
        Path(os.path.join(self.test_directory, _EXAMPLE_FILE)).touch()

    def test_load(self):
        path = self.load(self.test_directory)
        self.assertTrue(os.path.exists(os.path.join(path, _EXAMPLE_FILE)))


if __name__ == "__main__":
    unittest.main()
