from collections.abc import AsyncGenerator
from datetime import datetime, timedelta, timezone

import pytest_asyncio
from bcrypt import gensalt, hashpw
from httpx import ASGITransport, AsyncClient
from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.config import settings
from app.database import Base
from app.dependencies import get_db
from app.main import app
from app.models import User
from app.models.user import (
    ROLE_MUSEUM,
    ROLE_SUPER_ADMIN,
    STATUS_PENDING,
)

TEST_PASSWORD = "test-only-password"
_PASSWORD_HASH = hashpw(TEST_PASSWORD.encode(), gensalt()).decode()

test_engine = create_async_engine(
    settings.DATABASE_URL, echo=False, poolclass=NullPool
)
test_session = async_sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)


def make_token(user_id, hours: int = 1) -> str:
    expire = datetime.now(timezone.utc) + timedelta(hours=hours)
    return jwt.encode(
        {"sub": str(user_id), "exp": expire},
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM,
    )


@pytest_asyncio.fixture(scope="session", autouse=True, loop_scope="session")
async def setup_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await test_engine.dispose()


@pytest_asyncio.fixture(autouse=True, loop_scope="session")
async def _clean_tables():
    async with test_engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            await conn.execute(table.delete())
    yield


@pytest_asyncio.fixture(loop_scope="session")
async def db() -> AsyncGenerator[AsyncSession]:
    async with test_session() as session:
        yield session


@pytest_asyncio.fixture(loop_scope="session")
async def client() -> AsyncGenerator[AsyncClient]:
    async def override_get_db():
        async with test_session() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as c:
        yield c
    app.dependency_overrides.clear()


@pytest_asyncio.fixture(loop_scope="session")
async def super_admin(db: AsyncSession) -> User:
    user = User(
        email="super@test.local",
        password_hash=_PASSWORD_HASH,
        role=ROLE_SUPER_ADMIN,
        museum_status=None,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@pytest_asyncio.fixture(loop_scope="session")
async def museum_user(db: AsyncSession) -> User:
    user = User(
        email="museum@test.local",
        password_hash=_PASSWORD_HASH,
        role=ROLE_MUSEUM,
        museum_status=STATUS_PENDING,
        museum_name="테스트미술관",
        contact="010-0000-0000",
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@pytest_asyncio.fixture(loop_scope="session")
async def auth_headers(super_admin: User) -> dict:
    return {"Authorization": f"Bearer {make_token(super_admin.id)}"}


@pytest_asyncio.fixture(loop_scope="session")
async def museum_headers(museum_user: User) -> dict:
    return {"Authorization": f"Bearer {make_token(museum_user.id)}"}
