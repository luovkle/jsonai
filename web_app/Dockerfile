FROM python:3.12-alpine3.20
RUN pip install pipenv
WORKDIR /app
ENV PIPENV_VENV_IN_PROJECT=1
COPY ["./Pipfile", "./Pipfile.lock", "/app/"]
RUN pipenv install
COPY ["./app", "/app/app/"]
