import uuid
from collections.abc import AsyncGenerator
from datetime import datetime, timezone

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import async_session
from app.errors import forbidden, not_logged_in
from app.models import User
from app.models.user import ROLE_SUPER_ADMIN

security = HTTPBearer(auto_error=False)


async def get_db() -> AsyncGenerator[AsyncSession]:
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


def _decode_token(credentials: HTTPAuthorizationCredentials | None) -> str:
    if credentials is None:
        raise not_logged_in()
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
        )
    except JWTError:
        raise not_logged_in()

    sub: str | None = payload.get("sub")
    exp: int | None = payload.get("exp")
    if sub is None:
        raise not_logged_in()
    if exp and datetime.fromtimestamp(exp, tz=timezone.utc) < datetime.now(
        tz=timezone.utc
    ):
        raise not_logged_in()
    return sub


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    sub = _decode_token(credentials)
    try:
        user_id = uuid.UUID(sub)
    except ValueError:
        raise not_logged_in()

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise not_logged_in()
    return user


async def require_super_admin(
    user: User = Depends(get_current_user),
) -> User:
    if user.role != ROLE_SUPER_ADMIN:
        raise forbidden()
    return user


async def get_current_admin(
    user: User = Depends(get_current_user),
) -> str:
    """기존 라우터(events/venues/artworks/stats/upload) 호환용 — email 반환."""
    return user.email
