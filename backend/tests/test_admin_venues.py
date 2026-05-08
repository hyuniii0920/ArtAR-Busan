from httpx import AsyncClient

EVENT_PAYLOAD = {
    "name": "E",
    "slug": "e1",
    "start_date": "2026-03-01",
    "end_date": "2026-04-01",
    "is_public": True,
}

VENUE_PAYLOAD = {
    "name_i18n": {"ko": "부산시립미술관", "en": "Busan Museum"},
    "lat": 35.16,
    "lng": 129.13,
    "description_i18n": {"ko": "설명", "en": "desc"},
    "address": "부산시 해운대구",
    "sort_order": 0,
    "is_active": True,
}


async def _create_event(client: AsyncClient, auth_headers: dict) -> str:
    res = await client.post(
        "/api/v1/admin/events", json=EVENT_PAYLOAD, headers=auth_headers
    )
    return res.json()["data"]["id"]


async def test_create_and_get_venue(client: AsyncClient, auth_headers: dict):
    event_id = await _create_event(client, auth_headers)

    res = await client.post(
        f"/api/v1/admin/events/{event_id}/venues",
        json=VENUE_PAYLOAD,
        headers=auth_headers,
    )
    assert res.status_code == 201
    venue_id = res.json()["data"]["id"]

    res = await client.get(
        f"/api/v1/admin/venues/{venue_id}", headers=auth_headers
    )
    assert res.status_code == 200
    assert res.json()["data"]["name_i18n"]["ko"] == "부산시립미술관"


async def test_create_venue_invalid_lat_returns_422(
    client: AsyncClient, auth_headers: dict
):
    event_id = await _create_event(client, auth_headers)

    payload = {**VENUE_PAYLOAD, "lat": 99.0}
    res = await client.post(
        f"/api/v1/admin/events/{event_id}/venues",
        json=payload,
        headers=auth_headers,
    )
    assert res.status_code == 422


async def test_create_venue_under_unknown_event_returns_404(
    client: AsyncClient, auth_headers: dict
):
    res = await client.post(
        "/api/v1/admin/events/00000000-0000-0000-0000-000000000000/venues",
        json=VENUE_PAYLOAD,
        headers=auth_headers,
    )
    assert res.status_code == 404
