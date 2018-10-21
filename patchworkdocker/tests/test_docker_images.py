import os
import unittest
import uuid

import docker

from patchworkdocker.docker_images import build_docker_image
from patchworkdocker.tests._common import TestWithTempFiles

_BUILDING_RESOURCES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources", "building")


class TestBuildDockerImage(TestWithTempFiles):
    """
    Test `build_docker_image`.
    """
    def setUp(self):
        self._docker_client = docker.from_env()
        self._docker_image = f"{__name__}-{uuid.uuid4()}"

    def tearDown(self):
        self._docker_client.images.remove(self._docker_image)

    def test_build_docker_image(self):
        build_docker_image(self._docker_image, _BUILDING_RESOURCES, os.path.join(_BUILDING_RESOURCES, "Dockerfile"))
        contents = self._docker_client.containers.run(self._docker_image, "cat /test.txt", remove=True).decode("UTF8")
        self.assertEqual(contents, open(os.path.join(_BUILDING_RESOURCES, "hello-world.txt"), "r").read())


if __name__ == "__main__":
    unittest.main()
