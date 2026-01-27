import os
import json
import logging
import boto3
from botocore.exceptions import ClientError, NoCredentialsError

log = logging.getLogger(__name__)

class AWSConfig:
    AWS_REGION = os.getenv("AWS_REGION", "ap-south-1")
    SECRET_NAME = os.getenv("SECRET_NAME")
    ASSUME_ROLE_ARN = os.getenv("ASSUME_ROLE_ARN")

class AWSClients:
    def __init__(self, config=AWSConfig()):
        self.config = config
        self._session = None

    def base_session(self):
        # Uses AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY / AWS_SESSION_TOKEN
        # which Jenkins injected into Docker
        return boto3.Session(region_name=self.config.AWS_REGION)

    def session(self):
        if self._session:
            return self._session

        base = self.base_session()

        # Optional: Assume Role inside the container
        if self.config.ASSUME_ROLE_ARN:
            try:
                sts = base.client("sts")
                resp = sts.assume_role(
                    RoleArn=self.config.ASSUME_ROLE_ARN,
                    RoleSessionName="webapp-session"
                )
                creds = resp["Credentials"]
                self._session = boto3.Session(
                    aws_access_key_id=creds["AccessKeyId"],
                    aws_secret_access_key=creds["SecretAccessKey"],
                    aws_session_token=creds["SessionToken"],
                    region_name=self.config.AWS_REGION,
                )
                return self._session
            except ClientError as e:
                log.error(f"AssumeRole failed: {e}")
                raise
        else:
            self._session = base
            return self._session

    def secrets_client(self):
        return self.session().client("secretsmanager")

    def get_secret_value(self):
        sm = self.secrets_client()
        try:
            res = sm.get_secret_value(SecretId=self.config.SECRET_NAME)
            return res.get("SecretString") or res.get("SecretBinary")
        except NoCredentialsError:
            log.error("❌ No AWS credentials inside the Docker container.")
            raise
        except ClientError as e:
            log.error(f"❌ Failed to read secret: {e}")
            raise
