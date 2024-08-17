#!/usr/bin/env sh

if [ -f ./web_app/env/prod.env ]; then
  export $(grep -v '^#' ./web_app/env/prod.env | xargs)
fi

docker compose -f docker-compose.prod.yml up -d --build
