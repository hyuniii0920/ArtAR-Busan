from httpx import AsyncClient

from tests.conftest import TEST_ADMIN_PASSWORD


async def test_login_success(client: AsyncClient):
    res = await client.post(
        "/api/v1/admin/auth/login",
        json={"username": "admin", "password": TEST_ADMIN_PASSWORD},
    )
    assert res.status_code == 200
    body = res.json()
    assert body["token_type"] == "bearer"
    assert isinstance(body["access_token"], str) and len(body["access_token"]) > 20


async def test_login_wrong_password(client: AsyncClient):
    res = await client.post(
        "/api/v1/admin/auth/login",
        json={"username": "admin", "password": "wrong"},
    )
    assert res.status_code == 401


async def test_login_wrong_username(client: AsyncClient):
    res = await client.post(
        "/api/v1/admin/auth/login",
        json={"username": "not-admin", "password": TEST_ADMIN_PASSWORD},
    )
    assert res.status_code == 401


async def test_protected_endpoint_without_token(client: AsyncClient):
    res = await client.get("/api/v1/admin/events")
    assert res.status_code in (401, 403)
