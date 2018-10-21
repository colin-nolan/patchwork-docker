# Patchwork Docker

## Purpose
To easily change an existing Docker build without having to go through the motions of cloning and modifying and 
existing build repository. For example, 


- Patch the Dockerfile or other files in the build context.
- Add/override files in the build context.
- Define a different Dockerfile.


## Installation
Prerequisites
- Docker
- Python 3.7+ (can be run entirely from Docker if you don't have Python 3.7)

The tool can be installed directly from GitHub:
```bash
pip install git+https://github.com/wtsi-hgi/patchwork-docker@master#egg=patchworkdocker
```


## Usage
