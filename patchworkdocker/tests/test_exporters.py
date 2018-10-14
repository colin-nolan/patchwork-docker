import contextlib
import os
import unittest
from abc import ABCMeta, abstractmethod
from pathlib import Path

from patchworkdocker.exporters import Exporter, DirectoryExporter
from patchworkdocker.tests._common import TestWithTempFiles

_INVALID_DIRECTORY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "not/valid")


class _TestExporter(TestWithTempFiles, metaclass=ABCMeta):
    """
    TODO
    """
    @property
    @abstractmethod
    def exporter(self) -> Exporter:
        """
        Gets the exporter that is being tested.
        :return: the exporter being tested
        """

    def setUp(self):
        super().setUp()
        with contextlib.suppress(FileNotFoundError):
            os.rmdir(_INVALID_DIRECTORY)

    def tearDown(self):
        self.assertFalse(os.path.exists(_INVALID_DIRECTORY))
        super().tearDown()

    def test_export_invalid_src(self):
        self.assertRaises(FileNotFoundError, self.exporter.export, _INVALID_DIRECTORY, self.create_temp_directory())


class TestDirectoryExporter(_TestExporter):
    """
    Tests for `DirectoryExporter`.
    """
    @property
    def exporter(self) -> Exporter:
        return DirectoryExporter()

    def test_export_to_valid_dest(self):
        src = self.create_temp_directory()
        file_location = os.path.join(src, "test")
        Path(file_location).touch()

        dest_parent = self.create_temp_directory()
        dest = os.path.join(dest_parent, "export")

        self.exporter.export(src, dest)
        self.assertTrue(os.path.exists(dest))
        self.assertEquals([os.path.basename(file_location)], os.listdir(dest))


del _TestExporter

if __name__ == "__main__":
    unittest.main()
