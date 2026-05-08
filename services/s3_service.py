import boto3
import os
import uuid
from botocore.exceptions import ClientError

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION", "ap-south-1")
S3_BUCKET = os.getenv("S3_BUCKET_NAME", "socialcardcraft-media")


def get_s3_client():
    return boto3.client(
        "s3",
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION,
    )


def upload_file_to_s3(file_bytes: bytes, filename: str, content_type: str = "image/png", folder: str = "uploads") -> str:
    s3 = get_s3_client()
    key = f"{folder}/{uuid.uuid4()}_{filename}"
    try:
        s3.put_object(
            Bucket=S3_BUCKET,
            Key=key,
            Body=file_bytes,
            ContentType=content_type,
        )
        return f"https://{S3_BUCKET}.s3.{AWS_REGION}.amazonaws.com/{key}"
    except ClientError as e:
        raise RuntimeError(f"S3 upload failed: {e}")


def upload_local_file_to_s3(local_path: str, s3_key: str, content_type: str = "application/zip") -> str:
    s3 = get_s3_client()
    try:
        s3.upload_file(local_path, S3_BUCKET, s3_key, ExtraArgs={"ContentType": content_type})
        return f"https://{S3_BUCKET}.s3.{AWS_REGION}.amazonaws.com/{s3_key}"
    except ClientError as e:
        raise RuntimeError(f"S3 upload failed: {e}")


def delete_s3_object(url: str):
    s3 = get_s3_client()
    key = url.split(f"{S3_BUCKET}.s3.{AWS_REGION}.amazonaws.com/")[-1]
    try:
        s3.delete_object(Bucket=S3_BUCKET, Key=key)
    except ClientError:
        pass
