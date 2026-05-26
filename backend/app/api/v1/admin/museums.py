import uuid
from urllib.parse import unquote

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.dependencies import get_db, require_super_admin
from app.errors import (
    contact_required,
    invalid_payload,
    museum_name_required,
    not_museum,
    user_not_found,
)
from app.models import User
from app.models.user import ROLE_MUSEUM
from app.schemas.common import ApiResponse, PaginationMeta
from app.schemas.user import MuseumStatus, MuseumStatusUpdate, UserResponse
from app.services import gcs

router = APIRouter(prefix="/museums", tags=["Admin - Museums"])

PROOF_PREFIX = "proofs"


async def _get_museum(db: AsyncSession, user_id: uuid.UUID) -> User:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise user_not_found()
    if user.role != ROLE_MUSEUM:
        raise not_museum()
    return user


def _proof_key_from_url(url: str | None) -> str | None:
    if not url:
        return None
    prefix = f"https://storage.googleapis.com/{settings.GCS_BUCKET}/"
    if not url.startswith(prefix):
        return None
    return unquote(url[len(prefix):])


@router.get("", response_model=ApiResponse[list[UserResponse]])
async def list_museums(
    status: MuseumStatus | None = Query(default=None),
    q: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(require_super_admin),
):
    filters = [User.role == ROLE_MUSEUM]
    if status is not None:
        filters.append(User.museum_status == status)
    if q:
        like = f"%{q.strip()}%"
        filters.append(or_(User.email.ilike(like), User.museum_name.ilike(like)))

    count_result = await db.execute(
        select(func.count()).select_from(User).where(*filters)
    )
    total = count_result.scalar() or 0

    offset = (page - 1) * per_page
    result = await db.execute(
        select(User)
        .where(*filters)
        .order_by(User.created_at.desc())
        .offset(offset)
        .limit(per_page)
    )
    users = result.scalars().all()

    return ApiResponse(
        data=[UserResponse.model_validate(u) for u in users],
        meta=PaginationMeta(total=total, page=page, per_page=per_page),
    )


@router.patch("/{user_id}/status", response_model=ApiResponse[UserResponse])
async def update_museum_status(
    user_id: uuid.UUID,
    body: MuseumStatusUpdate,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(require_super_admin),
):
    user = await _get_museum(db, user_id)
    user.museum_status = body.museum_status
    await db.flush()
    await db.refresh(user)
    return ApiResponse(data=UserResponse.model_validate(user))


@router.patch("/{user_id}", response_model=ApiResponse[UserResponse])
async def update_museum(
    user_id: uuid.UUID,
    museum_name: str = Form(default=""),
    contact: str = Form(default=""),
    proof_file: UploadFile | None = File(default=None),
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(require_super_admin),
):
    user = await _get_museum(db, user_id)

    museum_name = museum_name.strip()
    contact = contact.strip()
    if not museum_name:
        raise museum_name_required()
    if not contact:
        raise contact_required()

    user.museum_name = museum_name
    user.contact = contact

    if proof_file is not None:
        content = await proof_file.read()
        if content:
            try:
                proof = gcs.upload_bytes(
                    content=content,
                    filename=proof_file.filename or "proof",
                    content_type=proof_file.content_type,
                    prefix=PROOF_PREFIX,
                )
            except RuntimeError as e:
                raise invalid_payload(f"증빙 파일 업로드 실패: {e}")
            user.proof_file_name = proof["filename"]
            user.proof_file_url = proof["public_url"]

    await db.flush()
    await db.refresh(user)
    return ApiResponse(data=UserResponse.model_validate(user))


@router.delete("/{user_id}", response_model=ApiResponse[dict])
async def delete_museum(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(require_super_admin),
):
    user = await _get_museum(db, user_id)

    key = _proof_key_from_url(user.proof_file_url)
    await db.delete(user)

    if key:
        try:
            gcs.delete_object(key)
        except Exception:
            pass  # 증빙 파일 정리는 best-effort

    return ApiResponse(data={"ok": True})
