from httpx import AsyncClient

REGISTER_FORM = {
    "email": "newmuseum@test.local",
    "password": "secret123",
    "museum_name": "신규미술관",
    "contact": "010-1234-5678",
}


async def test_register_museum_success(client: AsyncClient):
    res = await client.post(
        "/api/v1/admin/auth/register-museum", data=REGISTER_FORM
    )
    assert res.status_code == 201
    data = res.json()["data"]
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "newmuseum@test.local"
    assert data["user"]["role"] == "MUSEUM"
    assert data["user"]["museum_status"] == "PENDING_MUSEUM"
    assert "password_hash" not in data["user"]


async def test_register_duplicate_email(client: AsyncClient):
    await client.post("/api/v1/admin/auth/register-museum", data=REGISTER_FORM)
    res = await client.post(
        "/api/v1/admin/auth/register-museum", data=REGISTER_FORM
    )
    assert res.status_code == 409
    assert res.json()["error"]["code"] == "EMAIL_ALREADY_EXISTS"


async def test_register_missing_email(client: AsyncClient):
    form = {**REGISTER_FORM, "email": ""}
    res = await client.post("/api/v1/admin/auth/register-museum", data=form)
    assert res.status_code == 422
    assert res.json()["error"]["code"] == "EMAIL_REQUIRED"


async def test_register_missing_museum_name(client: AsyncClient):
    form = {**REGISTER_FORM, "museum_name": ""}
    res = await client.post("/api/v1/admin/auth/register-museum", data=form)
    assert res.status_code == 422
    assert res.json()["error"]["code"] == "MUSEUM_NAME_REQUIRED"


async def test_register_invalid_email_format(client: AsyncClient):
    form = {**REGISTER_FORM, "email": "not-an-email"}
    res = await client.post("/api/v1/admin/auth/register-museum", data=form)
    assert res.status_code == 422
    assert res.json()["error"]["code"] == "INVALID_PAYLOAD"


async def test_registered_museum_can_login(client: AsyncClient):
    await client.post("/api/v1/admin/auth/register-museum", data=REGISTER_FORM)
    res = await client.post(
        "/api/v1/admin/auth/login",
        json={"username": REGISTER_FORM["email"], "password": REGISTER_FORM["password"]},
    )
    assert res.status_code == 200
    assert res.json()["user"]["museum_status"] == "PENDING_MUSEUM"


async def test_resubmit_updates_info_and_sets_pending(
    client: AsyncClient, museum_user, museum_headers: dict
):
    res = await client.patch(
        "/api/v1/admin/auth/museum-application/resubmit",
        data={"museum_name": "수정된미술관", "contact": "010-9999-8888"},
        headers=museum_headers,
    )
    assert res.status_code == 200
    data = res.json()["data"]
    assert data["museum_status"] == "PENDING_MUSEUM"
    assert data["museum_name"] == "수정된미술관"
    assert data["contact"] == "010-9999-8888"


async def test_resubmit_requires_museum_role(
    client: AsyncClient, super_admin, auth_headers: dict
):
    res = await client.patch(
        "/api/v1/admin/auth/museum-application/resubmit",
        data={"museum_name": "x", "contact": "y"},
        headers=auth_headers,
    )
    assert res.status_code == 400
    assert res.json()["error"]["code"] == "NOT_MUSEUM"


# --- Super Admin 관리 ---


async def test_list_museums_requires_super_admin(
    client: AsyncClient, museum_user, museum_headers: dict
):
    res = await client.get("/api/v1/admin/museums", headers=museum_headers)
    assert res.status_code == 403
    assert res.json()["error"]["code"] == "FORBIDDEN"


async def test_list_museums(
    client: AsyncClient, super_admin, museum_user, auth_headers: dict
):
    res = await client.get("/api/v1/admin/museums", headers=auth_headers)
    assert res.status_code == 200
    body = res.json()
    assert body["meta"]["total"] == 1  # super_admin은 제외, museum_user만
    assert body["data"][0]["email"] == "museum@test.local"


async def test_list_museums_status_filter(
    client: AsyncClient, super_admin, museum_user, auth_headers: dict
):
    res = await client.get(
        "/api/v1/admin/museums?status=APPROVED_MUSEUM", headers=auth_headers
    )
    assert res.status_code == 200
    assert res.json()["meta"]["total"] == 0  # museum_user는 PENDING


async def test_approve_museum(
    client: AsyncClient, super_admin, museum_user, auth_headers: dict
):
    res = await client.patch(
        f"/api/v1/admin/museums/{museum_user.id}/status",
        json={"museum_status": "APPROVED_MUSEUM"},
        headers=auth_headers,
    )
    assert res.status_code == 200
    assert res.json()["data"]["museum_status"] == "APPROVED_MUSEUM"


async def test_status_update_unknown_user(
    client: AsyncClient, super_admin, auth_headers: dict
):
    res = await client.patch(
        "/api/v1/admin/museums/00000000-0000-0000-0000-000000000000/status",
        json={"museum_status": "APPROVED_MUSEUM"},
        headers=auth_headers,
    )
    assert res.status_code == 404
    assert res.json()["error"]["code"] == "USER_NOT_FOUND"


async def test_update_museum_info(
    client: AsyncClient, super_admin, museum_user, auth_headers: dict
):
    res = await client.patch(
        f"/api/v1/admin/museums/{museum_user.id}",
        data={"museum_name": "관리자수정", "contact": "010-1111-2222"},
        headers=auth_headers,
    )
    assert res.status_code == 200
    assert res.json()["data"]["museum_name"] == "관리자수정"


async def test_delete_museum(
    client: AsyncClient, super_admin, museum_user, auth_headers: dict
):
    res = await client.delete(
        f"/api/v1/admin/museums/{museum_user.id}", headers=auth_headers
    )
    assert res.status_code == 200
    assert res.json()["data"]["ok"] is True

    # 삭제 확인
    res = await client.get("/api/v1/admin/museums", headers=auth_headers)
    assert res.json()["meta"]["total"] == 0
