import os
import shutil
import unittest
from abc import ABCMeta
from tempfile import mkdtemp

from typing import List


class TestWithTempFiles(unittest.TestCase, metaclass=ABCMeta):
    """
    TODO
    """
    def setUp(self):
        #
        self._paths: List[str] = []

    def tearDown(self):
        try:
            for path in self._paths:
                shutil.rmtree(path)
        except OSError:
            pass

    def create_temp_directory(self) -> str:
        """
        TODO
        :return: 
        """
        temp_directory = mkdtemp()
        self._paths.append(temp_directory)
        return temp_directory
