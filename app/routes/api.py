import io
import logging
from flask import Blueprint, jsonify, request, send_file, current_app

from app.services.aws_clients import AWSClients
from app.services.s3_ops import (
    list_buckets, list_objects, upload_fileobj, download_to_bytes, delete_object, basic_metrics
)

api = Blueprint("api", __name__)
log = logging.getLogger(__name__)

def _s3():
    aws = AWSClients()
    return aws.session().client("s3")

@api.get("/healthz")
def healthz():
    return {"status": "ok"}, 200

@api.get("/buckets")
def api_buckets():
    names = list_buckets(_s3())
    return jsonify({"buckets": names})

@api.get("/objects")
def api_objects():
    bucket = current_app.config["S3_BUCKET"]
    prefix = request.args.get("prefix", "")
    contents = list_objects(_s3(), bucket, prefix)
    return jsonify({
        "bucket": bucket,
        "prefix": prefix,
        "objects": [
            {
                "key": c["Key"],
                "size": c["Size"],
                "last_modified": c["LastModified"].isoformat()
            } for c in contents
        ],
        "metrics": basic_metrics(contents)
    })

@api.post("/upload")
def api_upload():
    bucket = current_app.config["S3_BUCKET"]
    if "file" not in request.files:
        return {"error": "file form field is required"}, 400
    file = request.files["file"]
    key = f"uploads/{file.filename}"
    if not file or file.filename == "":
        return {"error": "empty file"}, 400
    upload_fileobj(_s3(), bucket, file.stream, key)
    return {"message": "uploaded", "bucket": bucket, "key": key}, 201

@api.get("/download")
def api_download():
    bucket = current_app.config["S3_BUCKET"]
    key = request.args.get("key")
    if not key:
        return {"error": "key is required"}, 400
    data = download_to_bytes(_s3(), bucket, key)
    return send_file(
        io.BytesIO(data),
        mimetype="application/octet-stream",
        as_attachment=True,
        download_name=key.split("/")[-1]
    )

@api.delete("/object")
def api_delete():
    bucket = current_app.config["S3_BUCKET"]
    key = request.args.get("key")
    if not key:
        return {"error": "key is required"}, 400
    delete_object(_s3(), bucket, key)
    return {"message": "deleted", "bucket": bucket, "key": key}, 200
