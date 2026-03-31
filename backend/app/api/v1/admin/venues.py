import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_admin, get_db
from app.models import Artwork, Event, Venue
from app.schemas.common import ApiResponse
from app.schemas.venue import VenueCreate, VenueResponse, VenueUpdate

router = APIRouter(tags=["Admin - Venues"])


@router.get(
    "/events/{event_id}/venues", response_model=ApiResponse[list[VenueResponse]]
)
async def list_venues(
    event_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _admin: str = Depends(get_current_admin),
):
    result = await db.execute(
        select(Venue).where(Venue.event_id == event_id).order_by(Venue.sort_order)
    )
    venues = result.scalars().all()

    items = []
    for venue in venues:
        ac = await db.execute(
            select(func.count()).where(Artwork.venue_id == venue.id)
        )
        items.append(
            VenueResponse(
                id=venue.id,
                event_id=venue.event_id,
                name_i18n=venue.name_i18n,
                lat=venue.lat,
                lng=venue.lng,
                description_i18n=venue.description_i18n,
                address=venue.address,
                sort_order=venue.sort_order,
                is_active=venue.is_active,
                artwork_count=ac.scalar() or 0,
            )
        )

    return ApiResponse(data=items)


@router.post(
    "/events/{event_id}/venues",
    response_model=ApiResponse[VenueResponse],
    status_code=201,
)
async def create_venue(
    event_id: uuid.UUID,
    body: VenueCreate,
    db: AsyncSession = Depends(get_db),
    _admin: str = Depends(get_current_admin),
):
    event_result = await db.execute(select(Event).where(Event.id == event_id))
    if not event_result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    venue = Venue(
        event_id=event_id,
        name_i18n=body.name_i18n.to_dict(),
        lat=body.lat,
        lng=body.lng,
        description_i18n=body.description_i18n.to_dict(),
        address=body.address,
        sort_order=body.sort_order,
        is_active=body.is_active,
    )
    db.add(venue)
    await db.flush()
    await db.refresh(venue)

    return ApiResponse(
        data=VenueResponse(
            id=venue.id,
            event_id=venue.event_id,
            name_i18n=venue.name_i18n,
            lat=venue.lat,
            lng=venue.lng,
            description_i18n=venue.description_i18n,
            address=venue.address,
            sort_order=venue.sort_order,
            is_active=venue.is_active,
            artwork_count=0,
        )
    )


@router.put("/venues/{venue_id}", response_model=ApiResponse[VenueResponse])
async def update_venue(
    venue_id: uuid.UUID,
    body: VenueUpdate,
    db: AsyncSession = Depends(get_db),
    _admin: str = Depends(get_current_admin),
):
    result = await db.execute(select(Venue).where(Venue.id == venue_id))
    venue = result.scalar_one_or_none()
    if not venue:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    update_data = body.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if key in ("name_i18n", "description_i18n") and value is not None:
            setattr(venue, key, value.to_dict() if hasattr(value, "to_dict") else value)
        else:
            setattr(venue, key, value)

    await db.flush()
    await db.refresh(venue)

    ac = await db.execute(
        select(func.count()).where(Artwork.venue_id == venue.id)
    )

    return ApiResponse(
        data=VenueResponse(
            id=venue.id,
            event_id=venue.event_id,
            name_i18n=venue.name_i18n,
            lat=venue.lat,
            lng=venue.lng,
            description_i18n=venue.description_i18n,
            address=venue.address,
            sort_order=venue.sort_order,
            is_active=venue.is_active,
            artwork_count=ac.scalar() or 0,
        )
    )


@router.delete("/venues/{venue_id}", status_code=204)
async def delete_venue(
    venue_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _admin: str = Depends(get_current_admin),
):
    result = await db.execute(select(Venue).where(Venue.id == venue_id))
    venue = result.scalar_one_or_none()
    if not venue:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    await db.delete(venue)
