from httpx import AsyncClient

VALID_PAYLOAD = {
    "name": "Test Event",
    "slug": "test-event",
    "start_date": "2026-03-01",
    "end_date": "2026-04-01",
    "is_public": True,
    "exhibition_hall_name": "부산시립미술관",
    "location": "부산 해운대구 APEC로 58",
    "organizer_name": "ArtAR 운영사무국",
    "memo": "현장 메모",
}


async def test_create_and_get_event(client: AsyncClient, auth_headers: dict):
    res = await client.post(
        "/api/v1/admin/events", json=VALID_PAYLOAD, headers=auth_headers
    )
    assert res.status_code == 201
    event_id = res.json()["data"]["id"]

    res = await client.get(
        f"/api/v1/admin/events/{event_id}", headers=auth_headers
    )
    assert res.status_code == 200
    data = res.json()["data"]
    assert data["slug"] == "test-event"
    assert data["exhibition_hall_name"] == "부산시립미술관"
    assert data["location"] == "부산 해운대구 APEC로 58"
    assert data["organizer_name"] == "ArtAR 운영사무국"
    assert data["memo"] == "현장 메모"


async def test_create_missing_exhibition_hall_returns_422(
    client: AsyncClient, auth_headers: dict
):
    payload = {k: v for k, v in VALID_PAYLOAD.items() if k != "exhibition_hall_name"}
    res = await client.post(
        "/api/v1/admin/events", json=payload, headers=auth_headers
    )
    assert res.status_code == 422


async def test_create_missing_organizer_returns_422(
    client: AsyncClient, auth_headers: dict
):
    payload = {k: v for k, v in VALID_PAYLOAD.items() if k != "organizer_name"}
    res = await client.post(
        "/api/v1/admin/events", json=payload, headers=auth_headers
    )
    assert res.status_code == 422


async def test_memo_is_optional(client: AsyncClient, auth_headers: dict):
    payload = {k: v for k, v in VALID_PAYLOAD.items() if k != "memo"}
    res = await client.post(
        "/api/v1/admin/events", json=payload, headers=auth_headers
    )
    assert res.status_code == 201
    assert res.json()["data"]["memo"] is None


async def test_update_event_detail_fields(client: AsyncClient, auth_headers: dict):
    create = await client.post(
        "/api/v1/admin/events", json=VALID_PAYLOAD, headers=auth_headers
    )
    event_id = create.json()["data"]["id"]

    res = await client.put(
        f"/api/v1/admin/events/{event_id}",
        json={"location": "수정된 위치", "memo": "수정 메모"},
        headers=auth_headers,
    )
    assert res.status_code == 200
    data = res.json()["data"]
    assert data["location"] == "수정된 위치"
    assert data["memo"] == "수정 메모"
    assert data["exhibition_hall_name"] == "부산시립미술관"  # 미변경 유지


async def test_list_includes_detail_fields(client: AsyncClient, auth_headers: dict):
    await client.post(
        "/api/v1/admin/events", json=VALID_PAYLOAD, headers=auth_headers
    )
    res = await client.get("/api/v1/admin/events?per_page=100", headers=auth_headers)
    assert res.status_code == 200
    item = res.json()["data"][0]
    assert item["exhibition_hall_name"] == "부산시립미술관"
    assert "updated_at" in item
    assert "venue_count" in item


async def test_create_duplicate_slug_returns_409(
    client: AsyncClient, auth_headers: dict
):
    await client.post(
        "/api/v1/admin/events", json=VALID_PAYLOAD, headers=auth_headers
    )
    res = await client.post(
        "/api/v1/admin/events", json=VALID_PAYLOAD, headers=auth_headers
    )
    assert res.status_code == 409


async def test_end_date_before_start_date_returns_422(
    client: AsyncClient, auth_headers: dict
):
    payload = {**VALID_PAYLOAD, "end_date": "2026-02-01"}
    res = await client.post(
        "/api/v1/admin/events", json=payload, headers=auth_headers
    )
    assert res.status_code == 422


async def test_invalid_slug_returns_422(client: AsyncClient, auth_headers: dict):
    payload = {**VALID_PAYLOAD, "slug": "Invalid Slug!"}
    res = await client.post(
        "/api/v1/admin/events", json=payload, headers=auth_headers
    )
    assert res.status_code == 422


async def test_update_event(client: AsyncClient, auth_headers: dict):
    create = await client.post(
        "/api/v1/admin/events", json=VALID_PAYLOAD, headers=auth_headers
    )
    event_id = create.json()["data"]["id"]

    res = await client.put(
        f"/api/v1/admin/events/{event_id}",
        json={"name": "Renamed"},
        headers=auth_headers,
    )
    assert res.status_code == 200
    assert res.json()["data"]["name"] == "Renamed"


async def test_delete_event(client: AsyncClient, auth_headers: dict):
    create = await client.post(
        "/api/v1/admin/events", json=VALID_PAYLOAD, headers=auth_headers
    )
    event_id = create.json()["data"]["id"]

    res = await client.delete(
        f"/api/v1/admin/events/{event_id}", headers=auth_headers
    )
    assert res.status_code == 204

    res = await client.get(
        f"/api/v1/admin/events/{event_id}", headers=auth_headers
    )
    assert res.status_code == 404


async def test_get_unknown_event_returns_404(
    client: AsyncClient, auth_headers: dict
):
    res = await client.get(
        "/api/v1/admin/events/00000000-0000-0000-0000-000000000000",
        headers=auth_headers,
    )
    assert res.status_code == 404
