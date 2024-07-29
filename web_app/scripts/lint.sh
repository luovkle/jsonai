#!/usr/bin/env sh

set -x

mypy .
black --check .
isort --check-only .
flake8 .
docformatter --check .
