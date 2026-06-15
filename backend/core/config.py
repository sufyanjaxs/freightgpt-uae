from pydantic_settings import BaseSettings
from typing import Optional, List


class Settings(BaseSettings):
    APP_NAME: str = "FreightGPT UAE"
    VERSION: str = "1.0.0"
    DEBUG: bool = True
    ENV: str = "development"

    # Database - defaults to SQLite for free dev, switch to Postgres in prod
    DATABASE_URL: str = "sqlite+aiosqlite:///./freightgpt.db"
    DATABASE_URL_SYNC: str = "sqlite:///./freightgpt.db"
    REDIS_URL: Optional[str] = None  # Redis is optional, falls back to in-memory

    # Security
    SECRET_KEY: str = "freightgpt-dev-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # LLM - defaults to FREE Ollama with local models
    # No API keys needed! Install Ollama: https://ollama.ai
    OPENAI_API_KEY: Optional[str] = None  # Optional
    ANTHROPIC_API_KEY: Optional[str] = None  # Optional
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    LLM_ROUTER_MODEL: str = "ollama/qwen2.5"  # Using your local qwen model
    FALLBACK_LLM: str = "ollama/qwen2.5:1.5b"  # Fallback to smaller qwen

    # Vector DB - Qdrant is free and open-source
    QDRANT_URL: Optional[str] = None  # Optional, falls back to in-memory

    # Email - FREE: Use Gmail SMTP or Mailtrap (free tier)
    # No SendGrid required. Set these up for free:
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None  # Your free Gmail address
    SMTP_PASSWORD: Optional[str] = None  # Gmail app password

    # SMS/Voice - Optional, uses free mock service by default
    TWILIO_ACCOUNT_SID: Optional[str] = None
    TWILIO_AUTH_TOKEN: Optional[str] = None
    TWILIO_PHONE_NUMBER: Optional[str] = None

    # Storage - FREE: Local filesystem by default. No S3 needed.
    STORAGE_BACKEND: str = "local"  # "local" or "s3"
    UPLOAD_DIR: str = "./uploads"
    S3_BUCKET_NAME: Optional[str] = None

    # Maps - FREE: OpenStreetMap + Nominatim. No Google Maps API key needed.
    # Google Maps is optional, falls back to OSM
    GOOGLE_MAPS_API_KEY: Optional[str] = None
    OSM_USER_AGENT: str = "FreightGPT-UAE/1.0"

    # Monitoring
    SENTRY_DSN: Optional[str] = None
    LOG_LEVEL: str = "INFO"

    CORS_ORIGINS: List[str] = ["*"]

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
