from httpx import AsyncClient

PLACE_PAYLOAD = {
    "title": "부산현대미술관",
    "category": "해운대구",
    "location": "부산 해운대구 APEC로 58",
    "hours": "10:00 – 18:00 (월요일 휴관)",
    "fee": "무료 관람",
    "phone": "051-278-2345",
    "description": "부산의 현대미술을 대표하는 공간입니다.",
    "imageUrl": "https://storage.googleapis.com/artar-busan-public/images/museum_busan_moca.jpg",
}


async def test_create_and_get_place(client: AsyncClient, auth_headers: dict):
    res = await client.post(
        "/api/v1/admin/places", json=PLACE_PAYLOAD, headers=auth_headers
    )
    assert res.status_code == 201
    data = res.json()["data"]
    assert data["imageUrl"] == PLACE_PAYLOAD["imageUrl"]  # camelCase 입출력
    place_id = data["id"]

    got = await client.get(
        f"/api/v1/admin/places/{place_id}", headers=auth_headers
    )
    assert got.status_code == 200
    assert got.json()["data"]["title"] == "부산현대미술관"


async def test_missing_required_field_returns_422(
    client: AsyncClient, auth_headers: dict
):
    payload = {k: v for k, v in PLACE_PAYLOAD.items() if k != "title"}
    res = await client.post(
        "/api/v1/admin/places", json=payload, headers=auth_headers
    )
    assert res.status_code == 422


async def test_empty_required_field_returns_422(
    client: AsyncClient, auth_headers: dict
):
    res = await client.post(
        "/api/v1/admin/places",
        json={**PLACE_PAYLOAD, "title": ""},
        headers=auth_headers,
    )
    assert res.status_code == 422


async def test_update_place(client: AsyncClient, auth_headers: dict):
    created = await client.post(
        "/api/v1/admin/places", json=PLACE_PAYLOAD, headers=auth_headers
    )
    place_id = created.json()["data"]["id"]

    res = await client.put(
        f"/api/v1/admin/places/{place_id}",
        json={"fee": "성인 1,000원"},
        headers=auth_headers,
    )
    assert res.status_code == 200
    assert res.json()["data"]["fee"] == "성인 1,000원"


async def test_delete_place(client: AsyncClient, auth_headers: dict):
    created = await client.post(
        "/api/v1/admin/places", json=PLACE_PAYLOAD, headers=auth_headers
    )
    place_id = created.json()["data"]["id"]

    res = await client.delete(
        f"/api/v1/admin/places/{place_id}", headers=auth_headers
    )
    assert res.status_code == 204

    got = await client.get(
        f"/api/v1/admin/places/{place_id}", headers=auth_headers
    )
    assert got.status_code == 404


async def test_create_requires_auth(client: AsyncClient):
    res = await client.post("/api/v1/admin/places", json=PLACE_PAYLOAD)
    assert res.status_code in (401, 403)
