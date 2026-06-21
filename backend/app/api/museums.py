"""Android 앱 전용 공개 API — /api/museums.

미술관/문화공간 장소 디렉토리. 인증 불필요, 평탄 camelCase 응답.
api/works.py 와 동일한 비버전 공개 API 패턴.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db
from app.models import Place
from app.schemas.place import PlaceResponse

router = APIRouter(prefix="/museums", tags=["App - Museums"])


@router.get("", response_model=list[PlaceResponse])
async def list_museums(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Place)
        .where(Place.is_active.is_(True))
        .order_by(Place.sort_order, Place.id)
    )
    return list(result.scalars().all())


@router.get("/{id}", response_model=PlaceResponse)
async def get_museum(id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Place).where(Place.id == id))
    place = result.scalar_one_or_none()
    if place is None:
        raise HTTPException(status_code=404, detail="Place not found")
    return place
