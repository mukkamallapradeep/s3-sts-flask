FROM python:3.11-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# System deps (optional: ca-certificates default present)
RUN pip install --no-cache-dir --upgrade pip

# App deps
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# App
COPY app /app/app
COPY gunicorn.conf.py /app/gunicorn.conf.py

# Logs volume (mapped by Jenkins or Docker run)
VOLUME ["/app_logs"]

# Env defaults (override in Jenkins)
ENV AWS_REGION=ap-south-1 \
    SECRET_NAME=prod/jenkins/aws-keys \
    ASSUME_ROLE_ARN=arn:aws:iam::432870135296:role/S3LimitedAccessRole \
    S3_BUCKET=vms-lab-pradeep-logs \
    LOG_DIR=/app_logs \
    LOG_LEVEL=INFO

EXPOSE 8000
CMD ["gunicorn", "-c", "gunicorn.conf.py", "app:create_app()"]
