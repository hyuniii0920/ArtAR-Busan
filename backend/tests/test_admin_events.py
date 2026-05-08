from httpx import AsyncClient

VALID_PAYLOAD = {
    "name": "Test Event",
    "slug": "test-event",
    "start_date": "2026-03-01",
    "end_date": "2026-04-01",
    "is_public": True,
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
    assert res.json()["data"]["slug"] == "test-event"


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
