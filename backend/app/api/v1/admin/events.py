import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.dependencies import get_current_admin, get_db
from app.models import Event, EventTheme, Venue
from app.schemas.common import ApiResponse, PaginationMeta
from app.schemas.event import (
    EventCreate,
    EventListResponse,
    EventResponse,
    EventThemeCreate,
    EventThemeResponse,
    EventUpdate,
)

router = APIRouter(prefix="/events", tags=["Admin - Events"])


@router.get("", response_model=ApiResponse[list[EventListResponse]])
async def list_events(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _admin: str = Depends(get_current_admin),
):
    count_result = await db.execute(select(func.count()).select_from(Event))
    total = count_result.scalar() or 0

    offset = (page - 1) * per_page
    result = await db.execute(
        select(Event).order_by(Event.created_at.desc()).offset(offset).limit(per_page)
    )
    events = result.scalars().all()

    items = []
    for event in events:
        vc = await db.execute(
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
                venue_count=vc.scalar() or 0,
            )
        )

    return ApiResponse(
        data=items,
        meta=PaginationMeta(total=total, page=page, per_page=per_page),
    )


@router.post("", response_model=ApiResponse[EventResponse], status_code=201)
async def create_event(
    body: EventCreate,
    db: AsyncSession = Depends(get_db),
    _admin: str = Depends(get_current_admin),
):
    dup = await db.execute(select(Event.id).where(Event.slug == body.slug))
    if dup.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"slug '{body.slug}' already exists",
        )

    event = Event(**body.model_dump())
    db.add(event)
    await db.flush()
    await db.refresh(event)

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
            venue_count=0,
        )
    )


@router.get("/{event_id}", response_model=ApiResponse[EventResponse])
async def get_event(
    event_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _admin: str = Depends(get_current_admin),
):
    result = await db.execute(
        select(Event).options(selectinload(Event.theme)).where(Event.id == event_id)
    )
    event = result.scalar_one_or_none()
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    vc = await db.execute(
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
            venue_count=vc.scalar() or 0,
        )
    )


@router.put("/{event_id}", response_model=ApiResponse[EventResponse])
async def update_event(
    event_id: uuid.UUID,
    body: EventUpdate,
    db: AsyncSession = Depends(get_db),
    _admin: str = Depends(get_current_admin),
):
    result = await db.execute(
        select(Event).options(selectinload(Event.theme)).where(Event.id == event_id)
    )
    event = result.scalar_one_or_none()
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    update_data = body.model_dump(exclude_unset=True)

    if "slug" in update_data and update_data["slug"] != event.slug:
        dup = await db.execute(
            select(Event.id).where(
                Event.slug == update_data["slug"], Event.id != event_id
            )
        )
        if dup.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"slug '{update_data['slug']}' already exists",
            )

    for key, value in update_data.items():
        setattr(event, key, value)

    await db.flush()
    await db.refresh(event)

    vc = await db.execute(
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
            venue_count=vc.scalar() or 0,
        )
    )


@router.delete("/{event_id}", status_code=204)
async def delete_event(
    event_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _admin: str = Depends(get_current_admin),
):
    result = await db.execute(select(Event).where(Event.id == event_id))
    event = result.scalar_one_or_none()
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    await db.delete(event)


# --- Theme ---
@router.put("/{event_id}/theme", response_model=ApiResponse[EventThemeResponse])
async def upsert_theme(
    event_id: uuid.UUID,
    body: EventThemeCreate,
    db: AsyncSession = Depends(get_db),
    _admin: str = Depends(get_current_admin),
):
    # Verify event exists
    event_result = await db.execute(select(Event).where(Event.id == event_id))
    if not event_result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    result = await db.execute(
        select(EventTheme).where(EventTheme.event_id == event_id)
    )
    theme = result.scalar_one_or_none()

    if theme:
        for key, value in body.model_dump().items():
            setattr(theme, key, value)
    else:
        theme = EventTheme(event_id=event_id, **body.model_dump())
        db.add(theme)

    await db.flush()
    await db.refresh(theme)

    return ApiResponse(data=EventThemeResponse.model_validate(theme))
