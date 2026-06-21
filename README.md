# ArtAR Busan

부산 문화행사용 **공유 AR 앱 템플릿 플랫폼**.  
하나의 앱 구조에서 행사별 콘텐츠와 테마를 교체하여 재사용하는 구조입니다.

> Loop Lab Busan을 첫 번째 레퍼런스로, 부산비엔날레 · 페스티벌 시월 · 광안리 빛축제 등으로 확장을 목표합니다.

## 주요 기능

| 대상                    | 기능                                                                             |
| ----------------------- | -------------------------------------------------------------------------------- |
| **관람객 (Android 앱)** | 행사 선택, AR 작품 오버레이, 4개 언어(한/영/일/중), TTS 음성 안내, 스탬프 체크인 |
| **관리자 (React CMS)**  | 행사·장소·작품 등록, 테마 편집(색상/로고), 이미지 업로드, 방문 통계 대시보드     |
| **백엔드 (FastAPI)**    | REST API, 다국어 JSONB, 익명 방문 로그, JWT 인증, GCS 이미지 관리                |

## 기술 스택

| 레이어       | 기술                                                   |
| ------------ | ------------------------------------------------------ |
| 관람객 앱    | Kotlin (Android), ARCore                               |
| 어드민 CMS   | React 18 + TypeScript                                  |
| 백엔드 API   | FastAPI (Python 3.11), SQLAlchemy 2.0 (async), Alembic |
| 데이터베이스 | PostgreSQL 15                                          |
| 인프라       | GCP Cloud Run, Cloud SQL, Cloud Storage                |
| CI/CD        | GitHub Actions                                         |

## 시스템 아키텍처

```
Android App (관람객)          React CMS (관리자)
       │                            │
       │  /api/v1/app/*             │  /api/v1/admin/*
       └────────┬───────────────────┘
                │
       ┌────────▼──────────┐
       │   GCP Cloud Run    │
       │   FastAPI Server   │
       └───┬──────────┬────┘
           │          │
    ┌──────▼──┐  ┌────▼──────────┐
    │Cloud SQL│  │Cloud Storage  │
    │Postgres │  │(이미지/마커)   │
    └─────────┘  └───────────────┘
```

## 데이터 모델

```
Event (행사)
 ├── EventTheme (테마: 색상, 로고, 앱명)  [1:1]
 ├── Venue (장소: 좌표, 다국어 설명)       [1:N]
 │    └── Artwork (작품: AR 마커, 미디어)   [1:N]
 └── VisitLog (익명 방문 로그)             [1:N]
        ↑ event/venue/artwork 모두 SET NULL로 약하게 참조
```

- 다국어 필드는 JSONB: `{"ko":"...", "en":"...", "jp":"...", "cn":"..."}`
- 익명 체크인: `device_hash` (SHA-256 + salt), 개인식별정보 미저장
- CMS 편집 엔티티(Event/EventTheme/Venue/Artwork)는 `created_at`/`updated_at` 자동 관리
- 참조 대상(Venue·Artwork 등)이 삭제되어도 VisitLog는 보존되어 통계 연속성 유지

## 시작하기

### 사전 요구사항

- Docker & Docker Compose
- Python 3.11+ (Docker 없이 실행 시)

### Docker로 실행 (권장)

```bash
cd backend
docker compose up
```

API 서버: http://localhost:8080
Swagger UI: http://localhost:8080/docs
ReDoc: http://localhost:8080/redoc

### 로컬 실행 (Docker 없이)

```bash
# PostgreSQL이 localhost:5432에서 실행 중이어야 합니다

cd backend
pip install -r requirements-dev.txt
cp .env.example .env    # 환경변수 설정

alembic upgrade head    # DB 마이그레이션
uvicorn app.main:app --reload --port 8080
```

### 시드 데이터

개발/테스트용 샘플 데이터(행사 2건, 장소 3건, 작품 6건)를 삽입합니다.

```bash
cd backend
python -m scripts.seed          # 삽입
python -m scripts.seed --reset  # 기존 데이터 삭제 후 재삽입
```

