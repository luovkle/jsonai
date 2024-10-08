from typing import TYPE_CHECKING
from uuid import uuid4

import orjson
from flask import g
from redis import Redis

from app.config import settings

if TYPE_CHECKING:
    from flask import Flask


def get_cache_db() -> Redis:
    if "cache_db" not in g:
        g.cache_db = Redis(
            host=settings.CACHE_DB_HOST,
            port=settings.CACHE_DB_PORT,
            password=settings.CACHE_DB_PASSWORD,
            ssl=settings.CACHE_DB_SSL,
            decode_responses=True,
        )
    return g.cache_db


def close_cache_db(_=None):
    cache_db = g.pop("cache_db", None)
    if cache_db:
        cache_db.close()


def init_cache_db(app: "Flask"):
    app.teardown_appcontext(close_cache_db)


def cache_save(topic_id: str, topic: str, content: list[dict]) -> bool:
    cache_db = get_cache_db()
    for item in content:
        item["id"] = str(uuid4())
    data = orjson.dumps({"topic": topic, "content": content})
    cache_db.set(topic_id, value=data)
    return True


def cache_read(topic_id: str) -> dict | None:
    cache_db = get_cache_db()
    response = cache_db.get(topic_id)
    return orjson.loads(str(response)) if response else None
