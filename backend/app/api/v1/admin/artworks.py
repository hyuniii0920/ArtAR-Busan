import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_admin, get_db
from app.models import Artwork, Venue
from app.schemas.artwork import ArtworkCreate, ArtworkResponse, ArtworkUpdate
from app.schemas.common import ApiResponse

router = APIRouter(tags=["Admin - Artworks"])


@router.get(
    "/venues/{venue_id}/artworks",
    response_model=ApiResponse[list[ArtworkResponse]],
)
async def list_artworks(
    venue_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _admin: str = Depends(get_current_admin),
):
    result = await db.execute(
        select(Artwork).where(Artwork.venue_id == venue_id).order_by(Artwork.sort_order)
    )
    artworks = result.scalars().all()

    return ApiResponse(
        data=[ArtworkResponse.model_validate(a) for a in artworks]
    )


@router.post(
    "/venues/{venue_id}/artworks",
    response_model=ApiResponse[ArtworkResponse],
    status_code=201,
)
async def create_artwork(
    venue_id: uuid.UUID,
    body: ArtworkCreate,
    db: AsyncSession = Depends(get_db),
    _admin: str = Depends(get_current_admin),
):
    venue_result = await db.execute(select(Venue).where(Venue.id == venue_id))
    if not venue_result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    artwork = Artwork(
        venue_id=venue_id,
        title_i18n=body.title_i18n.to_dict(),
        description_i18n=body.description_i18n.to_dict(),
        artist=body.artist,
        marker_image_url=body.marker_image_url,
        media_url=body.media_url,
        media_type=body.media_type,
        sort_order=body.sort_order,
        is_active=body.is_active,
    )
    db.add(artwork)
    await db.flush()
    await db.refresh(artwork)

    return ApiResponse(data=ArtworkResponse.model_validate(artwork))


@router.put("/artworks/{artwork_id}", response_model=ApiResponse[ArtworkResponse])
async def update_artwork(
    artwork_id: uuid.UUID,
    body: ArtworkUpdate,
    db: AsyncSession = Depends(get_db),
    _admin: str = Depends(get_current_admin),
):
    result = await db.execute(select(Artwork).where(Artwork.id == artwork_id))
    artwork = result.scalar_one_or_none()
    if not artwork:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    update_data = body.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if key in ("title_i18n", "description_i18n") and value is not None:
            setattr(
                artwork,
                key,
                value.to_dict() if hasattr(value, "to_dict") else value,
            )
        else:
            setattr(artwork, key, value)

    await db.flush()
    await db.refresh(artwork)

    return ApiResponse(data=ArtworkResponse.model_validate(artwork))


@router.delete("/artworks/{artwork_id}", status_code=204)
async def delete_artwork(
    artwork_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _admin: str = Depends(get_current_admin),
):
    result = await db.execute(select(Artwork).where(Artwork.id == artwork_id))
    artwork = result.scalar_one_or_none()
    if not artwork:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    await db.delete(artwork)
