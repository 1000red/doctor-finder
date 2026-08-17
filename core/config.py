from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # App
    APP_NAME: str = "Doctor Finder"
    APP_VERSION: str = "1.0.0"

    # Database
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/eru_tawasol"

    # JWT
    SECRET_KEY: str = "change-this-to-a-very-long-random-secret-key-min-32-chars"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    RESET_TOKEN_EXPIRE_MINUTES: int = 10

    # SMTP
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str
    SMTP_PASSWORD: str
    FROM_EMAIL: str

    # # S3 / MinIO
    # S3_ENDPOINT_URL: str = ""          # empty = real AWS S3
    # S3_ACCESS_KEY: str = "minioadmin"
    # S3_SECRET_KEY: str = "minioadmin"
    # S3_BUCKET_NAME: str = "eru-tawasol"
    # S3_PUBLIC_BASE_URL: str = "http://localhost:9000/eru-tawasol"

    # OTP
    OTP_EXPIRE_MINUTES: int = 10

    GOOGLE_CLIENT_ID: str

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
