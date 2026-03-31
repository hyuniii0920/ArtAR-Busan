# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ArtAR Busan — 부산 문화행사용 공유 AR 앱 템플릿 플랫폼. 하나의 앱 구조에서 행사별 콘텐츠/테마를 교체하여 재사용하는 구조.

## Tech Stack

- **Backend**: FastAPI (Python 3.11), SQLAlchemy 2.0 (async), Alembic, Pydantic v2
- **Database**: PostgreSQL 15 (JSONB for i18n)
- **Infrastructure**: GCP Cloud Run, Cloud SQL, GCS, GitHub Actions CI/CD
- **Frontend** (별도 팀): Flutter (관람객 앱), React + TypeScript (어드민 CMS)

## Repository Structure

```
backend/
├── app/
│   ├── main.py          # FastAPI 앱, CORS, rate limiting, lifespan, OpenAPI 메타데이터
│   ├── config.py        # pydantic-settings 환경변수
│   ├── database.py      # async SQLAlchemy 엔진/세션
│   ├── dependencies.py  # get_db, get_current_admin (JWT)
│   ├── models/          # SQLAlchemy ORM (Event, EventTheme, Venue, Artwork, VisitLog)
│   ├── schemas/         # Pydantic 요청/응답 스키마
│   ├── api/v1/
│   │   ├── app/         # 모바일 공개 API (/api/v1/app/*)
│   │   └── admin/       # 어드민 인증 API (/api/v1/admin/*)
│   ├── services/        # 비즈니스 로직
│   └── utils/           # i18n 헬퍼 등
├── alembic/             # DB 마이그레이션
│   └── versions/        # 마이그레이션 파일 (initial_schema 포함)
├── scripts/
│   └── seed.py          # 개발용 시드 데이터 (행사·장소·작품 샘플)
├── tests/               # pytest-asyncio 테스트
├── Dockerfile
└── docker-compose.yml   # 로컬 개발 (PostgreSQL + FastAPI)
```

## Common Commands

```bash
# 로컬 개발 환경 실행
cd backend && docker compose up

# 의존성 설치 (로컬)
pip install -r backend/requirements-dev.txt

# 테스트 실행
cd backend && pytest -v

# 린트
cd backend && ruff check app/

# DB 마이그레이션 생성
cd backend && alembic revision --autogenerate -m "description"

# DB 마이그레이션 적용
cd backend && alembic upgrade head

# 시드 데이터 삽입 (DB 실행 중 필요)
cd backend && python -m scripts.seed

# 시드 데이터 초기화 후 재삽입
cd backend && python -m scripts.seed --reset

# 로컬 서버 직접 실행 (Docker 없이)
cd backend && uvicorn app.main:app --reload --port 8080
```

## Architecture Decisions

- **API 구조**: `/api/v1/app/*` (모바일, 공개) + `/api/v1/admin/*` (CMS, JWT 인증)
- **i18n**: JSONB 컬럼 `{"ko":"...", "en":"...", "jp":"...", "cn":"..."}`, `utils/i18n.py`의 `localize()` 함수로 추출
- **인증**: 환경변수 기반 단일 관리자 + JWT (python-jose), `dependencies.py`의 `get_current_admin`
- **데이터 계층**: Event → Venue → Artwork (물리적 장소 바인딩)
- **익명 체크인**: `device_hash` (SHA-256 + salt)로 PII 미저장