## API 구조

### 모바일 앱 API (`/api/v1/app/`) — 공개

| Method | Endpoint                     | 설명                    |
| ------ | ---------------------------- | ----------------------- |
| GET    | `/events`                    | 공개 진행 중 행사 목록  |
| GET    | `/events/{slug}`             | 행사 상세 + 테마        |
| GET    | `/events/{slug}/venues`      | 행사 장소 목록 (다국어) |
| GET    | `/venues/{id}/artworks`      | 장소별 작품 + AR 마커   |
| POST   | `/visits`                    | 익명 체크인 로그        |
| GET    | `/events/{slug}/visit-count` | 스탬프 진행도 조회      |

### Android 앱 전용 API (`/api/works/`) — 공개, 비버전

안드로이드 앱이 QR(작품 정수 ID)로 단일 작품을 조회하는 평탄(snake_case) 응답 엔드포인트입니다. 기존 `/api/v1/app/*`와 별개로 `/api/*`에 마운트됩니다.

| Method | Endpoint                 | 설명                                        |
| ------ | ------------------------ | ------------------------------------------- |
| GET    | `/api/works/{id}`        | 작품 단건 조회 (id=정수 `code`, 404 미존재) |
| GET    | `/api/health`            | 헬스 체크                                   |

- `id`는 `Artwork.code`(정수, 101+). 잘못된 형식은 422.
- `?lang=ko|en|ja|zh` 선택, 기본 `ko`. (`ja`→`jp`, `zh`→`cn`로 내부 매핑)
- 응답 필드: `id, title, artist, summary_description, detail_description, image_url, ar_asset_url, marker_image_url, marker_width_meters, media_url` (nullable은 `null`)
- 404 본문: `{"detail": "Artwork not found"}`

### 어드민 인증/계정 API (`/api/v1/admin/auth/`)

| Method | Endpoint                            | 인증        | 설명                                  |
| ------ | ----------------------------------- | ----------- | ------------------------------------- |
| POST   | `/auth/login`                       | 공개        | 로그인 → JWT + user 반환              |
| POST   | `/auth/register-museum`             | 공개        | 미술관 가입 신청 (multipart) → PENDING |
| GET    | `/auth/me`                          | 로그인      | 현재 사용자 정보 (role/status)        |
| PATCH  | `/auth/museum-application/resubmit` | MUSEUM      | 거절된 미술관 재신청 (multipart)      |

### 미술관 승인 관리 API (`/api/v1/admin/museums/`) — SUPER_ADMIN 전용

| Method | Endpoint                  | 설명                                    |
| ------ | ------------------------- | --------------------------------------- |
| GET    | `/museums`                | 미술관 목록 (status/q/page/per_page)    |
| PATCH  | `/museums/{id}/status`    | 승인/거절 (`museum_status` 변경)        |
| PATCH  | `/museums/{id}`           | 미술관 정보 수정 (multipart)            |
| DELETE | `/museums/{id}`           | 미술관 삭제 (증빙 파일도 정리)          |
| GET    | `/museums/{id}/proof-url` | 증빙 문서 조회용 signed URL (15분 만료) |

### 어드민 콘텐츠 API (`/api/v1/admin/`) — JWT 인증

| Method | Endpoint                                  | 설명                                |
| ------ | ----------------------------------------- | ----------------------------------- |
| CRUD   | `/events`, `/events/{id}`                 | 행사 관리 (전시관/주최/메모 포함)   |
| PUT    | `/events/{id}/theme`                      | 테마 upsert                         |
| CRUD   | `/events/{id}/venues`, `/venues/{id}`     | 장소 관리                           |
| CRUD   | `/venues/{id}/artworks`, `/artworks/{id}` | 작품 관리                           |
| POST   | `/upload/signed-url`                      | GCS PUT용 signed URL 발급           |
| GET    | `/stats/events/{id}/summary`              | 방문 통계                           |
| GET    | `/stats/events/{id}/demographics`         | 언어/OS 분포                        |

