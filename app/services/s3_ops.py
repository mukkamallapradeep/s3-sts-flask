import logging
from datetime import datetime, timezone
from typing import List, Dict, Optional

from botocore.exceptions import ClientError

log = logging.getLogger(__name__)

def list_buckets(s3) -> List[str]:
    try:
        resp = s3.list_buckets()
        names = [b["Name"] for b in resp.get("Buckets", [])]
        log.info(f"Buckets: {names}")
        return names
    except ClientError as e:
        log.error(f"List buckets failed: {e}")
        raise

def list_objects(s3, bucket: str, prefix: str = "") -> List[Dict]:
    try:
        resp = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)
        return resp.get("Contents", [])
    except ClientError as e:
        log.error(f"List objects failed: {e}")
        raise

def upload_fileobj(s3, bucket: str, fileobj, key: str):
    try:
        s3.upload_fileobj(fileobj, bucket, key)
        log.info(f"Uploaded to s3://{bucket}/{key}")
    except ClientError as e:
        log.error(f"Upload failed: {e}")
        raise

def download_to_bytes(s3, bucket: str, key: str) -> bytes:
    try:
        obj = s3.get_object(Bucket=bucket, Key=key)
        return obj["Body"].read()
    except ClientError as e:
        log.error(f"Download failed: {e}")
        raise

def delete_object(s3, bucket: str, key: str):
    try:
        s3.delete_object(Bucket=bucket, Key=key)
        log.info(f"Deleted s3://{bucket}/{key}")
    except ClientError as e:
        log.error(f"Delete failed: {e}")
        raise

def basic_metrics(contents: Optional[List[Dict]]) -> Dict:
    count = len(contents) if contents else 0
    last_modified = None
    if contents:
        last_modified = max(obj["LastModified"] for obj in contents)
        if isinstance(last_modified, datetime) and last_modified.tzinfo is None:
            last_modified = last_modified.replace(tzinfo=timezone.utc)
    metrics = {
        "object_count": count,
        "last_modified": last_modified.isoformat() if last_modified else None
    }
    log.info(f"Metrics: {metrics}")
    return metrics

