import os
import unittest
import uuid

import docker

from patchworkdocker.docker_images import build_docker_image
from patchworkdocker.tests._common import TestWithTempFiles, EXAMPLE_BUILD_DIRECTORY


class TestBuildDockerImage(TestWithTempFiles):
    """
    Test `build_docker_image`.
    """
    def setUp(self):
        super().setUp()
        self._docker_client = docker.from_env()
        self._docker_image = f"{__name__}-{uuid.uuid4()}"

    def tearDown(self):
        super().tearDown()
        self._docker_client.images.remove(self._docker_image)

    def test_build_docker_image(self):
        build_docker_image(self._docker_image, EXAMPLE_BUILD_DIRECTORY, os.path.join(EXAMPLE_BUILD_DIRECTORY, "Dockerfile"))
        contents = self._docker_client.containers.run(self._docker_image, "cat /test.txt", remove=True).decode("UTF8")
        self.assertEqual(contents, open(os.path.join(EXAMPLE_BUILD_DIRECTORY, "hello-world.txt"), "r").read())


if __name__ == "__main__":
    unittest.main()
