from httpx import AsyncClient

from app.api.v1.admin import upload as upload_module
from app.services import gcs


async def test_signed_url_request_invalid_content_type(
    client: AsyncClient, auth_headers: dict
):
    res = await client.post(
        "/api/v1/admin/upload/signed-url",
        json={"filename": "x.jpg", "content_type": "application/x-msdownload"},
        headers=auth_headers,
    )
    assert res.status_code == 422


async def test_signed_url_request_empty_filename(
    client: AsyncClient, auth_headers: dict
):
    res = await client.post(
        "/api/v1/admin/upload/signed-url",
        json={"filename": "", "content_type": "image/jpeg"},
        headers=auth_headers,
    )
    assert res.status_code == 422


async def test_signed_url_returns_payload_when_gcs_available(
    client: AsyncClient, auth_headers: dict, monkeypatch
):
    def fake_generate(filename, content_type, expires_in_minutes=15):
        return {
            "upload_url": "https://storage.googleapis.com/_signed_/abc",
            "public_url": "https://storage.googleapis.com/artar-busan-assets/uploads/abc.jpg",
            "key": "uploads/abc.jpg",
            "content_type": content_type,
            "expires_in_minutes": expires_in_minutes,
        }

    monkeypatch.setattr(
        upload_module.gcs, "generate_signed_upload_url", fake_generate
    )

    res = await client.post(
        "/api/v1/admin/upload/signed-url",
        json={"filename": "photo.jpg", "content_type": "image/jpeg"},
        headers=auth_headers,
    )
    assert res.status_code == 200
    data = res.json()["data"]
    assert data["upload_url"].startswith("https://")
    assert data["key"].startswith("uploads/")
    assert data["content_type"] == "image/jpeg"


async def test_signed_url_unavailable_returns_503(
    client: AsyncClient, auth_headers: dict, monkeypatch
):
    def raise_runtime(*a, **kw):
        raise RuntimeError("no SA email")

    monkeypatch.setattr(
        upload_module.gcs, "generate_signed_upload_url", raise_runtime
    )

    res = await client.post(
        "/api/v1/admin/upload/signed-url",
        json={"filename": "photo.jpg", "content_type": "image/jpeg"},
        headers=auth_headers,
    )
    assert res.status_code == 503


async def test_legacy_upload_image_returns_410(
    client: AsyncClient, auth_headers: dict
):
    res = await client.post("/api/v1/admin/upload/image", headers=auth_headers)
    assert res.status_code == 410


async def test_signed_url_unauthenticated(client: AsyncClient):
    res = await client.post(
        "/api/v1/admin/upload/signed-url",
        json={"filename": "x.jpg", "content_type": "image/jpeg"},
    )
    assert res.status_code in (401, 403)


# 사용 안 하는 import 회피
_ = gcs
