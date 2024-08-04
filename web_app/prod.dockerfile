FROM node:22-alpine3.20 AS node-deps
RUN yarn global add pnpm
WORKDIR /deps/
COPY ["./package.json", "./pnpm-lock.yaml", "/deps/"]
RUN pnpm i --frozen-lockfile

FROM node-deps AS node-builder
WORKDIR /builder/
COPY --from=node-deps ["/deps/node_modules/", "/builder/node_modules/"]
COPY ["./package.json", "./tailwind.config.js", "/builder/"]
COPY ["./app/priv/static/input.css", "/builder/app/priv/static/"]
COPY ["./app/templates/", "/builder/app/templates/"]
RUN pnpm build:css

FROM python:3.12-alpine3.20 AS python-requirements
RUN pip install pipenv
WORKDIR /requirements/
COPY ["./Pipfile", "./Pipfile.lock", "/requirements/"]
RUN pipenv requirements --hash > requirements.txt

FROM python:3.12-alpine3.20 AS unit-config
RUN pip install jinja2
WORKDIR /config/
COPY ["./unit/", "/config/unit/"]
ARG APP_SECRET_KEY
ARG APP_ENV
ARG CACHE_DB_HOST
ARG CACHE_DB_PORT
ARG CACHE_DB_PASSWORD
ARG CACHE_DB_SSL
ARG DB_URI
ARG DB_NAME
ARG OPENAI_API_KEY
ARG OPENAI_MODEL
ARG OPENAI_MAX_TOKENS
ARG OPENAI_TEMPERATURE
ARG SENTRY_DSN
ARG SENTRY_TRACES_SAMPLE_RATE
ARG SENTRY_PROFILES_SAMPLE_RATE
ENV APP_SECRET_KEY=${APP_SECRET_KEY}
ENV APP_ENV=${APP_ENV}
ENV CACHE_DB_HOST=${CACHE_DB_HOST}
ENV CACHE_DB_PORT=${CACHE_DB_PORT}
ENV CACHE_DB_PASSWORD=${CACHE_DB_PASSWORD}
ENV CACHE_DB_SSL=${CACHE_DB_SSL}
ENV DB_URI=${DB_URI}
ENV DB_NAME=${DB_NAME}
ENV OPENAI_API_KEY=${OPENAI_API_KEY}
ENV OPENAI_MODEL=${OPENAI_MODEL}
ENV OPENAI_MAX_TOKENS=${OPENAI_MAX_TOKENS}
ENV OPENAI_TEMPERATURE=${OPENAI_TEMPERATURE}
ENV SENTRY_DSN=${SENTRY_DSN}
ENV SENTRY_TRACES_SAMPLE_RATE=${SENTRY_TRACES_SAMPLE_RATE}
ENV SENTRY_PROFILES_SAMPLE_RATE=${SENTRY_PROFILES_SAMPLE_RATE}
RUN python3 unit/render.py

FROM unit:1.32.1-python3.12 AS runner
COPY --from=python-requirements ["/requirements/requirements.txt", "/www/"]
RUN python3 -m pip install -r /www/requirements.txt
COPY --from=unit-config ["/config/unit/config.json", "/docker-entrypoint.d/"]
COPY ["./app/", "/www/app/"]
COPY --from=node-builder ["/builder/app/static/", "/www/app/static/"]
EXPOSE 80
