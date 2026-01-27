import os

class Config:
    # Core AWS config
    AWS_REGION = os.getenv("AWS_REGION", "ap-south-1")
    SECRET_NAME = os.getenv("SECRET_NAME", "prod/jenkins/aws-keys")
    ASSUME_ROLE_ARN = os.getenv("ASSUME_ROLE_ARN", "arn:aws:iam::432870135296:role/S3LimitedAccessRole")

    # Target bucket
    S3_BUCKET = os.getenv("S3_BUCKET", "vms-lab-pradeep-logs")

    # Optional toggles
    DELETE_AFTER = os.getenv("DELETE_AFTER", "false").lower() == "true"

    # Logging
    LOG_DIR = os.getenv("LOG_DIR", "/app_logs")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    # Flask secret
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "change-me")

    # Upload handling
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_UPLOAD_MB", "25")) * 1024 * 1024
