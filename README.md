# Patchwork Docker

## Purpose
To allow an existing Docker build to be easily changed, without having to go through the motions of cloning and 
modifying and an existing build repository. 


## Features
All with a single command, the tool can:
- Build images from a different base image.
- Add/override files in the build context.
- Apply patches to the Dockerfile or other files in the build context.
- Define a different Dockerfile.


## Use Cases
A few basic use cases:
- To change a base image from `debian:stretch` to `python:3.7-stretch` so as to get the latest version of Python in the 
  image with no hassle:
  ```bash
  ./docker-run.sh build example:1.0.0 https://github.com/example/docker-example.git \
      --base-image python:3.7-stretch
  ```
- Add an alternate Dockerfile to a pre-existing context:
  ```bash
  ./docker-run.sh build example:1.0.0 https://github.com/example/docker-example.git \
      --additional-file Dockerfile:Dockerfile.example \
      --dockerfile Dockerfile.example
  ```
- Change the URL of a piece of software that gets installed into a Docker image:
  ```bash
  ./docker-run.sh build example:1.0.0 https://github.com/docker-library/python.git \
      --dockerfile 3.7/stretch/Dockerfile \
      --patch change-install-url.patch:Dockerfile
  ```

Raspberry Pi users may find this tool particularly useful as, outside the official images, there is often need to 
change image build in order to get them to work on the non-standard rpi architectures. 


## Installation
Prerequisites
- Docker
- Python 3.7+ (optional, as can be run entirely from Docker if you don't have Python 3.7)

The tool can be installed directly from GitHub:
```bash
pip install git+https://github.com/wtsi-hgi/patchwork-docker@master#egg=patchworkdocker
```


## Usage
Up-to-date usage information can be seen with:
```bash
./docker-run.sh --help
./docker-run.sh build --help
```
