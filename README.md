# s3-sts-flask

# S3 STS Automation (Flask)

Flask web + REST API that:
- Reads source AWS keys from **AWS Secrets Manager**
- Uses **STS AssumeRole** to get short-lived creds
- Performs S3 operations (list, upload, download, delete)
- Logs to `/app_logs/app.log`

## Prereqs

- The **EC2/Jenkins node** running this container must have an **IAM instance role** with:
  - `secretsmanager:GetSecretValue` on the secret `prod/jenkins/aws-keys` (ap-south-1)
- The **assumed role** must permit S3 access to your target bucket.

## Env Vars

- `AWS_REGION` (default: ap-south-1)
- `SECRET_NAME` (default: prod/jenkins/aws-keys)
- `ASSUME_ROLE_ARN` (your role ARN)
- `S3_BUCKET` (your bucket)
- `LOG_DIR` (default: /app_logs)
- `LOG_LEVEL` (default: INFO)

## Local (without Docker)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export AWS_REGION=ap-south-1
export SECRET_NAME=prod/jenkins/aws-keys
export ASSUME_ROLE_ARN=arn:aws:iam::<ACCOUNT_ID>:role/S3LimitedAccessRole
export S3_BUCKET=vms-lab-pradeep-logs
# Ensure your local AWS creds can read the secret
export FLASK_APP=app
flask run --port 8000