> 이전의 `POST /upload/image`(파일 직접 수신)는 410 Gone으로 응답합니다 — signed URL 흐름으로 마이그레이션하세요.

### 행사(Event) 필드

기본 필드(`name`, `slug`, `start_date`, `end_date`, `is_public`) 외에 CMS 편의를 위한 대표 전시관 정보를 Event에 직접 보유합니다.

| 필드 | 생성 시 | 비고 |
| --- | --- | --- |
| `exhibition_hall_name` | 필수 | 대표 전시관명 |
| `location` | 필수 | 주소/위치 |
| `organizer_name` | 필수 | 주최측명 |
| `memo` | 선택 | 운영 메모 |

- `end_date`는 `start_date` 이상, `slug` 중복 시 409. 목록/상세/수정 응답 모두 위 필드를 포함합니다(기존 행은 `null`일 수 있음).

### 인증/계정 모델

- DB `users` 테이블 기반. `role`은 `SUPER_ADMIN` / `MUSEUM`, `museum_status`는 `PENDING_MUSEUM` / `APPROVED_MUSEUM` / `REJECTED_MUSEUM` / `null`(super admin)
- 로그인 요청은 `{username, password}` 형식이며 `username`에 이메일을 넣습니다. 응답에 `user` 객체 포함 (`password_hash`는 절대 미노출)
- 프론트 라우팅: SUPER_ADMIN → `/super-admin`, MUSEUM+PENDING → `/waiting`, MUSEUM+APPROVED → `/cms`, MUSEUM+REJECTED → `/rejected`
- 신규 회원/승인 라우터의 에러는 `{ "success": false, "error": { "code", "message" } }` 형식 (code: `INVALID_CREDENTIALS`, `EMAIL_ALREADY_EXISTS`, `USER_NOT_FOUND`, `NOT_MUSEUM`, `NOT_LOGGED_IN`, `FORBIDDEN` 등)

### 이미지 업로드 흐름 (Signed URL 2단계)

```
1) CMS  → POST /api/v1/admin/upload/signed-url
         body:  { filename, content_type }
         resp:  { upload_url, public_url, key, content_type, expires_in_minutes }

2) CMS  → PUT  upload_url  (브라우저가 GCS에 직접 PUT, Content-Type 헤더 필수)

3) CMS  → PUT/POST  /admin/...  (받은 public_url을 artwork.media_url 등에 저장)
```

- `content_type`은 `image/jpeg | image/png | image/webp | image/gif`만 허용
- `upload_url` 만료시간 기본 15분
- 어드민 CMS origin은 GCS 버킷 CORS에 등록되어야 함 (현재 `localhost:3000`, `localhost:5173`)

### 검증 정책 (Pydantic)

| 필드 | 제약 |
| ---- | ---- |
| `Event.slug` | `^[a-z0-9-]+$`, 최대 100자, 중복 시 409 |
| `Event.end_date` | `start_date` 이상 |
| `EventTheme.primary_color` / `secondary_color` | `#RRGGBB` HEX |
| `EventTheme.logo_url` / `hero_image_url` | `https?://` 시작 URL |
| `Venue.lat` / `lng` | `-90~90` / `-180~180` |
| `Artwork.media_type` | `image | video | audio | model3d` |
| `Artwork.marker_image_url` / `media_url` | `https?://` 시작 URL |
| `sort_order` | `>= 0` |

## 배포 (GCP Cloud Run)

프로덕션 서버는 GCP Cloud Run + Cloud SQL에 배포되어 있습니다.

| 리소스         | 구성                                                      |
| -------------- | --------------------------------------------------------- |
| Cloud Run      | `artar-backend`, asia-northeast3 리전                     |
| Cloud SQL      | PostgreSQL 15 (`artar-db`), db-f1-micro                   |
| Cloud Storage  | `artar-busan-assets` 버킷, 어드민 CMS origin CORS 허용    |
| Secret Manager | DATABASE_URL, JWT_SECRET, ADMIN_USERNAME 등 5개 시크릿    |
| CI/CD          | GitHub Actions — main push 시 test → Cloud Run 자동 배포 |

