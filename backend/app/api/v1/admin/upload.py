from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies import get_current_admin
from app.schemas.common import ApiResponse
from app.schemas.upload import SignedUrlRequest, SignedUrlResponse
from app.services import gcs

router = APIRouter(prefix="/upload", tags=["Admin - Upload"])


@router.post("/signed-url", response_model=ApiResponse[SignedUrlResponse])
async def request_signed_url(
    body: SignedUrlRequest,
    _admin: str = Depends(get_current_admin),
):
    try:
        result = gcs.generate_signed_upload_url(
            filename=body.filename,
            content_type=body.content_type,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e)
        )

    return ApiResponse(data=SignedUrlResponse(**result))


@router.post("/image", deprecated=True, status_code=status.HTTP_410_GONE)
async def upload_image_deprecated():
    raise HTTPException(
        status_code=status.HTTP_410_GONE,
        detail=(
            "Replaced by signed URL upload. "
            "1) POST /api/v1/admin/upload/signed-url with {filename, content_type} "
            "to obtain `upload_url` (PUT) and `public_url`. "
            "2) PUT the file directly to `upload_url`. "
            "3) Save `public_url` on the artwork/theme record."
        ),
    )
