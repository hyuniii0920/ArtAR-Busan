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
    GCS_BUCKET: str = "artar-busan-assets"  # 비공개 (증빙 proofs/ 등)
    # 작품·테마 이미지 등 공개 자원 (allUsers read). signed PUT로 업로드, public URL로 조회
    GCS_PUBLIC_BUCKET: str = "artar-busan-public"

    # CORS
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
