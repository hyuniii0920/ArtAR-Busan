from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.dependencies import get_db
from app.models import Event, Venue
from app.schemas.common import ApiResponse, PaginationMeta
from app.schemas.event import EventListResponse, EventResponse

router = APIRouter(prefix="/events", tags=["App - Events"])


@router.get("", response_model=ApiResponse[list[EventListResponse]])
async def list_events(
    lang: str = Query(default="ko", pattern=r"^(ko|en|jp|cn)$"),
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    today = date.today()
    base_query = select(Event).where(
        Event.is_public.is_(True),
        Event.start_date <= today,
        Event.end_date >= today,
    )

    # Count
    count_result = await db.execute(
        select(func.count()).select_from(base_query.subquery())
    )
    total = count_result.scalar() or 0

    # Fetch with venue count
    offset = (page - 1) * per_page
    result = await db.execute(
        base_query.order_by(Event.start_date.desc())
        .offset(offset)
        .limit(per_page)
    )
    events = result.scalars().all()

    items = []
    for event in events:
        venue_count_result = await db.execute(
            select(func.count()).where(Venue.event_id == event.id)
        )
        items.append(
            EventListResponse(
                id=event.id,
                name=event.name,
                slug=event.slug,
                start_date=event.start_date,
                end_date=event.end_date,
                is_public=event.is_public,
                created_at=event.created_at,
                venue_count=venue_count_result.scalar() or 0,
            )
        )

    return ApiResponse(
        data=items,
        meta=PaginationMeta(total=total, page=page, per_page=per_page),
    )


@router.get("/{slug}", response_model=ApiResponse[EventResponse])
async def get_event(
    slug: str,
    lang: str = Query(default="ko", pattern=r"^(ko|en|jp|cn)$"),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Event)
        .options(selectinload(Event.theme))
        .where(Event.slug == slug)
    )
    event = result.scalar_one_or_none()
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    venue_count_result = await db.execute(
        select(func.count()).where(Venue.event_id == event.id)
    )

    return ApiResponse(
        data=EventResponse(
            id=event.id,
            name=event.name,
            slug=event.slug,
            start_date=event.start_date,
            end_date=event.end_date,
            is_public=event.is_public,
            created_at=event.created_at,
            updated_at=event.updated_at,
            theme=event.theme,
            venue_count=venue_count_result.scalar() or 0,
        )
    )
