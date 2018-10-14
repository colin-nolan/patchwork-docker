import os
import unittest
from pathlib import Path

import re

from patchworkdocker.modifiers import copy_additional_files, replace_in_string
from patchworkdocker.tests._common import TestWithTempFiles


_EXAMPLE_DOCKERFILE_LOCATION = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_resources/Dockerfile.example")

_EXAMPLE_FILE_NAME = "test-file"
_EXAMPLE_FILE_NAME_2 = "test-file-2"
_EXAMPLE_STRING = "test"


class TestCopyAdditionalFiles(TestWithTempFiles):
    """
    Tests for `copy_additional_files`.
    """
    def setUp(self):
        super().setUp()
        self.src_directory = self.create_temp_directory()
        self.dest_directory = self.create_temp_directory()

    def test_empty_src_to_empty_dest(self):
        copy_additional_files([self.src_directory], self.dest_directory)
        self.assertEquals(0, len(os.listdir(self.dest_directory)))

    def test_single_src_to_empty_dest(self):
        Path(os.path.join(self.src_directory, _EXAMPLE_FILE_NAME)).touch()
        copy_additional_files([self.src_directory], self.dest_directory)
        self.assertTrue(os.path.exists(os.path.join(self.dest_directory, _EXAMPLE_FILE_NAME)))
        self.assertEquals(1, len(os.listdir(self.dest_directory)))

    def test_single_src_to_dest(self):
        Path(os.path.join(self.dest_directory, _EXAMPLE_FILE_NAME_2)).touch()
        Path(os.path.join(self.src_directory, _EXAMPLE_FILE_NAME)).touch()
        copy_additional_files([self.src_directory], self.dest_directory)
        self.assertTrue(os.path.exists(os.path.join(self.dest_directory, _EXAMPLE_FILE_NAME)))
        self.assertEquals(2, len(os.listdir(self.dest_directory)))

    def test_single_src_to_dest_with_directory_merge(self):
        Path(os.path.join(self.dest_directory, _EXAMPLE_FILE_NAME_2)).touch()
        Path(os.path.join(self.src_directory, _EXAMPLE_FILE_NAME)).touch()
        copy_additional_files([self.src_directory], self.dest_directory)
        self.assertTrue(os.path.exists(os.path.join(self.dest_directory, _EXAMPLE_FILE_NAME)))
        self.assertEquals(2, len(os.listdir(self.dest_directory)))

    def test_single_src_file_to_empty_dest(self):
        file_location = os.path.join(self.src_directory, _EXAMPLE_FILE_NAME)
        Path(file_location).touch()
        copy_additional_files([file_location], self.dest_directory)
        self.assertTrue(os.path.exists(os.path.join(self.dest_directory, _EXAMPLE_FILE_NAME)))
        self.assertEquals(1, len(os.listdir(self.dest_directory)))

    def test_single_src_file_to_dest_with_overwrite(self):
        file_location = os.path.join(self.src_directory, _EXAMPLE_FILE_NAME)
        print("1", file=open(os.path.join(self.dest_directory, _EXAMPLE_FILE_NAME), "w"), end="")
        print("1", file=open(os.path.join(self.dest_directory, _EXAMPLE_FILE_NAME_2), "w"), end="")
        print("2", file=open(file_location, "w"), end="")
        copy_additional_files([file_location], self.dest_directory)
        self.assertEquals("2", open(os.path.join(self.dest_directory, _EXAMPLE_FILE_NAME), "r").read())
        self.assertEquals(2, len(os.listdir(self.dest_directory)))

    def test_multiple_src_to_empty_dest(self):
        other_source_directory = self.create_temp_directory()
        Path(os.path.join(self.src_directory, _EXAMPLE_FILE_NAME)).touch()
        Path(os.path.join(other_source_directory, _EXAMPLE_FILE_NAME_2)).touch()
        copy_additional_files([self.src_directory, other_source_directory], self.dest_directory)
        self.assertTrue(os.path.exists(os.path.join(self.dest_directory, _EXAMPLE_FILE_NAME)))
        self.assertTrue(os.path.exists(os.path.join(self.dest_directory, _EXAMPLE_FILE_NAME_2)))
        self.assertEquals(2, len(os.listdir(self.dest_directory)))

    def test_multiple_src_with_same_name_to_empty_dest(self):
        other_source_directory = self.create_temp_directory()
        print("1", file=open(os.path.join(self.src_directory, _EXAMPLE_FILE_NAME), "w"), end="")
        print("2", file=open(os.path.join(other_source_directory, _EXAMPLE_FILE_NAME), "w"), end="")
        copy_additional_files([self.src_directory, other_source_directory], self.dest_directory)
        self.assertEquals("2", open(os.path.join(self.dest_directory, _EXAMPLE_FILE_NAME), "r").read())
        self.assertEquals(1, len(os.listdir(self.dest_directory)))


class TestReplaceInString(TestWithTempFiles):
    """
    Tests for `replace_in_string`.
    """
    _EXAMPLE_DOCKERFILE: str

    @classmethod
    def setUpClass(cls):
        TestReplaceInString._EXAMPLE_DOCKERFILE = open(_EXAMPLE_DOCKERFILE_LOCATION, "r").read()

    def test_replace_no_pattern_replacements(self):
        self.assertEquals(TestReplaceInString._EXAMPLE_DOCKERFILE,
                          replace_in_string([], TestReplaceInString._EXAMPLE_DOCKERFILE))

    def test_replace_with_no_matching_patterns(self):
        pattern = "not_matched"
        self.assertEquals(
            TestReplaceInString._EXAMPLE_DOCKERFILE, replace_in_string([(pattern, _EXAMPLE_STRING)], TestReplaceInString._EXAMPLE_DOCKERFILE))

    def test_replace_part_of_line(self):
        pattern = "FROM"
        expected = TestReplaceInString._EXAMPLE_DOCKERFILE.replace(pattern, _EXAMPLE_STRING)
        self.assertEquals(
            expected, replace_in_string([(pattern, _EXAMPLE_STRING)], TestReplaceInString._EXAMPLE_DOCKERFILE))

    def test_replace_whole_line(self):
        pattern = "FROM.*"
        expected = "\n%s" % "\n".join(TestReplaceInString._EXAMPLE_DOCKERFILE.split("\n")[1:])
        self.assertEquals(expected, replace_in_string([(pattern, "")], TestReplaceInString._EXAMPLE_DOCKERFILE))

    def test_replace_over_multiple_lines(self):
        pattern = "RUN(.|\n|\r)*setup-2.sh"
        expected = re.sub(pattern, _EXAMPLE_STRING, TestReplaceInString._EXAMPLE_DOCKERFILE)
        assert "setup-1.sh" not in expected and "setup-2.sh" not in expected
        self.assertEquals(
            expected, replace_in_string([(pattern, _EXAMPLE_STRING)], TestReplaceInString._EXAMPLE_DOCKERFILE))

    def test_replace_only_matches_first(self):
        pattern = ".*\./setup.*"
        expected = TestReplaceInString._EXAMPLE_DOCKERFILE.replace("RUN ./setup-1.sh \\", _EXAMPLE_STRING, 1)
        self.assertEquals(
            expected, replace_in_string([(pattern, _EXAMPLE_STRING)], TestReplaceInString._EXAMPLE_DOCKERFILE))



























































if __name__ == "__main__":
    unittest.main()
