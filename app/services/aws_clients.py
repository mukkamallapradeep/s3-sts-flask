import json
import logging
import time
from typing import Optional, Dict

import boto3
from botocore.exceptions import ClientError, NoCredentialsError

from app.config import Config

log = logging.getLogger(__name__)

class STSSessionCache:
    """
    Caches temporary credentials to avoid calling AssumeRole on every request.
    """
    def __init__(self, config: Config):
        self.config = config
        self._cached: Optional[Dict] = None  # {"creds": {...}, "exp": epoch}

    def get_temp_creds(self) -> Dict:
        now = int(time.time())
        # Use cached if valid for at least 2 more minutes
        if self._cached and self._cached["exp"] - now > 120:
            return self._cached["creds"]

        # 1) Read source creds from Secrets Manager using instance role (or env profile)
        src_access_key, src_secret_key = self._get_source_creds_from_secrets()

        # 2) Assume target role
        sts = boto3.client(
            "sts",
            aws_access_key_id=src_access_key,
            aws_secret_access_key=src_secret_key,
            region_name=self.config.AWS_REGION
        )
        try:
            resp = sts.assume_role(
                RoleArn=self.config.ASSUME_ROLE_ARN,
                RoleSessionName=f"s3-automation-{now}",
                DurationSeconds=3600
            )
            creds = resp["Credentials"]
            self._cached = {
                "creds": creds,
                "exp": int(creds["Expiration"].timestamp())
            }
            log.info("AssumeRole succeeded; temporary credentials cached.")
            return creds
        except ClientError as e:
            log.error(f"AssumeRole failed: {e}")
            raise

    def s3_client(self):
        tc = self.get_temp_creds()
        return boto3.client(
            "s3",
            aws_access_key_id=tc["AccessKeyId"],
            aws_secret_access_key=tc["SecretAccessKey"],
            aws_session_token=tc["SessionToken"],
            region_name=self.config.AWS_REGION
        )

    def _get_source_creds_from_secrets(self):
        """
        Reads the secret JSON: { "AWS_ACCESS_KEY_ID": "...", "AWS_SECRET_ACCESS_KEY": "..." }
        NOTE: Your compute (EC2/Jenkins node) must have permission to read this secret
              via its instance role / node role.
        """
        sm = boto3.client("secretsmanager", region_name=self.config.AWS_REGION)
        try:
            res = sm.get_secret_value(SecretId=self.config.SECRET_NAME)
            payload = res.get("SecretString")
            if not payload:
                raise ValueError("SecretString empty")
            data = json.loads(payload)
            ak = data["AWS_ACCESS_KEY_ID"]
            sk = data["AWS_SECRET_ACCESS_KEY"]
            return ak, sk
        except (ClientError, NoCredentialsError, KeyError, ValueError) as e:
            log.error(f"Failed to read secret {self.config.SECRET_NAME}: {e}")
            raise
