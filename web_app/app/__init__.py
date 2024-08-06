import sentry_sdk
from flask import Flask, render_template

from app.cache import init_cache_db
from app.config import settings
from app.db import init_db
from app.views import bp as views_bp


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
    app.register_blueprint(views_bp)
    app.register_error_handler(404, page_not_found)
    app.register_error_handler(500, internal_server_error)
    return app
