from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db
from app.models import Artwork, Event, Venue
from app.schemas.common import ApiResponse
from app.schemas.venue import VenueLocalizedResponse
from app.utils.i18n import localize

router = APIRouter(tags=["App - Venues"])


@router.get(
    "/events/{slug}/venues",
    response_model=ApiResponse[list[VenueLocalizedResponse]],
)
async def list_venues_by_event(
    slug: str,
    lang: str = Query(default="ko", pattern=r"^(ko|en|jp|cn)$"),
    db: AsyncSession = Depends(get_db),
):
    event_result = await db.execute(select(Event).where(Event.slug == slug))
    event = event_result.scalar_one_or_none()
    if not event:
        return ApiResponse(data=[])

    result = await db.execute(
        select(Venue)
        .where(Venue.event_id == event.id, Venue.is_active.is_(True))
        .order_by(Venue.sort_order)
    )
    venues = result.scalars().all()

    items = []
    for venue in venues:
        artwork_count_result = await db.execute(
            select(func.count()).where(
                Artwork.venue_id == venue.id, Artwork.is_active.is_(True)
            )
        )
        items.append(
            VenueLocalizedResponse(
                id=venue.id,
                event_id=venue.event_id,
                name=localize(venue.name_i18n, lang),
                lat=venue.lat,
                lng=venue.lng,
                description=localize(venue.description_i18n, lang),
                address=venue.address,
                sort_order=venue.sort_order,
                artwork_count=artwork_count_result.scalar() or 0,
            )
        )

    return ApiResponse(data=items)
