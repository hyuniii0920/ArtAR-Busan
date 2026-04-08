from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.config import settings
from app.api.v1.router import api_v1_router
from app.rate_limit import limiter


# ── OpenAPI 태그 메타데이터 (Swagger UI 그룹핑) ──────────────
OPENAPI_TAGS = [
    {
        "name": "App - Events",
        "description": "모바일 앱용 행사 조회 API. 현재 공개 중인 행사 목록 및 상세 정보를 제공합니다.",
    },
    {
        "name": "App - Venues",
        "description": "모바일 앱용 장소 조회 API. 행사별 장소 목록과 작품 수를 반환합니다.",
    },
    {
        "name": "App - Artworks",
        "description": "모바일 앱용 작품 조회 API. 장소별 작품 목록을 다국어로 반환합니다.",
    },
    {
        "name": "App - Visits",
        "description": "방문 기록 API. 익명 체크인 기록 생성 및 방문 장소 수 조회를 제공합니다.",
    },
    {
        "name": "Admin - Auth",
        "description": "어드민 인증 API. JWT 토큰 발급을 처리합니다.",
    },
    {
        "name": "Admin - Events",
        "description": "어드민 행사 관리 API. 행사 CRUD 및 테마 설정을 제공합니다.",
    },
    {
        "name": "Admin - Venues",
        "description": "어드민 장소 관리 API. 행사별 장소 CRUD를 제공합니다.",
    },
    {
        "name": "Admin - Artworks",
        "description": "어드민 작품 관리 API. 장소별 작품 CRUD를 제공합니다.",
    },
    {
        "name": "Admin - Upload",
        "description": "어드민 파일 업로드 API. 이미지 업로드를 처리합니다.",
    },
    {
        "name": "Admin - Stats",
        "description": "어드민 통계 API. 행사별 방문 통계 및 인구통계를 제공합니다.",
    },
]


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    # Startup: DB 커넥션 풀 워밍업
    from app.database import engine

    async with engine.begin() as conn:
        pass  # 커넥션 테스트
    yield
    # Shutdown
    await engine.dispose()


app = FastAPI(
    title="ArtAR Busan API",
    description=(
        "## 부산 문화행사 공유 AR 앱 템플릿 플랫폼 백엔드\n\n"
        "하나의 앱 구조에서 행사별 콘텐츠/테마를 교체하여 재사용하는 구조입니다.\n\n"
        "### API 구조\n"
        "- **`/api/v1/app/*`** — 모바일 앱용 공개 API (인증 불필요)\n"
        "- **`/api/v1/admin/*`** — 어드민 CMS용 API (JWT Bearer 인증 필요)\n\n"
        "### 다국어 지원\n"
        "모바일 API에서 `lang` 쿼리 파라미터로 언어를 지정합니다: `ko`, `en`, `jp`, `cn`\n\n"
        "### 공통 응답 형식\n"
        "```json\n"
        '{ "success": true, "data": ..., "meta": { "total": 10, "page": 1, "per_page": 20 } }\n'
        "```"
    ),
    version="0.1.0",
    openapi_tags=OPENAPI_TAGS,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate Limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# Routers
app.include_router(api_v1_router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    return {"status": "ok"}

# GCP 배포용 포트 번호 설정
if __name__ == "__main__":
    import uvicorn
    # port를 8080으로 설정
    uvicorn.run(app, host="0.0.0.0", port=8080)
