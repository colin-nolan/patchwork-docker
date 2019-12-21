import os
import shutil
import unittest

import docker
from capturewrap import CaptureWrapBuilder, CaptureResult

from patchworkdocker.cli import main
from patchworkdocker.tests._common import TestWithTempFiles, EXAMPLE_BUILD_DIRECTORY, create_image_name


class CliTest(TestWithTempFiles):
    """
    TODO
    """
    def setUp(self) -> None:
        super().setUp()
        self.capture_wrap_builder = CaptureWrapBuilder(capture_stdout=True, capture_stderr=True)
        self.capture_wrap_builder.capture_exceptions = lambda e: isinstance(e, SystemExit)

    def test_no_arguments(self):
        self.capture_wrap_builder.capture_exceptions = True
        result = self._call_wrapped_main([])
        self.assertNotEqual(result.exception.code, 0)
        self.assertTrue(result.stderr.startswith("usage:"))

    def test_help(self):
        result = self._call_wrapped_main(["--help"])
        self.assertEqual(result.exception.code, 0)
        self.assertTrue(result.stdout.startswith("usage:"))

    def test_invalid_action(self):
        result = self._call_wrapped_main(["invalid"])
        self.assertNotEqual(result.exception.code, 0)

    def test_basic_prepare(self):
        result = self._call_wrapped_main(["prepare", EXAMPLE_BUILD_DIRECTORY])
        directory = result.stdout.strip()
        try:
            self.assertTrue(os.path.exists(directory))
        finally:
            shutil.rmtree(directory, ignore_errors=True)

    def test_basic_build(self):
        image_name = create_image_name()
        client = docker.from_env()
        expected_output = open(os.path.join(EXAMPLE_BUILD_DIRECTORY, "hello-world.txt"), "rb").read()
        try:
            self._call_wrapped_main(["build", EXAMPLE_BUILD_DIRECTORY, image_name])
            output = client.containers.run(image_name)
            self.assertEqual(expected_output, output)
        finally:
            client.images.remove(image_name)

    def _call_wrapped_main(self, *args, **kwargs) -> CaptureResult:
        wrapped_main = self.capture_wrap_builder.build(main)
        return wrapped_main(*args, **kwargs)


if __name__ == "__main__":
    unittest.main()
