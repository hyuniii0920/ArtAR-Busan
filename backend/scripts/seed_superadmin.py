"""SUPER_ADMIN 계정을 DB users 테이블에 시드한다 (멱등).

email은 SUPER_ADMIN_EMAIL, 비밀번호 해시는 기존 ADMIN_PASSWORD_HASH를 재사용한다.
즉 기존 환경변수 단일 관리자가 DB 기반 SUPER_ADMIN으로 승계된다.

사용:
    python -m scripts.seed_superadmin
"""

import asyncio

from sqlalchemy import select

from app.config import settings
from app.database import async_session
from app.models import User
from app.models.user import ROLE_SUPER_ADMIN


async def seed() -> None:
    if not settings.ADMIN_PASSWORD_HASH:
        print("ADMIN_PASSWORD_HASH가 비어 있어 중단합니다.")
        return

    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.email == settings.SUPER_ADMIN_EMAIL)
        )
        if result.scalar_one_or_none():
            print(f"SUPER_ADMIN 이미 존재: {settings.SUPER_ADMIN_EMAIL}")
            return

        session.add(
            User(
                email=settings.SUPER_ADMIN_EMAIL,
                password_hash=settings.ADMIN_PASSWORD_HASH,
                role=ROLE_SUPER_ADMIN,
                museum_status=None,
            )
        )
        await session.commit()
        print(f"SUPER_ADMIN 생성 완료: {settings.SUPER_ADMIN_EMAIL}")


if __name__ == "__main__":
    asyncio.run(seed())
