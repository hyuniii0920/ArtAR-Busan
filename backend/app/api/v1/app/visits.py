from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy import distinct, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db
from app.models import Event, VisitLog
from app.rate_limit import limiter
from app.schemas.common import ApiResponse
from app.schemas.visit import VisitCountResponse, VisitCreate, VisitResponse

router = APIRouter(tags=["App - Visits"])


@router.post("/visits", response_model=ApiResponse[VisitResponse], status_code=201)
@limiter.limit("60/minute")
async def create_visit(
    request: Request,
    body: VisitCreate,
    db: AsyncSession = Depends(get_db),
):
    visit = VisitLog(
        event_id=body.event_id,
        venue_id=body.venue_id,
        artwork_id=body.artwork_id,
        lang=body.lang,
        os=body.os,
        device_hash=body.device_hash,
    )
    db.add(visit)
    await db.flush()
    await db.refresh(visit)

    return ApiResponse(data=VisitResponse.model_validate(visit))


@router.get(
    "/events/{slug}/visit-count",
    response_model=ApiResponse[VisitCountResponse],
)
async def get_visit_count(
    slug: str,
    device_hash: str = Query(..., max_length=64),
    db: AsyncSession = Depends(get_db),
):
    event_result = await db.execute(select(Event).where(Event.slug == slug))
    event = event_result.scalar_one_or_none()

    if not event:
        return ApiResponse(
            data=VisitCountResponse(
                event_slug=slug, device_hash=device_hash, unique_venue_count=0
            )
        )

    count_result = await db.execute(
        select(func.count(distinct(VisitLog.venue_id))).where(
            VisitLog.event_id == event.id,
            VisitLog.device_hash == device_hash,
            VisitLog.venue_id.isnot(None),
        )
    )

    return ApiResponse(
        data=VisitCountResponse(
            event_slug=slug,
            device_hash=device_hash,
            unique_venue_count=count_result.scalar() or 0,
        )
    )
