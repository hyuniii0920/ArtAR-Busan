from httpx import AsyncClient

EVENT_PAYLOAD = {
    "name": "E",
    "slug": "e2",
    "start_date": "2026-03-01",
    "end_date": "2026-04-01",
    "is_public": True,
    "exhibition_hall_name": "전시관",
    "location": "부산",
    "organizer_name": "운영사무국",
}

VENUE_PAYLOAD = {
    "name_i18n": {"ko": "v"},
    "lat": 35.16,
    "lng": 129.13,
}

ARTWORK_PAYLOAD = {
    "title_i18n": {"ko": "작품"},
    "description_i18n": {"ko": "설명"},
    "artist": "홍길동",
    "marker_image_url": "https://example.com/marker.png",
    "media_url": "https://example.com/media.mp4",
    "media_type": "video",
    "sort_order": 0,
    "is_active": True,
}


async def _create_venue(client: AsyncClient, auth_headers: dict) -> str:
    e = await client.post(
        "/api/v1/admin/events", json=EVENT_PAYLOAD, headers=auth_headers
    )
    event_id = e.json()["data"]["id"]
    v = await client.post(
        f"/api/v1/admin/events/{event_id}/venues",
        json=VENUE_PAYLOAD,
        headers=auth_headers,
    )
    return v.json()["data"]["id"]


async def test_create_and_get_artwork(client: AsyncClient, auth_headers: dict):
    venue_id = await _create_venue(client, auth_headers)

    res = await client.post(
        f"/api/v1/admin/venues/{venue_id}/artworks",
        json=ARTWORK_PAYLOAD,
        headers=auth_headers,
    )
    assert res.status_code == 201
    artwork_id = res.json()["data"]["id"]

    res = await client.get(
        f"/api/v1/admin/artworks/{artwork_id}", headers=auth_headers
    )
    assert res.status_code == 200
    assert res.json()["data"]["media_type"] == "video"


async def test_code_auto_assigned_for_qr(client: AsyncClient, auth_headers: dict):
    """작품 생성 시 QR용 정수 code가 101부터 순차 자동 채번된다."""
    venue_id = await _create_venue(client, auth_headers)

    first = await client.post(
        f"/api/v1/admin/venues/{venue_id}/artworks",
        json=ARTWORK_PAYLOAD,
        headers=auth_headers,
    )
    second = await client.post(
        f"/api/v1/admin/venues/{venue_id}/artworks",
        json=ARTWORK_PAYLOAD,
        headers=auth_headers,
    )

    assert first.json()["data"]["code"] == 101
    assert second.json()["data"]["code"] == 102
    # QR에 담을 딥링크 URL이 code 기반으로 함께 내려온다
    assert first.json()["data"]["qr_url"].endswith("/api/works/101")


async def test_invalid_media_type_returns_422(
    client: AsyncClient, auth_headers: dict
):
    venue_id = await _create_venue(client, auth_headers)

    payload = {**ARTWORK_PAYLOAD, "media_type": "hologram"}
    res = await client.post(
        f"/api/v1/admin/venues/{venue_id}/artworks",
        json=payload,
        headers=auth_headers,
    )
    assert res.status_code == 422


async def test_invalid_url_pattern_returns_422(
    client: AsyncClient, auth_headers: dict
):
    venue_id = await _create_venue(client, auth_headers)

    payload = {**ARTWORK_PAYLOAD, "media_url": "not-a-url"}
    res = await client.post(
        f"/api/v1/admin/venues/{venue_id}/artworks",
        json=payload,
        headers=auth_headers,
    )
    assert res.status_code == 422
