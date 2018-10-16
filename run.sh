#!/usr/bin/env bash

set -eu -o pipefail

scriptDirectory="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "${scriptDirectory}"

docker build -t patchworkdocker .

docker run --rm -it patchworkdocker inputfiles "$@"
