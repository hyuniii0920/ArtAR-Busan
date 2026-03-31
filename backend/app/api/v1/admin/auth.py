from datetime import datetime, timedelta, timezone

from bcrypt import checkpw
from fastapi import APIRouter, HTTPException, status
from jose import jwt

from app.config import settings
from app.schemas.auth import LoginRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["Admin - Auth"])


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest):
    if body.username != settings.ADMIN_USERNAME:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    if not checkpw(
        body.password.encode(), settings.ADMIN_PASSWORD_HASH.encode()
    ):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    expire = datetime.now(timezone.utc) + timedelta(hours=settings.JWT_EXPIRE_HOURS)
    token = jwt.encode(
        {"sub": body.username, "exp": expire},
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM,
    )

    return TokenResponse(access_token=token)
