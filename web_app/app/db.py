from typing import TYPE_CHECKING

from flask import g
from pydantic import ValidationError
from pymongo import MongoClient

from app.config import settings
from app.exceptions import CouldNotSaveDocumentError, DocumentNotFoundError
from app.schemas import TopicRead
from app.types import FoundTopics

if TYPE_CHECKING:
    from flask import Flask
    from pymongo.database import Database


def get_db() -> "Database":
    if "db" not in g:
        g.db = MongoClient(settings.DB_URI)
    return g.db[settings.DB_NAME]


def close_db(_=None):
    db = g.pop("db", None)
    if db:
        db.close()


def init_db(app: "Flask"):
    app.teardown_appcontext(close_db)


def db_save(topic_id: str, topic: str, content: list[dict]) -> bool:
    db = get_db()
    result = db.public.insert_one({"_id": topic_id, "topic": topic, "content": content})
    doc = db.public.find_one({"_id": result.inserted_id})
    if not doc:
        raise CouldNotSaveDocumentError
    return True


def db_find_topics(page: int = 1) -> FoundTopics:
    db = get_db()
    skip = (abs(page) - 1) * 20
    docs = list(db.public.find(projection=["topic"]).skip(skip).limit(20))
    topics: list[dict] = []
    for doc in docs:
        try:
            topic = TopicRead(**doc).model_dump()
        except ValidationError:
            continue
        topics.append(topic)
    preview = page - 1 if page > 1 else None  # Show 'preview' button?
    docs = list(db.public.find(projection=["topic"]).skip(skip + 20).limit(1))
    next = page + 1 if docs else None  # Show 'next' button?
    return {"topics": topics, "preview": preview, "next": next}


def db_read(topic_id: str) -> list[dict]:
    db = get_db()
    doc = db.public.find_one({"_id": topic_id})
    if not doc:
        raise DocumentNotFoundError("Topic not found")
    return doc.get("content", [])


def db_show(topic_id: str, item_id: str) -> dict:
    db = get_db()
    doc = db.public.find_one({"_id": topic_id})
    if not doc:
        raise DocumentNotFoundError("Topic not found")
    content: list = doc.get("content")
    items = list(filter(lambda item: item.get("id") == item_id, content))
    if not items:
        raise DocumentNotFoundError("Item not found")
    return items[0]
