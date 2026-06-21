"""
시드 데이터 스크립트 — 개발/테스트용 샘플 데이터 삽입.

사용법:
    cd backend
    python -m scripts.seed          # 삽입
    python -m scripts.seed --reset  # 기존 데이터 삭제 후 재삽입
"""

import argparse
import asyncio
import uuid
from datetime import date, datetime, timezone

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session, engine
from app.models import Artwork, Event, EventTheme, Venue, VisitLog  # noqa: F401


# ── 고정 UUID (테스트에서 재사용 가능) ──────────────────────────
EVENT_1_ID = uuid.UUID("a1000000-0000-0000-0000-000000000001")
EVENT_2_ID = uuid.UUID("a1000000-0000-0000-0000-000000000002")

VENUE_1_ID = uuid.UUID("b1000000-0000-0000-0000-000000000001")
VENUE_2_ID = uuid.UUID("b1000000-0000-0000-0000-000000000002")
VENUE_3_ID = uuid.UUID("b1000000-0000-0000-0000-000000000003")

ARTWORK_IDS = [
    uuid.UUID(f"c1000000-0000-0000-0000-00000000000{i}") for i in range(1, 7)
]

now = datetime.now(timezone.utc)


# ── 시드 데이터 정의 ──────────────────────────────────────────

def seed_events() -> list[Event]:
    return [
        Event(
            id=EVENT_1_ID,
            name="2026 부산비엔날레 AR 체험",
            slug="busan-biennale-2026",
            start_date=date(2026, 3, 1),
            end_date=date(2026, 6, 30),
            is_public=True,
            created_at=now,
            updated_at=now,
        ),
        Event(
            id=EVENT_2_ID,
            name="해운대 빛축제 AR",
            slug="haeundae-light-2026",
            start_date=date(2026, 12, 1),
            end_date=date(2027, 1, 31),
            is_public=False,
            created_at=now,
            updated_at=now,
        ),
    ]


def seed_themes() -> list[EventTheme]:
    return [
        EventTheme(
            id=uuid.uuid4(),
            event_id=EVENT_1_ID,
            primary_color="#1E3A5F",
            secondary_color="#F5A623",
            logo_url="https://storage.googleapis.com/artar-busan-assets/demo/logo-biennale.png",
            app_name="부산비엔날레 AR",
            font_family="Pretendard",
            hero_image_url="https://storage.googleapis.com/artar-busan-assets/demo/hero-biennale.jpg",
        ),
    ]


def seed_venues() -> list[Venue]:
    return [
        Venue(
            id=VENUE_1_ID,
            event_id=EVENT_1_ID,
            name_i18n={"ko": "부산시립미술관", "en": "Busan Museum of Art", "jp": "釜山市立美術館", "cn": "釜山市立美术馆"},
            lat=35.1631,
            lng=129.1306,
            description_i18n={
                "ko": "부산의 대표 현대미술관으로 다양한 기획전을 선보입니다.",
                "en": "Busan's leading contemporary art museum featuring diverse exhibitions.",
                "jp": "釜山を代表する現代美術館で、多様な企画展を開催しています。",
                "cn": "釜山代表性的当代美术馆，展出多种策划展览。",
            },
            address="부산광역시 해운대구 APEC로 58",
            sort_order=0,
            is_active=True,
        ),
        Venue(
            id=VENUE_2_ID,
            event_id=EVENT_1_ID,
            name_i18n={"ko": "F1963", "en": "F1963", "jp": "F1963", "cn": "F1963"},
            lat=35.1725,
            lng=129.0924,
            description_i18n={
                "ko": "고려제강 수영공장을 리모델링한 복합문화공간입니다.",
                "en": "A cultural complex renovated from a former steel wire factory.",
                "jp": "高麗製鋼の工場をリモデリングした複合文化空間です。",
                "cn": "由高丽制钢水泳工厂改建的综合文化空间。",
            },
            address="부산광역시 수영구 구락로 123번길 20",
            sort_order=1,
            is_active=True,
        ),
        Venue(
            id=VENUE_3_ID,
            event_id=EVENT_1_ID,
            name_i18n={"ko": "감천문화마을", "en": "Gamcheon Culture Village", "jp": "甘川文化村", "cn": "甘川文化村"},
            lat=35.0975,
            lng=129.0108,
            description_i18n={
                "ko": "알록달록 계단식 마을로 유명한 부산 명소입니다.",
                "en": "A famous Busan attraction known for its colorful terraced houses.",
                "jp": "カラフルな階段状の村として有名な釜山の名所です。",
                "cn": "以色彩缤纷的阶梯式房屋而闻名的釜山景点。",
            },
            address="부산광역시 사하구 감내2로 203",
            sort_order=2,
            is_active=True,
        ),
    ]


