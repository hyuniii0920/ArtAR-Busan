from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_admin, get_db
from app.models import Place
from app.schemas.common import ApiResponse
from app.schemas.place import PlaceCreate, PlaceResponse, PlaceUpdate

router = APIRouter(prefix="/places", tags=["Admin - Places"])


@router.get("", response_model=ApiResponse[list[PlaceResponse]])
async def list_places(
    db: AsyncSession = Depends(get_db),
    _admin: str = Depends(get_current_admin),
):
    result = await db.execute(select(Place).order_by(Place.sort_order, Place.id))
    return ApiResponse(
        data=[PlaceResponse.model_validate(p) for p in result.scalars().all()]
    )


@router.post("", response_model=ApiResponse[PlaceResponse], status_code=201)
async def create_place(
    body: PlaceCreate,
    db: AsyncSession = Depends(get_db),
    _admin: str = Depends(get_current_admin),
):
    place = Place(**body.model_dump())
    db.add(place)
    await db.flush()
    await db.refresh(place)
    return ApiResponse(data=PlaceResponse.model_validate(place))


@router.get("/{place_id}", response_model=ApiResponse[PlaceResponse])
async def get_place(
    place_id: int,
    db: AsyncSession = Depends(get_db),
    _admin: str = Depends(get_current_admin),
):
    result = await db.execute(select(Place).where(Place.id == place_id))
    place = result.scalar_one_or_none()
    if not place:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return ApiResponse(data=PlaceResponse.model_validate(place))


@router.put("/{place_id}", response_model=ApiResponse[PlaceResponse])
async def update_place(
    place_id: int,
    body: PlaceUpdate,
    db: AsyncSession = Depends(get_db),
    _admin: str = Depends(get_current_admin),
):
    result = await db.execute(select(Place).where(Place.id == place_id))
    place = result.scalar_one_or_none()
    if not place:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    for key, value in body.model_dump(exclude_unset=True).items():
        setattr(place, key, value)

    await db.flush()
    await db.refresh(place)
    return ApiResponse(data=PlaceResponse.model_validate(place))


@router.delete("/{place_id}", status_code=204)
async def delete_place(
    place_id: int,
    db: AsyncSession = Depends(get_db),
    _admin: str = Depends(get_current_admin),
):
    result = await db.execute(select(Place).where(Place.id == place_id))
    place = result.scalar_one_or_none()
    if not place:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    await db.delete(place)
