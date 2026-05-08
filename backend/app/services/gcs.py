"""GCS 업로드 — Signed URL 방식.

Cloud Run runtime SA의 self-impersonation으로 v4 PUT signed URL을 발급한다.
클라이언트는 받은 URL에 직접 PUT으로 파일을 업로드.
"""

import uuid
from datetime import timedelta
from urllib.parse import quote

import google.auth
from google.auth.transport import requests as gauth_requests
from google.cloud import storage

from app.config import settings

ALLOWED_CONTENT_TYPES: set[str] = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/gif",
}
DEFAULT_EXPIRES_MINUTES = 15


def _get_credentials():
    credentials, _ = google.auth.default()
    credentials.refresh(gauth_requests.Request())
    return credentials


def generate_signed_upload_url(
    filename: str,
    content_type: str,
    expires_in_minutes: int = DEFAULT_EXPIRES_MINUTES,
) -> dict:
    if content_type not in ALLOWED_CONTENT_TYPES:
        raise ValueError(f"Unsupported content_type: {content_type}")

    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else "bin"
    key = f"uploads/{uuid.uuid4()}.{ext}"

    credentials = _get_credentials()
    sa_email = getattr(credentials, "service_account_email", None)
    if not sa_email:
        raise RuntimeError(
            "GCS signing unavailable: credentials lack service_account_email. "
            "Cloud Run에서는 default Compute SA가 사용되며, 로컬에서는 "
            "`gcloud auth application-default login`으로 사용자 자격을 쓰면 발급 불가. "
            "SA impersonation을 설정하거나 SA 키 파일을 사용하세요."
        )

    client = storage.Client(credentials=credentials)
    blob = client.bucket(settings.GCS_BUCKET).blob(key)

    upload_url = blob.generate_signed_url(
        version="v4",
        expiration=timedelta(minutes=expires_in_minutes),
        method="PUT",
        content_type=content_type,
        service_account_email=sa_email,
        access_token=credentials.token,
    )

    public_url = (
        f"https://storage.googleapis.com/{settings.GCS_BUCKET}/{quote(key)}"
    )

    return {
        "upload_url": upload_url,
        "public_url": public_url,
        "key": key,
        "content_type": content_type,
        "expires_in_minutes": expires_in_minutes,
    }
