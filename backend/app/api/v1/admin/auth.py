import re
import uuid
from datetime import datetime, timedelta, timezone

from bcrypt import checkpw, gensalt, hashpw
from fastapi import APIRouter, Depends, File, Form, UploadFile
from jose import jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.dependencies import get_current_user, get_db
from app.errors import (
    contact_required,
    email_already_exists,
    email_required,
    invalid_credentials,
    invalid_payload,
    museum_name_required,
    not_museum,
    password_required,
)
from app.models import User
from app.models.user import ROLE_MUSEUM, STATUS_PENDING
from app.schemas.common import ApiResponse
from app.schemas.user import LoginRequest, TokenWithUser, UserResponse
from app.services import gcs

router = APIRouter(prefix="/auth", tags=["Admin - Auth"])

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PROOF_PREFIX = "proofs"


def _create_token(user_id: uuid.UUID) -> str:
    expire = datetime.now(timezone.utc) + timedelta(hours=settings.JWT_EXPIRE_HOURS)
    return jwt.encode(
        {"sub": str(user_id), "exp": expire},
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM,
    )


async def _upload_proof(proof_file: UploadFile) -> dict | None:
    content = await proof_file.read()
    if not content:
        return None
    try:
        return gcs.upload_bytes(
            content=content,
            filename=proof_file.filename or "proof",
            content_type=proof_file.content_type,
            prefix=PROOF_PREFIX,
        )
    except RuntimeError as e:
        raise invalid_payload(f"증빙 파일 업로드 실패: {e}")


@router.post("/login", response_model=TokenWithUser)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == body.username))
    user = result.scalar_one_or_none()
    if user is None or not checkpw(
        body.password.encode(), user.password_hash.encode()
    ):
        raise invalid_credentials()

    return TokenWithUser(
        access_token=_create_token(user.id),
        user=UserResponse.model_validate(user),
    )


@router.post(
    "/register-museum",
    response_model=ApiResponse[TokenWithUser],
    status_code=201,
)
async def register_museum(
    email: str = Form(default=""),
    password: str = Form(default=""),
    museum_name: str = Form(default=""),
    contact: str = Form(default=""),
    proof_file: UploadFile | None = File(default=None),
    db: AsyncSession = Depends(get_db),
):
    email = email.strip()
    museum_name = museum_name.strip()
    contact = contact.strip()

    if not email:
        raise email_required()
    if not EMAIL_RE.match(email):
        raise invalid_payload("이메일 형식이 올바르지 않습니다.")
    if not password:
        raise password_required()
    if not museum_name:
        raise museum_name_required()
    if not contact:
        raise contact_required()

    dup = await db.execute(select(User.id).where(User.email == email))
    if dup.scalar_one_or_none():
        raise email_already_exists()

    proof = await _upload_proof(proof_file) if proof_file is not None else None

    user = User(
        email=email,
        password_hash=hashpw(password.encode(), gensalt()).decode(),
        role=ROLE_MUSEUM,
        museum_status=STATUS_PENDING,
        museum_name=museum_name,
        contact=contact,
        proof_file_name=proof["filename"] if proof else None,
        proof_file_url=proof["public_url"] if proof else None,
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)

    return ApiResponse(
        data=TokenWithUser(
            access_token=_create_token(user.id),
            user=UserResponse.model_validate(user),
        )
    )


@router.get("/me", response_model=ApiResponse[UserResponse])
async def me(user: User = Depends(get_current_user)):
    return ApiResponse(data=UserResponse.model_validate(user))


@router.patch(
    "/museum-application/resubmit",
    response_model=ApiResponse[UserResponse],
)
async def resubmit_museum_application(
    museum_name: str = Form(default=""),
    contact: str = Form(default=""),
    proof_file: UploadFile | None = File(default=None),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if user.role != ROLE_MUSEUM:
        raise not_museum()

    museum_name = museum_name.strip()
    contact = contact.strip()
    if not museum_name:
        raise museum_name_required()
    if not contact:
        raise contact_required()

    user.museum_name = museum_name
    user.contact = contact

    if proof_file is not None:
        proof = await _upload_proof(proof_file)
        if proof:
            user.proof_file_name = proof["filename"]
            user.proof_file_url = proof["public_url"]

    user.museum_status = STATUS_PENDING

    await db.flush()
    await db.refresh(user)

    return ApiResponse(data=UserResponse.model_validate(user))
