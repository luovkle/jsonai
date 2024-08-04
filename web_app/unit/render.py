#!/usr/bin/env python3

import json
import os
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

template_dir = Path.cwd() / "unit"
input_filename = "template.json"
output_filename = "config.json"
vars = [
    "APP_SECRET_KEY",
    "APP_ENV",
    "CACHE_DB_HOST",
    "CACHE_DB_PORT",
    "CACHE_DB_PASSWORD",
    "CACHE_DB_SSL",
    "DB_URI",
    "DB_NAME",
    "OPENAI_API_KEY",
    "OPENAI_MODEL",
    "OPENAI_MAX_TOKENS",
    "OPENAI_TEMPERATURE",
    "SENTRY_DSN",
    "SENTRY_TRACES_SAMPLE_RATE",
    "SENTRY_PROFILES_SAMPLE_RATE",
]

env_vars = {var: os.getenv(var) for var in vars}
environment = Environment(loader=FileSystemLoader(template_dir))
template = environment.get_template(input_filename)
content = template.render(**env_vars)

with open(template_dir / output_filename, "w") as f:
    content_json = json.loads(content)
    json.dump(content_json, f, indent=2)
