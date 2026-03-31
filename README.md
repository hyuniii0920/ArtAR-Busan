# ArtAR Busan

부산 문화행사용 **공유 AR 앱 템플릿 플랫폼**.  
하나의 앱 구조에서 행사별 콘텐츠와 테마를 교체하여 재사용하는 구조입니다.

> Loop Lab Busan을 첫 번째 레퍼런스로, 부산비엔날레 · 페스티벌 시월 · 광안리 빛축제 등으로 확장을 목표합니다.

## 주요 기능

| 대상                    | 기능                                                                             |
| ----------------------- | -------------------------------------------------------------------------------- |
| **관람객 (Flutter 앱)** | 행사 선택, AR 작품 오버레이, 4개 언어(한/영/일/중), TTS 음성 안내, 스탬프 체크인 |
| **관리자 (React CMS)**  | 행사·장소·작품 등록, 테마 편집(색상/로고), 이미지 업로드, 방문 통계 대시보드     |
| **백엔드 (FastAPI)**    | REST API, 다국어 JSONB, 익명 방문 로그, JWT 인증, GCS 이미지 관리                |

## 기술 스택

| 레이어       | 기술                                                   |
| ------------ | ------------------------------------------------------ |
| 관람객 앱    | Flutter 3.x (Dart), ARCore/ARKit                       |
| 어드민 CMS   | React 18 + TypeScript                                  |
| 백엔드 API   | FastAPI (Python 3.11), SQLAlchemy 2.0 (async), Alembic |
| 데이터베이스 | PostgreSQL 15                                          |
| 인프라       | GCP Cloud Run, Cloud SQL, Cloud Storage                |
| CI/CD        | GitHub Actions                                         |

## 시스템 아키텍처

```
Flutter App (관람객)          React CMS (관리자)
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
```

- 다국어 필드는 JSONB: `{"ko":"...", "en":"...", "jp":"...", "cn":"..."}`
- 익명 체크인: `device_hash` (SHA-256 + salt), 개인식별정보 미저장

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

### 어드민 API (`/api/v1/admin/`) — JWT 인증

| Method | Endpoint                                  | 설명                     |
| ------ | ----------------------------------------- | ------------------------ |
| POST   | `/auth/login`                             | 관리자 로그인 → JWT 발급 |
| CRUD   | `/events`, `/events/{id}`                 | 행사 관리                |
| PUT    | `/events/{id}/theme`                      | 테마 편집                |
| CRUD   | `/events/{id}/venues`, `/venues/{id}`     | 장소 관리                |
| CRUD   | `/venues/{id}/artworks`, `/artworks/{id}` | 작품 관리                |
| POST   | `/upload/image`                           | 이미지 업로드 (GCS)      |
| GET    | `/stats/events/{id}/summary`              | 방문 통계                |
| GET    | `/stats/events/{id}/demographics`         | 언어/OS 분포             |

## 프론트엔드 팀 API 연동

- **Swagger UI**: http://localhost:8080/docs — 인터랙티브 API 테스트
- **ReDoc**: http://localhost:8080/redoc — 깔끔한 API 레퍼런스 문서
- **OpenAPI JSON**: http://localhost:8080/openapi.json — 코드 생성용 스키마

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
| Flutter (AR·구조)   | 팀원 2              |
| Flutter (UX·다국어) | 팀원 3              |
| **백엔드·인프라**   | **팀원 4 (박준우)** |
| 어드민 CMS          | 팀원 5              |

## 라이선스

본 프로젝트는 부산 소재 대학교 캡스톤디자인 과목의 일환으로 개발되었습니다.
