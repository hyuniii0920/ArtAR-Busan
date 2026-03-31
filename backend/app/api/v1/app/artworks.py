from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db
from app.models import Artwork
from app.schemas.artwork import ArtworkLocalizedResponse
from app.schemas.common import ApiResponse
from app.utils.i18n import localize

router = APIRouter(prefix="/venues", tags=["App - Artworks"])


@router.get(
    "/{venue_id}/artworks",
    response_model=ApiResponse[list[ArtworkLocalizedResponse]],
)
async def list_artworks_by_venue(
    venue_id: str,
    lang: str = Query(default="ko", pattern=r"^(ko|en|jp|cn)$"),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Artwork)
        .where(Artwork.venue_id == venue_id, Artwork.is_active.is_(True))
        .order_by(Artwork.sort_order)
    )
    artworks = result.scalars().all()

    items = [
        ArtworkLocalizedResponse(
            id=a.id,
            venue_id=a.venue_id,
            title=localize(a.title_i18n, lang),
            description=localize(a.description_i18n, lang),
            artist=a.artist,
            marker_image_url=a.marker_image_url,
            media_url=a.media_url,
            media_type=a.media_type,
            sort_order=a.sort_order,
        )
        for a in artworks
    ]

    return ApiResponse(data=items)
