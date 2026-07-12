"""
Centralized application configuration.

This is the single source of truth for every environment variable the backend
reads. Access it via the module-level ``settings`` singleton::

    from app.core.config import settings
    if settings.is_production:
        ...

Existing modules that still call ``os.environ.get`` directly keep working — this
object reads the same environment — but new code should prefer ``settings`` so
there is one documented, typed, validated place for configuration.
"""
from functools import lru_cache
from typing import List, Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # tolerate unrelated env vars
    )

    # ── Environment ───────────────────────────────────────────────────────────
    ENV: str = "development"

    # ── Auth / JWT ────────────────────────────────────────────────────────────
    SECRET_KEY: str = ""
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 days

    # ── Database ──────────────────────────────────────────────────────────────
    DATABASE_URL: str = ""

    # ── CORS ──────────────────────────────────────────────────────────────────
    # Comma-separated list, e.g. "https://app.example.com,https://example.com".
    ALLOWED_ORIGINS: str = ""

    # ── Redis / Celery ────────────────────────────────────────────────────────
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = ""
    CELERY_RESULT_BACKEND: str = ""

    # ── AI providers ──────────────────────────────────────────────────────────
    AI_PROVIDER: str = ""
    GROQ_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    OPENAI_API_KEY: str = ""

    # ── Stripe billing ────────────────────────────────────────────────────────
    STRIPE_SECRET_KEY: str = ""
    STRIPE_PUBLISHABLE_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""
    STRIPE_ENV: str = "test"

    # ── Email / SMTP ──────────────────────────────────────────────────────────
    EMAIL_USER: str = ""
    EMAIL_PASS: str = ""
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587

    # ── Code editor sandbox ───────────────────────────────────────────────────
    CODE_BASE_DIR: str = ""

    # ── Observability ─────────────────────────────────────────────────────────
    SENTRY_DSN: str = ""
    LOG_LEVEL: str = "INFO"
    LOG_JSON: bool = False  # emit structured JSON logs (recommended in prod)

    # ── Derived helpers ───────────────────────────────────────────────────────
    @property
    def is_production(self) -> bool:
        return self.ENV.lower() == "production"

    @property
    def allowed_origins_list(self) -> List[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",") if o.strip()]

    @property
    def broker_url(self) -> str:
        return self.CELERY_BROKER_URL or self.REDIS_URL

    @property
    def result_backend(self) -> str:
        return self.CELERY_RESULT_BACKEND or self.REDIS_URL

    def validate_production(self) -> None:
        """Fail fast at startup if a production deployment is misconfigured.

        Only enforced when ENV=production so local/dev runs stay frictionless.
        """
        if not self.is_production:
            return

        errors: list[str] = []

        if not self.SECRET_KEY or len(self.SECRET_KEY) < 32:
            errors.append("SECRET_KEY must be set and at least 32 characters in production")
        if not self.DATABASE_URL or self.DATABASE_URL.startswith("sqlite"):
            errors.append("DATABASE_URL must point to a production database (not SQLite)")
        if not self.allowed_origins_list:
            errors.append("ALLOWED_ORIGINS must be set (no wildcard CORS in production)")

        if errors:
            raise RuntimeError(
                "Invalid production configuration:\n  - " + "\n  - ".join(errors)
            )


@lru_cache
def get_settings() -> Settings:
    return Settings()


# Module-level singleton for convenient import.
settings = get_settings()
