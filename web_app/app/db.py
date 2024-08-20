from datetime import datetime
from typing import TYPE_CHECKING
from uuid import uuid4

from flask import abort, current_app, g
from pydantic import ValidationError
from pymongo import MongoClient

from app.config import settings
from app.exceptions import CouldNotSaveDocumentError, DocumentNotFoundError
from app.schemas import TopicRead, generate_model
from app.types import FoundTopics, Message

if TYPE_CHECKING:
    from flask import Flask
    from pymongo.database import Database

could_not_save_document_error_template = "Could not save the document {topic_id}"
validation_error_template = "The document {doc_id} does not have a valid schema"
topic_not_found_error_template = "Topic {topic_id} not found"
item_not_found_error_template = "Item {item_id} not found"
content_not_found_error_template = "Content of {topic_id} not found"


def _save_document(db: "Database", collection: str, topic_id: str, data: dict) -> dict:
    result = db[collection].insert_one(data)
    doc = db.public.find_one({"_id": result.inserted_id})
    if not doc:
        current_app.logger.error(
            could_not_save_document_error_template.format(topic_id=topic_id)
        )
        raise CouldNotSaveDocumentError(
            could_not_save_document_error_template.format(topic_id=topic_id)
        )
    return doc


def _get_collection_model(db: "Database", topic_id: str):
    doc = db["backup"].find_one(
        {"_id": topic_id},
        {"content": {"$slice": 1}},
    )
    if not doc:
        current_app.logger.warning(
            topic_not_found_error_template.format(topic_id=topic_id)
        )
        abort(404, description=topic_not_found_error_template.format(topic_id=topic_id))
    content = doc.get("content")
    if not content:
        current_app.logger.error(
            content_not_found_error_template.format(topic_id=topic_id)
        )
        abort(500)
    item = content[0]
    item.pop("id", None)
    return generate_model("Item", item)


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
    new_doc = {
        "_id": topic_id,
        "topic": topic,
        "content": content,
        "created_at": datetime.now(),
    }
    _save_document(db, collection="public", topic_id=topic_id, data=new_doc)
    _save_document(db, collection="backup", topic_id=topic_id, data=new_doc)
    return True


def db_save_completion(
    topic_id: str, prompt: str, completion: str, error: str | None = None
) -> bool:
    db = get_db()
    result = db.completions.insert_one(
        {
            "_id": str(uuid4()),
            "topic_id": topic_id,
            "prompt": prompt,
            "completion": completion,
            "error": error,
        }
    )
    doc = db.completions.find_one({"_id": result.inserted_id})
    if not doc:
        current_app.logger.error(
            could_not_save_document_error_template.format(topic_id=topic_id)
        )
    return True if doc else False


def db_find_topics(page: int = 1) -> FoundTopics:
    db = get_db()
    skip = (abs(page) - 1) * 20
    docs = list(db.public.find(projection=["topic"]).skip(skip).limit(20))
    topics: list[dict] = []
    for doc in docs:
        try:
            topic = TopicRead(**doc).model_dump()
        except ValidationError:
            current_app.logger.warning(
                validation_error_template.format(doc_id=doc.get("_id"))
            )
            continue
        topics.append(topic)
    preview = page - 1 if page > 1 else None  # Show 'preview' button?
    docs = list(db.public.find(projection=["topic"]).skip(skip + 20).limit(1))
    next = page + 1 if docs else None  # Show 'next' button?
    return {"topics": topics, "preview": preview, "next": next}


def db_last_topics() -> list[dict]:
    db = get_db()
    docs = list(db.public.find(projection=["topic"]).sort({"$natural": -1}).limit(10))
    topics: list[dict] = []
    for doc in docs:
        try:
            topic = TopicRead(**doc).model_dump()
        except ValidationError:
            current_app.logger.warning(
                validation_error_template.format(doc_id=doc.get("_id"))
            )
            continue
        topics.append(topic)
    return topics


def db_index(topic_id: str) -> list[dict]:
    db = get_db()
    doc = db.public.find_one({"_id": topic_id})
    if not doc:
        current_app.logger.warning(
            topic_not_found_error_template.format(topic_id=topic_id)
        )
        raise DocumentNotFoundError(
            topic_not_found_error_template.format(topic_id=topic_id)
        )
    return doc.get("content", [])


def db_show(topic_id: str, item_id: str) -> dict:
    db = get_db()
    doc = db.public.find_one({"_id": topic_id})
    if not doc:
        current_app.logger.warning(
            topic_not_found_error_template.format(topic_id=topic_id)
        )
        raise DocumentNotFoundError(
            topic_not_found_error_template.format(topic_id=topic_id)
        )
    content: list = doc.get("content")
    items = list(filter(lambda item: item.get("id") == item_id, content))
    if not items:
        current_app.logger.warning(
            item_not_found_error_template.format(item_id=item_id)
        )
        raise DocumentNotFoundError(
            item_not_found_error_template.format(item_id=item_id)
        )
    return items[0]


def db_delete(topic_id: str, item_id: str) -> Message:
    db = get_db()
    collection = db.public
    result = collection.update_one(
        {"_id": topic_id, "content.id": item_id},
        {"$pull": {"content": {"id": item_id}}},
    )
    if result.matched_count == 0 or result.modified_count == 0:
        current_app.logger.warning(
            item_not_found_error_template.format(item_id=item_id)
        )
        raise DocumentNotFoundError(
            item_not_found_error_template.format(item_id=item_id)
        )
    return {"msg": "ok"}


def db_create(topic_id: str, new_item: dict) -> dict:
    db = get_db()
    collection = db.public
    Item = _get_collection_model(db, topic_id)
    try:
        new_item_obj = Item(**new_item)
    except ValidationError as e:
        abort(422, description=e.errors())
    new_item_data = {"id": str(uuid4()), **new_item_obj.model_dump()}
    result = collection.update_one(
        {"_id": topic_id},
        {"$push": {"content": new_item_data}},
    )
    if result.matched_count == 0 or result.modified_count == 0:
        current_app.logger.warning(
            topic_not_found_error_template.format(topic_id=topic_id)
        )
        abort(404, description=topic_not_found_error_template.format(topic_id=topic_id))
    doc = collection.find_one(
        {"_id": topic_id},
        {"content": {"$elemMatch": {"id": new_item_data["id"]}}},
    )
    if not doc:
        abort(500)
    content = doc.get("content")
    return content[0]
