from httpx import AsyncClient

BASE = {"title": "장소", "category": "해운대구", "location": "주소"}


async def _create(client: AsyncClient, headers: dict, **overrides) -> dict:
    res = await client.post(
        "/api/v1/admin/places", json={**BASE, **overrides}, headers=headers
    )
    assert res.status_code == 201
    return res.json()["data"]


async def test_list_museums_returns_camelcase_array(
    client: AsyncClient, auth_headers: dict
):
    await _create(
        client,
        auth_headers,
        title="부산현대미술관",
        imageUrl="https://storage.googleapis.com/artar-busan-public/images/museum_busan_moca.jpg",
    )

    res = await client.get("/api/museums")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list) and len(data) == 1
    item = data[0]
    # 안드로이드 규약: 순수 배열 + camelCase
    assert item["title"] == "부산현대미술관"
    assert item["imageUrl"].endswith("museum_busan_moca.jpg")
    assert item["isActive"] is True
    assert "image_url" not in item  # snake_case는 노출되지 않아야


async def test_inactive_place_excluded(client: AsyncClient, auth_headers: dict):
    await _create(client, auth_headers, title="공개장소", isActive=True, sortOrder=1)
    await _create(client, auth_headers, title="비공개장소", isActive=False, sortOrder=2)

    res = await client.get("/api/museums")
    assert [m["title"] for m in res.json()] == ["공개장소"]


async def test_get_museum_detail_and_404(client: AsyncClient, auth_headers: dict):
    created = await _create(client, auth_headers, title="민주공원")

    ok = await client.get(f"/api/museums/{created['id']}")
    assert ok.status_code == 200
    assert ok.json()["title"] == "민주공원"

    nf = await client.get("/api/museums/9999")
    assert nf.status_code == 404
