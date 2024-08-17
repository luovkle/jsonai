from flask import Blueprint, jsonify

from app.db import db_delete, db_read, db_show
from app.exceptions import DocumentNotFoundError

bp = Blueprint("api", __name__, url_prefix="/api")


@bp.get("/<topic_id>")
def index(topic_id: str):
    try:
        content = db_read(topic_id)
    except DocumentNotFoundError as e:
        return jsonify(error=str(e)), 404
    return content


@bp.get("/<topic_id>/<item_id>")
def show(topic_id: str, item_id: str):
    try:
        content = db_show(topic_id, item_id)
    except DocumentNotFoundError as e:
        return jsonify(error=str(e)), 404
    return content


@bp.delete("/<topic_id>/<item_id>")
def delete(topic_id: str, item_id: str):
    try:
        content = db_delete(topic_id, item_id)
    except DocumentNotFoundError as e:
        return jsonify(error=str(e)), 404
    return content
