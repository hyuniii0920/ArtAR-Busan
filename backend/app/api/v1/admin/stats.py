import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import distinct, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_admin, get_db
from app.models import Event, VisitLog
from app.schemas.common import ApiResponse

router = APIRouter(prefix="/stats", tags=["Admin - Stats"])


@router.get("/events/{event_id}/summary", response_model=ApiResponse[dict])
async def event_summary(
    event_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _admin: str = Depends(get_current_admin),
):
    event_result = await db.execute(select(Event).where(Event.id == event_id))
    if not event_result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    base = select(VisitLog).where(VisitLog.event_id == event_id)

    total_visits = await db.execute(
        select(func.count()).select_from(base.subquery())
    )
    unique_devices = await db.execute(
        select(func.count(distinct(VisitLog.device_hash))).where(
            VisitLog.event_id == event_id
        )
    )

    return ApiResponse(
        data={
            "total_visits": total_visits.scalar() or 0,
            "unique_devices": unique_devices.scalar() or 0,
        }
    )


@router.get("/events/{event_id}/venues", response_model=ApiResponse[list[dict]])
async def venue_stats(
    event_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _admin: str = Depends(get_current_admin),
):
    result = await db.execute(
        select(VisitLog.venue_id, func.count().label("visit_count"))
        .where(VisitLog.event_id == event_id, VisitLog.venue_id.isnot(None))
        .group_by(VisitLog.venue_id)
        .order_by(func.count().desc())
    )

    return ApiResponse(
        data=[
            {"venue_id": str(row.venue_id), "visit_count": row.visit_count}
            for row in result.all()
        ]
    )


@router.get("/events/{event_id}/demographics", response_model=ApiResponse[dict])
async def demographics(
    event_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _admin: str = Depends(get_current_admin),
):
    lang_result = await db.execute(
        select(VisitLog.lang, func.count().label("count"))
        .where(VisitLog.event_id == event_id)
        .group_by(VisitLog.lang)
    )

    os_result = await db.execute(
        select(VisitLog.os, func.count().label("count"))
        .where(VisitLog.event_id == event_id)
        .group_by(VisitLog.os)
    )

    return ApiResponse(
        data={
            "by_lang": {row.lang: row.count for row in lang_result.all()},
            "by_os": {row.os: row.count for row in os_result.all()},
        }
    )
