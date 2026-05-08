"""
Upload service — tries S3 first, falls back to local /uploads directory.
"""
import os
import uuid
from pathlib import Path

UPLOADS_DIR = Path("uploads")


def upload_file(file_bytes: bytes, filename: str, content_type: str = "image/png", folder: str = "uploads") -> str:
    """Upload to S3 if configured, otherwise save locally and return a local URL."""
    try:
        from services.s3_service import upload_file_to_s3
        aws_key = os.getenv("AWS_ACCESS_KEY_ID", "")
        aws_secret = os.getenv("AWS_SECRET_ACCESS_KEY", "")
        if aws_key and not aws_key.startswith("REPLACE") and not aws_key.startswith("your"):
            return upload_file_to_s3(file_bytes, filename, content_type, folder)
    except Exception:
        pass

    # Local fallback
    local_dir = UPLOADS_DIR / folder
    local_dir.mkdir(parents=True, exist_ok=True)
    safe_name = f"{uuid.uuid4().hex}_{Path(filename).name}"
    file_path = local_dir / safe_name
    file_path.write_bytes(file_bytes)
    return f"/uploads/{folder}/{safe_name}"
