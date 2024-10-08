from flask import Blueprint, jsonify, request
from werkzeug.exceptions import (
    BadRequest,
    InternalServerError,
    NotFound,
    UnprocessableEntity,
)

from app.db import db_create, db_delete, db_index, db_show, db_update
from app.exceptions import DocumentNotFoundError

bp = Blueprint("api", __name__, url_prefix="/api")


@bp.errorhandler(400)
def bad_request(e: BadRequest):
    return jsonify(detail=e.description), 400


@bp.errorhandler(404)
def not_found(e: NotFound):
    return jsonify(detail=e.description), 404


@bp.errorhandler(422)
def unprocessable_entity(e: UnprocessableEntity):
    return jsonify(detail=e.description), 422


@bp.errorhandler(500)
def internal_server_error(_: InternalServerError):
    return jsonify(detail="Internal Server Error"), 500


@bp.post("/<topic_id>")
def create(topic_id: str):
    new_item = request.get_json()
    content = db_create(topic_id, new_item)
    return content, 201


@bp.get("/<topic_id>")
def index(topic_id: str):
    try:
        content = db_index(topic_id)
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


@bp.put("/<topic_id>/<item_id>")
def update(topic_id: str, item_id: str):
    new_item_data = request.get_json()
    content = db_update(topic_id, item_id, new_item_data)
    return content


@bp.delete("/<topic_id>/<item_id>")
def delete(topic_id: str, item_id: str):
    try:
        content = db_delete(topic_id, item_id)
    except DocumentNotFoundError as e:
        return jsonify(error=str(e)), 404
    return content
