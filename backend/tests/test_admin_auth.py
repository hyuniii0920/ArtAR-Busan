from httpx import AsyncClient

from tests.conftest import TEST_PASSWORD


async def test_login_success_returns_token_and_user(
    client: AsyncClient, super_admin
):
    res = await client.post(
        "/api/v1/admin/auth/login",
        json={"username": "super@test.local", "password": TEST_PASSWORD},
    )
    assert res.status_code == 200
    body = res.json()
    assert body["token_type"] == "bearer"
    assert len(body["access_token"]) > 20
    assert body["user"]["email"] == "super@test.local"
    assert body["user"]["role"] == "SUPER_ADMIN"
    assert "password_hash" not in body["user"]


async def test_login_wrong_password(client: AsyncClient, super_admin):
    res = await client.post(
        "/api/v1/admin/auth/login",
        json={"username": "super@test.local", "password": "wrong"},
    )
    assert res.status_code == 401
    assert res.json()["error"]["code"] == "INVALID_CREDENTIALS"


async def test_login_unknown_email(client: AsyncClient):
    res = await client.post(
        "/api/v1/admin/auth/login",
        json={"username": "nobody@test.local", "password": TEST_PASSWORD},
    )
    assert res.status_code == 401
    assert res.json()["error"]["code"] == "INVALID_CREDENTIALS"


async def test_me_returns_current_user(
    client: AsyncClient, museum_user, museum_headers: dict
):
    res = await client.get("/api/v1/admin/auth/me", headers=museum_headers)
    assert res.status_code == 200
    data = res.json()["data"]
    assert data["email"] == "museum@test.local"
    assert data["role"] == "MUSEUM"
    assert data["museum_status"] == "PENDING_MUSEUM"


async def test_me_without_token_returns_401(client: AsyncClient):
    res = await client.get("/api/v1/admin/auth/me")
    assert res.status_code == 401
    assert res.json()["error"]["code"] == "NOT_LOGGED_IN"


async def test_protected_admin_endpoint_without_token(client: AsyncClient):
    res = await client.get("/api/v1/admin/events")
    assert res.status_code == 401
