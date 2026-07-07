# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ArtAR Busan — 부산 문화행사용 공유 AR 앱 템플릿 플랫폼. 하나의 앱 구조에서 행사별 콘텐츠/테마를 교체하여 재사용하는 구조.

## Tech Stack

- **Backend**: FastAPI (Python 3.11), SQLAlchemy 2.0 (async), Alembic, Pydantic v2
- **Database**: PostgreSQL (Neon 관리형 서버리스, JSONB for i18n) — 2026-07 Cloud SQL에서 이전
- **Infrastructure**: GCP Cloud Run, GCS, GitHub Actions CI/CD + Neon(외부 Postgres)
- **Frontend** (별도 팀): Kotlin + ARCore (Android 관람객 앱), React + TypeScript (어드민 CMS)

## Repository Structure

```
backend/
├── app/
│   ├── main.py          # FastAPI 앱, CORS, rate limiting, lifespan, OpenAPI 메타데이터
│   ├── config.py        # pydantic-settings 환경변수
│   ├── database.py      # async SQLAlchemy 엔진/세션
│   ├── dependencies.py  # get_db, get_current_user/require_super_admin/get_current_admin (JWT)
│   ├── errors.py        # AppError + 핸들러 (code 포함 에러 응답)
│   ├── models/          # SQLAlchemy ORM (Event, EventTheme, Venue, Artwork, VisitLog, User)
│   ├── schemas/         # Pydantic 요청/응답 스키마
│   ├── api/v1/
│   │   ├── app/         # 모바일 공개 API (/api/v1/app/*)
│   │   └── admin/       # 어드민 인증 API (/api/v1/admin/*) — auth, events, venues, artworks, upload, stats, museums
│   ├── services/        # 비즈니스 로직 (gcs.py: signed URL + 직접 업로드)
│   └── utils/           # i18n 헬퍼 등
├── alembic/             # DB 마이그레이션
│   └── versions/        # 마이그레이션 파일들 (initial_schema, timestamps/visit_log 관계, users 테이블, event 상세필드, artwork android 필드 등)
├── scripts/
│   ├── seed.py          # 개발용 시드 데이터 (행사·장소·작품 샘플)
│   └── seed_superadmin.py  # SUPER_ADMIN 계정 시드 (멱등)
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

# SUPER_ADMIN 계정 시드 (ADMIN_PASSWORD_HASH/SUPER_ADMIN_EMAIL 환경변수 필요, 멱등)
cd backend && python -m scripts.seed_superadmin

# 로컬 서버 직접 실행 (Docker 없이)
cd backend && uvicorn app.main:app --reload --port 8080

# Cloud Run 수동 배포
cd backend && gcloud run deploy artar-backend --source=. --region=asia-northeast3

# 프로덕션 DB(Neon) 마이그레이션 — DATABASE_URL을 Neon 연결 문자열로 설정 후 실행
# (Secret Manager DATABASE_URL 값 사용, 형식: postgresql+asyncpg://...neon.tech/neondb?ssl=require)
cd backend && DATABASE_URL="<Neon 연결 문자열>" alembic upgrade head
```

## Deployment

- **Cloud Run**: `artar-backend` 서비스, `asia-northeast3` 리전
- **Database (Neon)**: 외부 관리형 서버리스 Postgres(AWS `ap-southeast-1` Singapore). Cloud Run은 `DATABASE_URL` 시크릿의 일반 TCP 연결(`postgresql+asyncpg://...neon.tech/neondb?ssl=require`, asyncpg는 `sslmode` 대신 `ssl` 쿼리 사용)로 접속. 2026-07 GCP 무료판 종료 대비 Cloud SQL에서 이전(비용 ₩0). 무료 티어라 유휴 시 오토서스펜드(첫 요청 콜드스타트 ~1s)
- **Cloud Storage**: `artar-busan-assets` 버킷, `asia-northeast3`. 객체 업로드는 PUT signed URL로만 진행 — 어드민 CMS origin은 버킷 CORS에 등록되어 있음
- **CI/CD**: `.github/workflows/deploy.yml` — main push 시 test → 자동 배포
- **인증**: Workload Identity Federation (`github-pool` / `github-provider`) → `github-deploy` 서비스 계정
- **시크릿**: GCP Secret Manager에 저장 (DATABASE_URL, JWT_SECRET, ADMIN_USERNAME, ADMIN_PASSWORD_HASH, GCS_BUCKET)
- **GitHub Secrets**: `WIF_PROVIDER`, `WIF_SERVICE_ACCOUNT` (`CLOUD_SQL_CONNECTION`은 Neon 이전으로 미사용)
- **Cloud Run runtime SA 권한**: 기본 Compute SA(`...-compute@developer.gserviceaccount.com`)에 `secretmanager.secretAccessor`, `iam.serviceAccountTokenCreator`(self), GCS 버킷 `storage.objectAdmin` 부여

