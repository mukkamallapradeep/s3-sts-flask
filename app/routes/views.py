import logging
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app

from app.routes.api import _s3
from app.services.s3_ops import list_objects, upload_fileobj, delete_object, basic_metrics

views = Blueprint("views", __name__)
log = logging.getLogger(__name__)

@views.get("/")
def index():
    bucket = current_app.config["S3_BUCKET"]
    prefix = request.args.get("prefix", "")
    objs = list_objects(_s3(), bucket, prefix)
    metrics = basic_metrics(objs)
    return render_template("index.html", bucket=bucket, prefix=prefix, objects=objs, metrics=metrics)

@views.post("/upload")
def upload():
    bucket = current_app.config["S3_BUCKET"]
    f = request.files.get("file")
    key = request.form.get("key") or (f"uploads/{f.filename}" if f else None)
    if not f or not key:
        flash("Select a file and key", "error")
        return redirect(url_for("views.index"))
    upload_fileobj(_s3(), bucket, f.stream, key)
    flash(f"Uploaded to s3://{bucket}/{key}", "success")
    return redirect(url_for("views.index"))

@views.post("/delete")
def delete():
    bucket = current_app.config["S3_BUCKET"]
    key = request.form.get("key")
    if not key:
        flash("Key required", "error")
        return redirect(url_for("views.index"))
    delete_object(_s3(), bucket, key)
    flash(f"Deleted s3://{bucket}/{key}", "success")
    return redirect(url_for("views.index"))
``
