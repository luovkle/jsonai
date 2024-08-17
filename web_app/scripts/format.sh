#!/usr/bin/env sh

set -e
set -x

autoflake --in-place .
black .
isort .
docformatter --in-place .
djlint --profile=jinja --reformat --quiet --indent 2 --preserve-blank-lines \
  --close-void-tags app/templates/
