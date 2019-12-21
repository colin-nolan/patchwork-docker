import os
from abc import ABCMeta
from unittest import TestCase
from temphelpers import TempManager
from uuid import uuid4
from patchworkdocker.meta import PACKAGE_NAME

EXAMPLE_GIT_REPOSITORY = "https://github.com/colin-nolan/test-repository.git"
EXAMPLE_BUILD_DIRECTORY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources", "building")


class TestWithTempFiles(TestCase, metaclass=ABCMeta):
    """
    Base class for tests that use temp files.
    """
    def setUp(self):
        self.temp_manager = TempManager()

    def tearDown(self):
        self.temp_manager.tear_down()


def create_image_name():
    """
    TODO
    :return:
    """
    return f"{PACKAGE_NAME}-test:{str(uuid4())}"
