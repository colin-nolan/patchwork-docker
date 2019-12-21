from setuptools import setup, find_packages

from patchworkdocker.meta import VERSION, DESCRIPTION, PACKAGE_NAME, EXECUTABLE_NAME

setup(
    name=PACKAGE_NAME,
    version=VERSION,
    author="Colin Nolan",
    author_email="cn580@alumni.york.ac.uk",
    packages=find_packages(exclude=["tests"]),
    install_requires=open("requirements.txt", "r").readlines(),
    url="https://github.com/wtsi-hgi/patchwork-docker",
    license="MIT",
    description=DESCRIPTION,
    long_description=open("README.md", "r").read(),
    long_description_content_type="text/markdown",
    entry_points={
        "console_scripts": [
            f"{EXECUTABLE_NAME}={PACKAGE_NAME}.cli:entrypoint"
        ]
    },
    zip_safe=True
)
