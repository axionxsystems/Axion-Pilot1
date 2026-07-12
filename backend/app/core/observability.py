"""
Observability: structured logging, request-id correlation, and optional Sentry.

Call ``setup_logging()`` and ``init_sentry()`` once at startup, and add
``RequestIDMiddleware`` so every log line and error can be correlated to a
single request via an ``X-Request-ID`` header.
"""
import json
import logging
import sys
import uuid
from contextvars import ContextVar

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.core.config import settings

# Holds the current request id so log records can pick it up without threading
# it through every function call.
request_id_ctx: ContextVar[str] = ContextVar("request_id", default="-")


class _RequestIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_ctx.get()
        return True


class _JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": getattr(record, "request_id", "-"),
            "time": self.formatTime(record, "%Y-%m-%dT%H:%M:%S%z"),
        }
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(payload)


def setup_logging() -> None:
    """Configure the root logger. JSON in prod (or when LOG_JSON=true), else text."""
    root = logging.getLogger()
    root.setLevel(settings.LOG_LEVEL.upper())

    # Replace any existing handlers so we don't double-log.
    for h in list(root.handlers):
        root.removeHandler(h)

    handler = logging.StreamHandler(sys.stdout)
    handler.addFilter(_RequestIdFilter())

    if settings.LOG_JSON or settings.is_production:
        handler.setFormatter(_JsonFormatter())
    else:
        handler.setFormatter(logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | [%(request_id)s] | %(message)s"
        ))

    root.addHandler(handler)


def init_sentry() -> None:
    """Initialize Sentry if SENTRY_DSN is set and the SDK is installed. No-op otherwise."""
    if not settings.SENTRY_DSN:
        return
    try:
        import sentry_sdk
        from sentry_sdk.integrations.fastapi import FastApiIntegration
        from sentry_sdk.integrations.starlette import StarletteIntegration
    except ImportError:
        logging.getLogger(__name__).warning(
            "SENTRY_DSN is set but sentry-sdk is not installed; skipping Sentry init."
        )
        return

    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment=settings.ENV,
        integrations=[StarletteIntegration(), FastApiIntegration()],
        traces_sample_rate=0.1,
        send_default_pii=False,
    )


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Attach an X-Request-ID to every request/response for log correlation."""

    async def dispatch(self, request: Request, call_next):
        req_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex
        token = request_id_ctx.set(req_id)
        try:
            response = await call_next(request)
        finally:
            request_id_ctx.reset(token)
        response.headers["X-Request-ID"] = req_id
        return response
