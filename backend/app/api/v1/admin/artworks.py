import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_admin, get_db
from app.models import Artwork, Venue
from app.schemas.artwork import ArtworkCreate, ArtworkResponse, ArtworkUpdate
from app.schemas.common import ApiResponse

router = APIRouter(tags=["Admin - Artworks"])


def _to_response(artwork: Artwork) -> ArtworkResponse:
    """ORM → 응답 변환. code가 있으면 QR용 딥링크(artar://work/{code})를 채운다."""
    resp = ArtworkResponse.model_validate(artwork)
    if artwork.code is not None:
        resp.qr_url = f"artar://work/{artwork.code}"
    return resp


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

    return ApiResponse(data=[_to_response(a) for a in artworks])


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

    # QR에 인코딩될 정수 code 자동 채번 (없으면 101부터, 기존 시드 규약과 일치)
    max_code = (await db.execute(select(func.max(Artwork.code)))).scalar()
    next_code = max_code + 1 if max_code is not None else 101

    artwork = Artwork(
        venue_id=venue_id,
        code=next_code,
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

    return ApiResponse(data=_to_response(artwork))


@router.get("/artworks/{artwork_id}", response_model=ApiResponse[ArtworkResponse])
async def get_artwork(
    artwork_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _admin: str = Depends(get_current_admin),
):
    result = await db.execute(select(Artwork).where(Artwork.id == artwork_id))
    artwork = result.scalar_one_or_none()
    if not artwork:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return ApiResponse(data=_to_response(artwork))


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

    return ApiResponse(data=_to_response(artwork))


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
