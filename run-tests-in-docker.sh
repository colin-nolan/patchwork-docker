#!/usr/bin/env bash

set -euf -o pipefail

scriptDirectory="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Note: `mktemp` creates temps in directory that cannot be mounted by default on Mac
tempDirectory="/tmp/patchwork-docker-${RANDOM}"
trap "echo ${tempDirectory} && rm -rf ${tempDirectory}" INT TERM HUP EXIT
mkdir "${tempDirectory}"

docker build -t patchworkdocker -f Dockerfile .
docker build -t patchworkdocker-tests -f Dockerfile.test .
docker run --rm -it -v "${scriptDirectory}":/patchwork-docker \
                    -v /var/run/docker.sock:/var/run/docker.sock:ro \
                    -v "${tempDirectory}:${tempDirectory}" \
                    -e TMPDIR="${tempDirectory}" \
                    --entrypoint=bash \
    patchworkdocker-tests /patchwork-docker/run-tests.sh
