from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    ENV: str = "development"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://artar:artar@localhost:5432/artar"

    # Auth
    JWT_SECRET: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_HOURS: int = 24
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD_HASH: str = ""

    # SUPER_ADMIN 시드 (DB users 테이블에 1계정 생성)
    SUPER_ADMIN_EMAIL: str = "admin@artar.local"

    # GCS
    GCS_BUCKET: str = "artar-busan-assets"

    # QR/딥링크용 공개 API base URL (프로덕션은 Cloud Run URL을 환경변수로 주입)
    PUBLIC_API_BASE_URL: str = "http://localhost:8080"

    # CORS
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