## Architecture Decisions

- **API 구조**: `/api/v1/app/*` (모바일, 공개) + `/api/v1/admin/*` (CMS, JWT 인증) + `/api/works/{id}`·`/api/health` (Android 앱 전용 비버전 공개 API)
- **Android works API**: `GET /api/works/{id}` — id는 `Artwork.code`(정수 101+, UUID PK와 별개). 평탄 snake_case 응답(`summary_description`/`detail_description`/`image_url`/`ar_asset_url`/`marker_width_meters`), `?lang=ko|en|ja|zh`(기본 ko, ja→jp·zh→cn 매핑). 라우터는 `api/works.py`, 스키마는 `schemas/work.py`. 404 본문은 FastAPI 기본 `{"detail":...}`
- **i18n**: JSONB 컬럼 `{"ko":"...", "en":"...", "jp":"...", "cn":"..."}`, `utils/i18n.py`의 `localize()` 함수로 추출
- **인증**: DB `users` 테이블 기반 멀티 유저 + JWT (python-jose). role: `SUPER_ADMIN` / `MUSEUM`. JWT `sub`=user_id. `dependencies.py`의 `get_current_user`(User 반환)·`require_super_admin`·`get_current_admin`(기존 라우터 호환용, email 반환). 기존 환경변수 단일 관리자는 `scripts/seed_superadmin.py`로 SUPER_ADMIN 1계정으로 승계(이메일=`SUPER_ADMIN_EMAIL`, 비밀번호 해시=`ADMIN_PASSWORD_HASH` 재사용)
- **미술관 회원/승인**: 미술관은 `POST /admin/auth/register-museum`(비인증, multipart)로 가입 → `PENDING_MUSEUM`. SUPER_ADMIN이 `/admin/museums`에서 승인/거절/수정/삭제. 거절된 미술관은 `/admin/auth/museum-application/resubmit`로 재신청. `proof_file`은 비로그인 컨텍스트라 백엔드가 GCS에 직접 업로드(`services/gcs.py: upload_bytes`, `proofs/` 프리픽스)
- **에러 응답**: 신규 회원/승인 라우터는 `errors.py`의 `AppError`로 `{"success":false,"error":{"code","message"}}` 형태 반환(프론트 분기용). 기존 라우터는 FastAPI 기본 `HTTPException` 유지
- **데이터 계층**: Event → Venue → Artwork (물리적 장소 바인딩). Event는 CMS 편의를 위해 대표 전시관 정보(`exhibition_hall_name`, `location`, `organizer_name`, `memo`)를 컬럼으로 직접 보유 — 생성 시 앞 3개 필수, 응답에선 optional(기존 행 호환)
- **타임스탬프 정책**: CMS 편집 대상 엔티티(Event, EventTheme, Venue, Artwork)는 `models/base.py`의 `TimestampMixin`을 상속해 `created_at`/`updated_at`을 자동 관리. CMS의 마지막 수정일 노출/정렬에 사용
- **VisitLog 관계**: `event`/`venue`/`artwork` 모두 `ondelete=SET NULL`로 약하게 연결 — 참조 대상이 삭제돼도 통계 보존을 위해 로그는 남김. ORM 레벨에 양방향 `visit_logs` 역참조 정의(통계 쿼리에서 직관적 접근)
- **이미지 업로드**: GCS v4 PUT signed URL 방식 — 백엔드는 `POST /api/v1/admin/upload/signed-url`로 발급만 하고, 클라이언트가 GCS에 직접 PUT. Cloud Run runtime SA의 self-impersonation(`iam.serviceAccountTokenCreator` 셀프 부여)으로 서명. 구현은 `services/gcs.py`
- **비공개 파일 조회**: 버킷은 비공개. 증빙 문서(`proofs/`)는 SUPER_ADMIN이 `GET /admin/museums/{id}/proof-url`로 만료시간 있는 v4 GET signed URL을 발급받아 열람(`services/gcs.py: generate_signed_download_url`). 직접 public URL 접근은 AccessDenied
- **검증 정책**: Pydantic 스키마에서 도메인 제약 강제 — slug 패턴, HEX 색상, lat/lng 범위(`-90~90`/`-180~180`), `media_type` Literal(image/video/audio/model3d), URL `https?://` 패턴, Event `end_date >= start_date` model_validator. slug 중복은 라우터에서 409로 매핑
- **익명 체크인**: `device_hash` (SHA-256 + salt)로 PII 미저장
