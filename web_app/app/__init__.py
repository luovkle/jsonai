import sentry_sdk
from flask import Flask

from app.cache import init_cache_db
from app.config import settings
from app.db import init_db
from app.views import bp as views_bp


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
    app.register_blueprint(views_bp)
    init_db(app)
    init_cache_db(app)
    return app
