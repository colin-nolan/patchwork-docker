#!/usr/bin/env bash
set -eu -o pipefail
shopt -s expand_aliases

WORKDIR="/root"

BASE_IMAGE="${BASE_IMAGE:-python:3.7}"
DOCKER_VERSION="${DOCKER_VERSION:-18.06.1-ce}"
userArguments="$@"

# Not assuming jq is installed on the machine
alias djq="docker run --rm -i endeveit/docker-jq jq"

# Bash implementation of `readlink` (which is not on OSX)
function readlinkx {
    echo "$(cd "$(dirname "$1")"; pwd)/$(basename "$1")"
}

# Creates mount Docker CLI setting for the given location
function createMountSetting {
    location="$1"
    if [[ "${location}" != /* ]]; then
        mountLocation="${WORKDIR}/$(echo "${location}" | sed -e 's/^[\.\/]*//g')"
    else
        mountLocation="${location}"
    fi
    echo "-v $(readlinkx ${location}):${mountLocation}"
}

>&2 echo "Building Docker image for patchworkdocker (BASE_IMAGE=${BASE_IMAGE}; DOCKER_VERSION=${DOCKER_VERSION})"
docker build -t patchworkdocker \
    --build-arg baseImage="${BASE_IMAGE}" --build-arg "dockerVersion=${DOCKER_VERSION}" . > /dev/null

>&2 echo "Determining configuration"
configuration=$(docker run --rm -i patchworkdocker --dry-run ${userArguments})
if [[ ! "${configuration}" =~ ^{.* ]]; then
    # Dry run not written JSON (probably written help)
    >&2 echo "${configuration}"
    exit 0
fi
>&2 echo "Configuration: ${configuration}"

>&2 echo "Preparing inputs"
inputLocations="$(echo ${configuration} | djq -r '[.additional_files, .patches | keys] | flatten | .[]')"
echo "${inputLocations}" | while read location; do
    if [[ ! -e "${location}" ]]; then
        >&2 echo "Input location does not exist: ${location}"
        exit 1
    fi
done
>&2 echo "Inputs: $(echo ${inputLocations} | sed 's/\n/ /g')"

>&2 echo "Preparing outputs"
buildLocation=$(echo "${configuration}" | djq -r '.build_location')
if [[ "${buildLocation}" == "null" ]]; then
    buildLocation=$(mktemp -d /tmp/patchworkdocker.XXXXXX)
    trap "rm -rf ${buildLocation}" EXIT
    userArguments="${userArguments} --build-location ${buildLocation}"
fi
outputLocations="${buildLocation}"
>&2 echo "Outputs: $(echo ${outputLocations} | sed 's/\n/ /g')"

>&2 echo "Running patchworkdocker..."
docker run --rm -i -v /var/run/docker.sock:/var/run/docker.sock:ro \
    $(echo "${outputLocations}" | while read location; do echo "$(createMountSetting ${location}) "; done) \
    $(echo "${inputLocations}" | while read location; do echo "$(createMountSetting ${location}):ro "; done) \
    patchworkdocker ${userArguments}