def seed_artworks() -> list[Artwork]:
    return [
        # 부산시립미술관 작품들
        Artwork(
            id=ARTWORK_IDS[0],
            code=101,
            venue_id=VENUE_1_ID,
            title_i18n={"ko": "파도와 기억", "en": "Waves and Memory", "jp": "波と記憶", "cn": "波浪与记忆"},
            description_i18n={
                "ko": "부산 바다를 모티브로 한 인터랙티브 AR 설치작품입니다.",
                "en": "An interactive AR installation inspired by Busan's sea.",
                "jp": "釜山の海をモチーフにしたインタラクティブAR設置作品です。",
                "cn": "以釜山大海为主题的互动AR装置作品。",
            },
            summary_description_i18n={
                "ko": "작품 카드에 표시할 짧은 설명입니다.",
                "en": "A short description shown on the artwork card.",
                "jp": "作品カードに表示する短い説明です。",
                "cn": "显示在作品卡片上的简短说明。",
            },
            detail_description_i18n={
                "ko": "TTS와 상세 화면에 표시할 전체 작품 설명입니다.",
                "en": "Full description shown on the detail screen and read by TTS.",
                "jp": "TTSと詳細画面に表示する全体の作品説明です。",
                "cn": "在详情页面显示并由TTS朗读的完整作品说明。",
            },
            artist="홍길동",
            image_url="https://storage.googleapis.com/artar-busan-assets/demo/artwork-101.jpg",
            marker_image_url="https://storage.googleapis.com/artar-busan-assets/demo/marker-waves.png",
            marker_width_meters=0.21,
            media_url="https://storage.googleapis.com/artar-busan-assets/demo/media-waves.mp4",
            media_type="video",
            sort_order=0,
            is_active=True,
            created_at=now,
        ),
        Artwork(
            id=ARTWORK_IDS[1],
            code=102,
            venue_id=VENUE_1_ID,
            title_i18n={"ko": "도시의 숨결", "en": "Breath of the City", "jp": "都市の息吹", "cn": "城市的呼吸"},
            description_i18n={
                "ko": "부산의 도시 풍경을 AR로 재해석한 작품입니다.",
                "en": "A reinterpretation of Busan's cityscape through AR.",
                "jp": "釜山の都市景観をARで再解釈した作品です。",
                "cn": "通过AR重新诠释釜山城市风景的作品。",
            },
            artist="이도윤",
            image_url="https://storage.googleapis.com/artar-busan-assets/demo/artwork-102.jpg",
            marker_image_url="https://storage.googleapis.com/artar-busan-assets/demo/marker-city.png",
            marker_width_meters=0.18,
            media_url="https://storage.googleapis.com/artar-busan-assets/demo/media-city.jpg",
            media_type="image",
            sort_order=1,
            is_active=True,
            created_at=now,
        ),
        # F1963 작품들
        Artwork(
            id=ARTWORK_IDS[2],
            code=103,
            venue_id=VENUE_2_ID,
            title_i18n={"ko": "철의 꽃", "en": "Iron Bloom", "jp": "鉄の花", "cn": "铁之花"},
            description_i18n={
                "ko": "공장의 역사를 AR 꽃으로 피워내는 작품입니다.",
                "en": "An artwork that blooms the factory's history into AR flowers.",
                "jp": "工場の歴史をARの花で咲かせる作品です。",
                "cn": "将工厂历史化为AR花朵绽放的作品。",
            },
            artist="박서진",
            marker_image_url="https://storage.googleapis.com/artar-busan-assets/demo/marker-iron.png",
            media_url="https://storage.googleapis.com/artar-busan-assets/demo/media-iron.mp4",
            media_type="video",
            sort_order=0,
            is_active=True,
            created_at=now,
        ),
        Artwork(
            id=ARTWORK_IDS[3],
            code=104,
            venue_id=VENUE_2_ID,
            title_i18n={"ko": "시간의 층위", "en": "Layers of Time", "jp": "時間の層", "cn": "时间的层次"},
            description_i18n={
                "ko": "과거와 현재가 겹치는 AR 타임라인 체험입니다.",
                "en": "An AR timeline experience where past and present overlap.",
                "jp": "過去と現在が重なるARタイムライン体験です。",
                "cn": "过去与现在重叠的AR时间线体验。",
            },
            artist="정하늘",
            media_url="https://storage.googleapis.com/artar-busan-assets/demo/media-layers.jpg",
            media_type="image",
            sort_order=1,
            is_active=True,
            created_at=now,
        ),
        # 감천문화마을 작품들
        Artwork(
            id=ARTWORK_IDS[4],
            code=105,
            venue_id=VENUE_3_ID,
            title_i18n={"ko": "골목 이야기", "en": "Alley Stories", "jp": "路地の物語", "cn": "胡同故事"},
            description_i18n={
                "ko": "마을 골목에 숨겨진 이야기를 AR로 들려줍니다.",
                "en": "AR reveals hidden stories in the village alleys.",
                "jp": "村の路地に隠された物語をARで伝えます。",
                "cn": "通过AR讲述隐藏在村庄巷弄中的故事。",
            },
            artist="최민아",
            marker_image_url="https://storage.googleapis.com/artar-busan-assets/demo/marker-alley.png",
            media_url="https://storage.googleapis.com/artar-busan-assets/demo/media-alley.mp4",
            media_type="video",
            sort_order=0,
            is_active=True,
            created_at=now,
        ),
        Artwork(
            id=ARTWORK_IDS[5],
            code=106,
            venue_id=VENUE_3_ID,
            title_i18n={"ko": "색의 언덕", "en": "Hill of Colors", "jp": "色の丘", "cn": "色彩之丘"},
            description_i18n={
                "ko": "감천마을의 색채를 AR로 확장한 체험형 작품입니다.",
                "en": "An experiential AR work expanding Gamcheon's colors.",
                "jp": "甘川村の色彩をARで拡張した体験型作品です。",
                "cn": "将甘川村的色彩通过AR扩展的体验型作品。",
            },
            artist="한소율",
            media_url="https://storage.googleapis.com/artar-busan-assets/demo/media-hill.jpg",
            media_type="image",
            sort_order=1,
            is_active=True,
            created_at=now,
        ),
    ]


async def reset_data(session: AsyncSession) -> None:
    """모든 시드 테이블을 CASCADE 삭제."""
    for table in ("visit_log", "artwork", "venue", "event_theme", "event"):
        await session.execute(text(f"DELETE FROM {table}"))
    await session.commit()
    print("기존 데이터 삭제 완료")


async def insert_seed(session: AsyncSession) -> None:
    events = seed_events()
    themes = seed_themes()
    venues = seed_venues()
    artworks = seed_artworks()

    session.add_all(events)
    await session.flush()

    session.add_all(themes)
    session.add_all(venues)
    await session.flush()

    session.add_all(artworks)
    await session.commit()

    print(f"시드 삽입 완료: Event {len(events)}건, Theme {len(themes)}건, "
          f"Venue {len(venues)}건, Artwork {len(artworks)}건")


async def main(reset: bool = False) -> None:
    async with async_session() as session:
        if reset:
            await reset_data(session)
        await insert_seed(session)
    await engine.dispose()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ArtAR 시드 데이터")
    parser.add_argument("--reset", action="store_true", help="기존 데이터 삭제 후 재삽입")
    args = parser.parse_args()
    asyncio.run(main(reset=args.reset))