### CI/CD 자동 배포

`backend/` 하위 파일을 수정하고 main에 push하면 자동으로 배포됩니다.

```
main push → Lint + Test → Cloud Run 배포
```

- **인증**: Workload Identity Federation (`github-pool`) → `github-deploy` 서비스 계정
- **시크릿**: GCP Secret Manager에서 Cloud Run으로 주입
- **GitHub Secrets**: `WIF_PROVIDER`, `WIF_SERVICE_ACCOUNT`, `CLOUD_SQL_CONNECTION`

### 수동 배포

```bash
cd backend
gcloud run deploy artar-backend --source=. --region=asia-northeast3
```

### 프로덕션 DB 마이그레이션

```bash
# 터미널 1: Cloud SQL Proxy 실행
cloud-sql-proxy artar-492707:asia-northeast3:artar-db --port=5433

# 터미널 2: 마이그레이션 적용
cd backend
DATABASE_URL=postgresql+asyncpg://artar:PASSWORD@localhost:5433/artar alembic upgrade head

# (최초 1회) SUPER_ADMIN 계정 시드 — ADMIN_PASSWORD_HASH/SUPER_ADMIN_EMAIL 환경변수 필요
DATABASE_URL=postgresql+asyncpg://artar:PASSWORD@localhost:5433/artar \
  ADMIN_PASSWORD_HASH='<bcrypt hash>' SUPER_ADMIN_EMAIL='admin@artar.local' \
  python -m scripts.seed_superadmin
```

## 프론트엔드 팀 API 연동

로컬 개발:

- **Swagger UI**: http://localhost:8080/docs
- **ReDoc**: http://localhost:8080/redoc
- **OpenAPI JSON**: http://localhost:8080/openapi.json

프로덕션 (Cloud Run 배포 URL):

- **Swagger UI**: `https://artar-backend-932907510949.asia-northeast3.run.app/docs`
- **ReDoc**: `https://artar-backend-932907510949.asia-northeast3.run.app/redoc`

모바일 앱 팀은 `/api/v1/app/*` 엔드포인트만 사용하며, `lang` 쿼리 파라미터로 다국어를 지정합니다 (`ko`, `en`, `jp`, `cn`).

## 개발 명령어

```bash
# 테스트
cd backend && pytest -v

# 린트
cd backend && ruff check app/

# DB 마이그레이션 생성
cd backend && alembic revision --autogenerate -m "description"

# DB 마이그레이션 적용
cd backend && alembic upgrade head

# 시드 데이터
cd backend && python -m scripts.seed --reset
```

## 환경변수

| 변수                  | 설명                    | 기본값                                                  |
| --------------------- | ----------------------- | ------------------------------------------------------- |
| `DATABASE_URL`        | PostgreSQL 연결 문자열  | `postgresql+asyncpg://artar:artar@localhost:5432/artar` |
| `JWT_SECRET`          | JWT 서명 키             | `change-me-in-production`                               |
| `ADMIN_USERNAME`      | 관리자 계정             | `admin`                                                 |
| `ADMIN_PASSWORD_HASH` | bcrypt 해시             | —                                                       |
| `GCS_BUCKET`          | GCS 버킷명              | `artar-busan-assets`                                    |
| `CORS_ORIGINS`        | 허용 오리진 (쉼표 구분) | `http://localhost:3000,http://localhost:5173`           |

## 팀 구성

| 역할                | 담당                |
| ------------------- | ------------------- |
| PM / 기획·데이터    | 팀원 1              |
| Android (AR·구조)   | 팀원 2              |
| Android (UX·다국어) | 팀원 3              |
| **백엔드·인프라**   | **팀원 4 (박준우)** |
| 어드민 CMS          | 팀원 5              |

## 라이선스

본 프로젝트는 부산 소재 대학교 캡스톤디자인 과목의 일환으로 개발되었습니다.
