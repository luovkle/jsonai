from uuid import uuid4

from flask import (
    Blueprint,
    abort,
    flash,
    redirect,
    render_template,
    session,
    url_for,
    request,
)

from app.cache import cache_read, cache_save
from app.db import db_read, db_save
from app.exceptions import (
    ChatGPTCompletionError,
    DocumentNotFoundError,
    JSONExtractionError,
)
from app.utils import generate_data

bp = Blueprint("views", __name__)


@bp.route("/", methods=("GET", "POST"))
def generator():
    if request.method == "POST":
        errors = []
        topic = request.form.get("topic", "")
        if not topic:
            errors.append("Invalid topic")
        if not errors:
            try:
                data = generate_data(topic)
            except (ChatGPTCompletionError, JSONExtractionError):
                abort(500)
            topic_id = str(uuid4())
            cache_save(topic_id, topic, data)
            session["topic_id"] = topic_id
            return redirect(url_for("views.preview"))
        for error in errors:
            flash(error)
    return render_template("index.html")


@bp.route("/preview")
def preview():
    topic_id = session.get("topic_id")
    if not topic_id:
        return redirect(url_for("views.generator"))
    data = cache_read(topic_id)
    if not data:
        return redirect(url_for("views.generator"))
    return render_template(
        "preview.html", topic=data.get("topic"), data=data.get("content")
    )


@bp.route("/publish", methods=("GET", "POST"))
def publish():
    topic_id = session.get("topic_id")
    if not topic_id:
        return redirect(url_for("views.generator"))
    if request.method == "POST":
        data = cache_read(topic_id)
        if not data:
            return redirect(url_for("views.generator"))
        db_save(topic_id, data.get("content", []))
        session.pop("topic_id")
        return redirect(url_for("views.api", topic_id=topic_id))
    return render_template("publish.html")


@bp.route("/api/<topic_id>")
def api(topic_id: str):
    try:
        content = db_read(topic_id)
    except DocumentNotFoundError:
        abort(404)
    return content
