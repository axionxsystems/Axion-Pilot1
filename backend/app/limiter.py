import hashlib

from slowapi import Limiter
from slowapi.util import get_remote_address
from starlette.requests import Request

# ── Shared Application Limiter ────────────────────────────────────────────────
# Use a unified instance across all routers so limit states are tracked correctly.
limiter = Limiter(key_func=get_remote_address)


def user_or_ip_key(request: Request) -> str:
    """Rate-limit key for authenticated endpoints.

    Keys on a hash of the bearer token (so each user/token gets its own budget)
    and falls back to the client IP for unauthenticated callers. Hashing avoids
    keeping raw tokens in the limiter's in-memory/redis state.
    """
    auth = request.headers.get("Authorization", "")
    if auth.lower().startswith("bearer "):
        token = auth[7:].strip()
        if token:
            return "user:" + hashlib.sha256(token.encode()).hexdigest()[:32]
    return "ip:" + get_remote_address(request)
