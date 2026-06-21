from pydantic import BaseModel


class WorkResponse(BaseModel):
    """Android 앱 전용 작품 응답 (snake_case, 평탄 구조).

    id는 Artwork.code(정수). 설명/제목은 lang에 맞춰 로컬라이즈된 문자열.
    """

    id: int
    title: str
    artist: str | None = None
    summary_description: str | None = None
    detail_description: str | None = None
    image_url: str | None = None
    ar_asset_url: str | None = None
    marker_image_url: str | None = None
    marker_width_meters: float | None = None
    media_url: str | None = None
