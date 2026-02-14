"""Application settings loaded from environment variables."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Global application settings."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "FastAPI Scaffold"
    api_prefix: str = "/api/v1"

    database_url: str = "sqlite+aiosqlite:///./app.db"

    jwt_secret_key: str = Field(default="change-me-in-production", min_length=16)
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60

    google_client_ids: list[str] = Field(default_factory=list)
    google_issuer: str = "https://accounts.google.com"
    google_jwks_url: str = "https://www.googleapis.com/oauth2/v3/certs"


settings = Settings()
