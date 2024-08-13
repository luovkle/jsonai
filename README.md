<div align="center">
  <h1>⚡️ JSONAI</h1
  <p><i>Effortlessly Create Powerful REST APIs with AI</i></p>
</div>

---

**URL**: <a href="https://jsonai.dev" target="_blank">jsonai.dev</a>

---

## Running Development Server

### Using Docker (Recommended)

#### Prerequisites

* <a href="https://www.docker.com/" target="_blank">Docker</a>
* <a href="https://docs.docker.com/compose/" target="_blank">Docker Compose</a>
* <a href="https://sentry.io/" target="_blank">Sentry Account</a>
* <a href="https://openai.com/" target="_blank">OpenAI Account</a>

#### Environment Variables

Before running the development environment, you need to configure the environment variables for the **db**, **cache_db**, and **web_app** services. These variables should be set using the **.env** files within each service's directory.

* db/.env
* cache_db/.env
* web_app/.env

In each service directory, you will find a **.env.sample** file that serves as a template with the required variables. Simply rename **.env.sample** to **.env** and assign appropriate values to each variable.

#### Running Services

```sh
docker compose -f docker-compose.dev.yml up -d --build
```

Open your browser at <a href="http://localhost" class="external-link" target="_blank">http://localhost</a>.

### Using Python (Not Recommended)

This project is designed to run in Docker; however, it is possible to run it directly using Python.

#### Prerequisites

* <a href="https://www.python.org/" target="_blank">Python 3.12</a>
* <a href="https://pipenv.pypa.io/" target="_blank">Pipenv</a>
* <a href="https://sentry.io/" target="_blank">Sentry Account</a>
* <a href="https://openai.com/" target="_blank">OpenAI Account</a>
* MongoDB Database
* Redis Database

#### Environment Variables

Ensure that you configure the environment variables in **web_app/.env**. You can find a sample configuration in **web_app/.env.sample**, which includes all the necessary environment variables required to run the server.

#### Running Server

Make sure you are in the **web_app/** directory and that all Python dependencies are installed.

```sh
pipenv install -d
```

You can start the development server with:

```sh
pipenv run dev
```

Open your browser at <a href="http://localhost:4000" class="external-link" target="_blank">http://localhost:4000</a>.

## Contributions

All contributions are welcome! If you have a great idea, feel free to open a PR.
