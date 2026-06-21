"""Android 앱 전용 공개 API — /api/works/{id}.

기존 /api/v1/app/* 와 별개로, 안드로이드가 요구한 평탄 snake_case 스키마와
정수 ID(Artwork.code)를 제공한다. 인증 불필요.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db
from app.models import Artwork
from app.schemas.work import WorkResponse
from app.utils.i18n import localize

router = APIRouter(prefix="/works", tags=["App - Works (Android)"])

# Android 언어코드 → 내부 i18n 키 매핑
_LANG_MAP = {"ja": "jp", "zh": "cn"}


def _loc(field: dict | None, lang: str) -> str | None:
    """로컬라이즈 결과가 비면 None (Android nullable 규약)."""
    value = localize(field, lang)
    return value or None


@router.get("/{id}", response_model=WorkResponse)
async def get_work(
    id: int,
    lang: str = Query(default="ko", pattern=r"^(ko|en|ja|zh)$"),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Artwork).where(Artwork.code == id))
    artwork = result.scalar_one_or_none()
    if artwork is None:
        raise HTTPException(status_code=404, detail="Artwork not found")

    internal_lang = _LANG_MAP.get(lang, lang)

    # 설명 우선순위: 요약 = summary → description, 상세 = detail → description → 요약
    summary = _loc(artwork.summary_description_i18n, internal_lang) or _loc(
        artwork.description_i18n, internal_lang
    )
    detail = (
        _loc(artwork.detail_description_i18n, internal_lang)
        or _loc(artwork.description_i18n, internal_lang)
        or summary
    )

    return WorkResponse(
        id=artwork.code,
        title=localize(artwork.title_i18n, internal_lang),
        artist=artwork.artist,
        summary_description=summary,
        detail_description=detail,
        image_url=artwork.image_url,
        ar_asset_url=artwork.ar_asset_url,
        marker_image_url=artwork.marker_image_url,
        marker_width_meters=artwork.marker_width_meters,
        media_url=artwork.media_url,
    )
