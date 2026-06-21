import uuid

from datetime import date

from httpx import AsyncClient

from app.models import Artwork, Event, Venue


async def _seed_work(db, code=101, **overrides):
    event = Event(
        name="E", slug=f"e-{uuid.uuid4().hex[:8]}",
        start_date=date(2026, 3, 1), end_date=date(2026, 4, 1), is_public=True,
    )
    db.add(event)
    await db.flush()
    venue = Venue(event_id=event.id, name_i18n={"ko": "v"}, lat=35.1, lng=129.0)
    db.add(venue)
    await db.flush()
    fields = dict(
        code=code,
        venue_id=venue.id,
        title_i18n={"ko": "파도와 기억", "en": "Waves"},
        description_i18n={"ko": "기본 설명", "en": "base desc"},
        summary_description_i18n={"ko": "짧은 설명", "en": "short"},
        detail_description_i18n={"ko": "상세 설명", "en": "detail"},
        artist="홍길동",
        image_url="https://example.com/101.jpg",
        marker_image_url="https://example.com/m101.jpg",
        marker_width_meters=0.21,
        media_url="https://example.com/101.mp4",
    )
    fields.update(overrides)
    art = Artwork(**fields)
    db.add(art)
    await db.commit()
    return art


async def test_get_work_200_and_schema(client: AsyncClient, db):
    await _seed_work(db, code=101)
    res = await client.get("/api/works/101")
    assert res.status_code == 200
    assert res.headers["content-type"].startswith("application/json")
    body = res.json()
    expected_keys = {
        "id", "title", "artist", "summary_description", "detail_description",
        "image_url", "ar_asset_url", "marker_image_url",
        "marker_width_meters", "media_url",
    }
    assert set(body.keys()) == expected_keys
    assert body["id"] == 101
    assert body["title"] == "파도와 기억"
    assert body["artist"] == "홍길동"


async def test_marker_width_is_number(client: AsyncClient, db):
    await _seed_work(db, code=101)
    res = await client.get("/api/works/101")
    assert isinstance(res.json()["marker_width_meters"], (int, float))
    assert res.json()["marker_width_meters"] == 0.21


async def test_nullable_fields_return_null(client: AsyncClient, db):
    await _seed_work(
        db, code=102, artist=None, image_url=None, ar_asset_url=None,
        marker_width_meters=None, media_url=None,
        summary_description_i18n={}, detail_description_i18n={},
        description_i18n={},
    )
    res = await client.get("/api/works/102")
    assert res.status_code == 200
    b = res.json()
    assert b["artist"] is None
    assert b["ar_asset_url"] is None
    assert b["marker_width_meters"] is None
    assert b["media_url"] is None
    assert b["summary_description"] is None
    assert b["detail_description"] is None


async def test_not_found_404(client: AsyncClient, db):
    res = await client.get("/api/works/999999")
    assert res.status_code == 404
    assert res.json()["detail"] == "Artwork not found"


async def test_invalid_id_422(client: AsyncClient):
    res = await client.get("/api/works/abc")
    assert res.status_code == 422


async def test_lang_param(client: AsyncClient, db):
    await _seed_work(db, code=103)
    res_en = await client.get("/api/works/103?lang=en")
    assert res_en.json()["title"] == "Waves"
    # ja → jp 매핑 (해당 키 없으면 ko 폴백)
    res_ja = await client.get("/api/works/103?lang=ja")
    assert res_ja.status_code == 200


async def test_default_lang_is_korean(client: AsyncClient, db):
    await _seed_work(db, code=104)
    res = await client.get("/api/works/104")
    assert res.json()["title"] == "파도와 기억"
    assert res.json()["summary_description"] == "짧은 설명"


async def test_summary_falls_back_to_description(client: AsyncClient, db):
    await _seed_work(db, code=105, summary_description_i18n={})
    res = await client.get("/api/works/105")
    assert res.json()["summary_description"] == "기본 설명"


async def test_api_health(client: AsyncClient):
    res = await client.get("/api/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"
