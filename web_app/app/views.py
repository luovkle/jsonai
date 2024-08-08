from uuid import uuid4

from flask import (
    Blueprint,
    abort,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from app.cache import cache_read, cache_save
from app.db import db_find_topics, db_last_topics, db_read, db_save, db_show
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
        if len(topic) >= 32:
            errors.append("Maximum length is 32 characters")
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
    last_topics = db_last_topics()
    return render_template("index.html", topics=last_topics)


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
    data = cache_read(topic_id)
    if not data:
        return redirect(url_for("views.generator"))
    if request.method == "POST":
        db_save(topic_id, data.get("topic", ""), data.get("content", []))
        session.pop("topic_id")
        return redirect(url_for("views.api_index", topic_id=topic_id))
    return render_template("publish.html", topic=data.get("topic"))


@bp.route("/find")
@bp.route("/find/<int:page>")
def find(page: int | None = None):
    if page in [0, 1]:
        return redirect(url_for("views.find"))
    page = page or 1
    found_topics = db_find_topics(page)
    if not found_topics["topics"]:
        abort(404)
    return render_template(
        "find.html",
        topics=found_topics["topics"],
        preview=found_topics["preview"],
        next=found_topics["next"],
    )


@bp.route("/api/<topic_id>")
def api_index(topic_id: str):
    try:
        content = db_read(topic_id)
    except DocumentNotFoundError as e:
        return jsonify(error=str(e)), 404
    return content


@bp.route("/api/<topic_id>/<item_id>")
def api_show(topic_id: str, item_id: str):
    try:
        content = db_show(topic_id, item_id)
    except DocumentNotFoundError as e:
        return jsonify(error=str(e)), 404
    return content
