#!/usr/bin/env bash

set -euf -o pipefail

# Remove old test coverage data
rm -f .coverage.*

# Run tests
PYTHONPATH=. python -m coverage run -m unittest discover -v -s patchworkdocker/tests
PYTHONPATH=. python -m coverage run patchworkdocker/cli.py -h
python -m coverage run setup.py -q install

# TODO: test ./docker-run.sh

# Generate coverage reports
coverage combine -a
coverage report
