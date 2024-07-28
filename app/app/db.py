from typing import TYPE_CHECKING

from flask import g
from pymongo import MongoClient

from app.config import settings
from app.exceptions import CouldNotSaveDocumentError, DocumentNotFoundError

if TYPE_CHECKING:
    from flask import Flask
    from pymongo.database import Database


def get_db() -> "Database":
    if not "db" in g:
        g.db = MongoClient(settings.DB_URI)
    return g.db[settings.DB_NAME]


def close_db(_=None):
    db = g.pop("db", None)
    if db:
        db.close()


def init_db(app: "Flask"):
    app.teardown_appcontext(close_db)


def db_save(topic_id: str, content: list[dict]) -> bool:
    db = get_db()
    result = db.public.insert_one({"_id": topic_id, "content": content})
    doc = db.public.find_one({"_id": result.inserted_id})
    if not doc:
        raise CouldNotSaveDocumentError
    return True


def db_read(topic_id: str) -> list[dict]:
    db = get_db()
    doc = db.public.find_one({"_id": topic_id})
    if not doc:
        raise DocumentNotFoundError
    return doc.get("content", [])
