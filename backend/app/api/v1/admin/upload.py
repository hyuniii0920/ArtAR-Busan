import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status

from app.config import settings
from app.dependencies import get_current_admin
from app.schemas.common import ApiResponse

router = APIRouter(prefix="/upload", tags=["Admin - Upload"])

ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


@router.post("/image", response_model=ApiResponse[dict])
async def upload_image(
    file: UploadFile,
    _admin: str = Depends(get_current_admin),
):
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type: {file.content_type}",
        )

    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File size exceeds 10MB limit",
        )

    # Generate unique filename
    ext = file.filename.rsplit(".", 1)[-1] if file.filename else "jpg"
    filename = f"uploads/{uuid.uuid4()}.{ext}"

    # TODO: GCS 업로드 구현 (7-8주차)
    # 현재는 URL 형태만 반환
    url = f"https://storage.googleapis.com/{settings.GCS_BUCKET}/{filename}"

    return ApiResponse(data={"url": url, "filename": filename})
