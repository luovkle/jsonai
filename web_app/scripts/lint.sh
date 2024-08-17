#!/usr/bin/env sh

set -x

mypy .
black --check .
isort --check-only .
flake8 .
docformatter --check .
djlint --profile=jinja --check --indent 2 --preserve-blank-lines \
  --close-void-tags app/templates/
djlint --lint app/templates/
