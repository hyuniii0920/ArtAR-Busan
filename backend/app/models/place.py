from sqlalchemy import Boolean, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.base import TimestampMixin


class Place(TimestampMixin, Base):
    """미술관/문화공간 장소 디렉토리.

    행사(Event)와 무관한 독립 엔티티. 안드로이드 앱이 정수 id로 조회하고
    CMS가 CRUD한다. 응답은 평탄 camelCase(`imageUrl` 등).
    """

    __tablename__ = "place"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200))  # 장소명 (필수)
    category: Mapped[str] = mapped_column(String(50))  # 지역구 (필수)
    location: Mapped[str] = mapped_column(String(500))  # 주소 (필수)
    hours: Mapped[str | None] = mapped_column(String(200), nullable=True)  # 운영 시간
    fee: Mapped[str | None] = mapped_column(String(200), nullable=True)  # 입장료
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)  # 문의 전화
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    image_url: Mapped[str | None] = mapped_column(Text, nullable=True)  # → imageUrl
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
