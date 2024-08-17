import logging

import sentry_sdk
from flask import Flask, has_request_context, render_template, request
from flask.logging import default_handler

from app.cache import init_cache_db
from app.config import settings
from app.db import init_db
from app.views.api import bp as api_bp
from app.views.index import bp as index_bp


class RequestFormatter(logging.Formatter):
    def format(self, record):
        if has_request_context():
            record.url = request.url
            record.remote_addr = request.remote_addr
        else:
            record.url = None
            record.remote_addr = None

        return super().format(record)


formatter = RequestFormatter(
    "[%(asctime)s] %(remote_addr)s requested %(url)s\n"
    "%(levelname)s in %(module)s: %(message)s"
)
default_handler.setFormatter(formatter)


def page_not_found(_):
    return render_template("404.html"), 404


def internal_server_error(_):
    return render_template("500.html"), 500


def create_app():
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        traces_sample_rate=settings.SENTRY_TRACES_SAMPLE_RATE,
        profiles_sample_rate=settings.SENTRY_PROFILES_SAMPLE_RATE,
        environment=settings.APP_ENV,
    )
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY=settings.APP_SECRET_KEY,
    )
    init_db(app)
    init_cache_db(app)
    app.register_blueprint(index_bp)
    app.register_blueprint(api_bp)
    app.register_error_handler(404, page_not_found)
    app.register_error_handler(500, internal_server_error)
    return app
