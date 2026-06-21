"""장소(미술관/문화공간) 시드 — 안드로이드 더미 8개 (멱등).

이미지는 public 버킷(artar-busan-public/images/)에 이미 업로드된 파일을 가리킨다
(scripts/upload_venue_images.py 참고).

사용:
    python -m scripts.seed_places
"""

import asyncio

from sqlalchemy import select

from app.database import async_session
from app.models import Place

IMAGE_BASE = "https://storage.googleapis.com/artar-busan-public/images"

PLACES = [
    {
        "id": 1,
        "title": "부산현대미술관",
        "category": "해운대구",
        "location": "부산 해운대구 APEC로 58",
        "hours": "10:00 – 18:00 (월요일 휴관)",
        "fee": "무료 관람",
        "phone": "051-278-2345",
        "description": (
            "부산의 현대미술을 대표하는 공간으로, 국내외 현대미술 작품을 상설 및 "
            "기획 전시합니다. 을숙도 생태공원과 맞닿아 있어 자연과 예술을 동시에 "
            "즐길 수 있습니다."
        ),
        "image": "museum_busan_moca.jpg",
    },
    {
        "id": 2,
        "title": "F1963",
        "category": "수영구",
        "location": "부산 수영구 구락로 123번길 20",
        "hours": "10:00 – 19:00 (연중무휴)",
        "fee": "무료 (일부 전시 유료)",
        "phone": "051-756-1963",
        "description": (
            "고려제강 수영공장을 리모델링한 복합문화공간입니다. 도서관, 전시장, "
            "카페, 공연장 등 다양한 문화 시설을 갖추고 있습니다."
        ),
        "image": "museum_f1963.jpg",
    },
    {
        "id": 3,
        "title": "부산시립미술관",
        "category": "해운대구",
        "location": "부산 해운대구 APEC로 58",
        "hours": "10:00 – 18:00 (월요일 휴관)",
        "fee": "성인 1,000원 / 청소년 600원",
        "phone": "051-744-2602",
        "description": (
            "부산의 대표 시립미술관으로, 근현대 미술 작품을 소장·전시합니다. "
            "다양한 기획 전시와 교육 프로그램을 운영하며 부산 미술 문화의 중심지 "
            "역할을 합니다."
        ),
        "image": "museum_busan_art.jpg",
    },
    {
        "id": 4,
        "title": "고은사진미술관",
        "category": "해운대구",
        "location": "부산 해운대구 해운대해변로 264",
        "hours": "10:00 – 18:00 (월요일 휴관)",
        "fee": "성인 5,000원 / 학생 3,000원",
        "phone": "051-746-0055",
        "description": (
            "국내 최초의 사진 전문 미술관으로, 국내외 사진 작가들의 작품을 "
            "전시합니다. 사진 예술의 역사와 현대적 트렌드를 탐색할 수 있는 "
            "공간입니다."
        ),
        "image": "museum_goeun_photo.jpg",
    },
    {
        "id": 5,
        "title": "아르떼뮤지엄 부산",
        "category": "영도구",
        "location": "부산 영도구 해양로 301번길 25",
        "hours": "10:00 – 20:00 (연중무휴)",
        "fee": "성인 17,000원 / 아동 13,000원",
        "phone": "1800-1467",
        "description": (
            "몰입형 미디어 아트를 경험할 수 있는 공간으로, 빛과 소리를 활용한 "
            "대형 인터랙티브 전시를 선보입니다. 자연을 모티프로 한 환상적인 "
            "디지털 아트 세계를 만날 수 있습니다."
        ),
        "image": "museum_arte_busan.jpg",
    },
    {
        "id": 6,
        "title": "부산근대역사관",
        "category": "중구",
        "location": "부산 중구 대청로 104",
        "hours": "09:00 – 18:00 (월요일 휴관)",
        "fee": "무료 관람",
        "phone": "051-253-3845",
        "description": (
            "부산의 근대 역사를 담은 박물관으로, 개항기부터 현대까지의 부산 역사와 "
            "문화를 전시합니다. 일제강점기 동양척식주식회사 부산지점 건물을 "
            "활용하였습니다."
        ),
        "image": "museum_modern_history.jpg",
    },
    {
        "id": 7,
        "title": "민주공원",
        "category": "중구",
        "location": "부산 중구 민주공원길 19",
        "hours": "09:00 – 18:00 (월요일 휴관)",
        "fee": "무료 관람",
        "phone": "051-790-7400",
        "description": (
            "부산 민주화운동의 역사를 기리는 공원으로, 민주항쟁기념관과 야외 "
            "공원으로 구성되어 있습니다. 부산의 민주화 운동 역사를 체험하고 배울 "
            "수 있습니다."
        ),
        "image": "museum_democracy_park.jpg",
    },
    {
        "id": 8,
        "title": "금정문화회관",
        "category": "금정구",
        "location": "부산 금정구 중앙대로 1777",
        "hours": "09:00 – 18:00 (월요일 휴관)",
        "fee": "전시별 상이",
        "phone": "051-519-5252",
        "description": (
            "금정구의 대표 문화 공간으로, 전시, 공연, 교육 등 다양한 문화 "
            "프로그램을 운영합니다. 지역 작가들의 작품을 발굴·소개하는 기획 전시를 "
            "정기적으로 진행합니다."
        ),
        "image": "museum_geumjeong_culture.jpg",
    },
]


async def seed() -> None:
    async with async_session() as session:
        added = 0
        for p in PLACES:
            existing = await session.execute(select(Place).where(Place.id == p["id"]))
            if existing.scalar_one_or_none():
                continue
            session.add(
                Place(
                    id=p["id"],
                    title=p["title"],
                    category=p["category"],
                    location=p["location"],
                    hours=p["hours"],
                    fee=p["fee"],
                    phone=p["phone"],
                    description=p["description"],
                    image_url=f"{IMAGE_BASE}/{p['image']}",
                    is_active=True,
                    sort_order=p["id"],
                )
            )
            added += 1
        await session.commit()
        print(f"장소 시드 완료: {added}개 추가 (총 {len(PLACES)}개 정의)")


if __name__ == "__main__":
    asyncio.run(seed())
