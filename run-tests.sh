#!/usr/bin/env bash
set -euf -o pipefail

# Remove old test coverage data
python -m coverage erase

# Run tests
PYTHONPATH=. python -m coverage run -m unittest discover -v -s patchworkdocker/tests
PYTHONPATH=. python -m coverage run patchworkdocker/cli.py -h
python -m coverage run setup.py -q install

# Generate coverage reports
python -m coverage combine -a
python -m coverage report
python -m coverage xml
