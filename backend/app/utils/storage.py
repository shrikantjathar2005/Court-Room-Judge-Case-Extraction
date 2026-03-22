"""File storage utilities supporting local and S3 storage."""

import os
import uuid
import aiofiles
from pathlib import Path
from typing import Optional
from fastapi import UploadFile
from app.config import settings


async def save_upload_file(
    upload_file: UploadFile,
    subdirectory: str = "documents",
) -> dict:
    """
    Save uploaded file to local storage or S3.
    Returns dict with file_path, file_size, file_type.
    """
    # Generate unique filename
    file_ext = os.path.splitext(upload_file.filename)[1].lower()
    unique_filename = f"{uuid.uuid4()}{file_ext}"

    if settings.STORAGE_TYPE == "s3":
        return await _save_to_s3(upload_file, unique_filename, subdirectory)
    else:
        return await _save_to_local(upload_file, unique_filename, subdirectory)


async def _save_to_local(
    upload_file: UploadFile, filename: str, subdirectory: str
) -> dict:
    """Save file to local filesystem."""
    upload_dir = Path(settings.UPLOAD_DIR) / subdirectory
    upload_dir.mkdir(parents=True, exist_ok=True)

    file_path = upload_dir / filename

    # Read and write file content
    content = await upload_file.read()
    async with aiofiles.open(file_path, "wb") as f:
        await f.write(content)

    return {
        "file_path": str(file_path),
        "file_size": len(content),
        "file_type": upload_file.content_type,
    }


async def _save_to_s3(
    upload_file: UploadFile, filename: str, subdirectory: str
) -> dict:
    """Save file to AWS S3."""
    import boto3

    s3_client = boto3.client(
        "s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION,
    )

    content = await upload_file.read()
    s3_key = f"{subdirectory}/{filename}"

    s3_client.put_object(
        Bucket=settings.AWS_S3_BUCKET,
        Key=s3_key,
        Body=content,
        ContentType=upload_file.content_type,
    )

    return {
        "file_path": f"s3://{settings.AWS_S3_BUCKET}/{s3_key}",
        "file_size": len(content),
        "file_type": upload_file.content_type,
    }


def get_file_path(stored_path: str) -> Optional[str]:
    """Get the actual file path for serving."""
    if stored_path.startswith("s3://"):
        # For S3, generate a presigned URL
        import boto3

        s3_client = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION,
        )
        bucket = stored_path.split("/")[2]
        key = "/".join(stored_path.split("/")[3:])
        url = s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": bucket, "Key": key},
            ExpiresIn=3600,
        )
        return url
    else:
        # Local file
        if os.path.exists(stored_path):
            return stored_path
        return None


async def delete_file(stored_path: str) -> bool:
    """Delete a stored file."""
    try:
        if stored_path.startswith("s3://"):
            import boto3

            s3_client = boto3.client(
                "s3",
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_REGION,
            )
            bucket = stored_path.split("/")[2]
            key = "/".join(stored_path.split("/")[3:])
            s3_client.delete_object(Bucket=bucket, Key=key)
        else:
            if os.path.exists(stored_path):
                os.remove(stored_path)
        return True
    except Exception:
        return False
