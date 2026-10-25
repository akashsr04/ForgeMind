from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    APP_ENV: str = "development"
    APP_NAME: str = "ForgeMind"
    API_V1_PREFIX: str = "/api/v1"
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Database
    DATABASE_URL: str = "sqlite:///forgemind.db"

    # Qdrant Vector Store
    QDRANT_URL: str = "memory"
    QDRANT_COLLECTION: str = "forgemind_maintenance"

    # Frontend Origin
    FRONTEND_ORIGIN: str = "http://localhost:5173"

    # ML & Embedding
    EMBEDDING_MODEL_NAME: str = "sentence-transformers/all-MiniLM-L6-v2"
    RANDOM_SEED: int = 42
    DEMO_MODE: bool = True

    # Optional LLM
    LLM_PROVIDER: str = "none"
    LLM_BASE_URL: Optional[str] = None
    LLM_MODEL: Optional[str] = None


@lru_cache()
def get_settings() -> Settings:
    return Settings()
