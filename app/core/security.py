"""api key auth and in-memory rate limiting for write endpoints."""

from __future__ import annotations

from collections import defaultdict, deque
from threading import Lock
from time import time

from fastapi import HTTPException, Request, Security, status
from fastapi.security import APIKeyHeader

from app.core.config import get_settings

_hits: defaultdict[str, deque[float]] = defaultdict(deque)
_lock = Lock()
api_key_header = APIKeyHeader(
    name="X-API-Key",
    auto_error=False,
    description="Required for all write operations (POST, PUT, DELETE).",
)


def _error_payload(code: str, message: str) -> dict[str, dict[str, str]]:
    return {"error": {"code": code, "message": message}}


def reset_rate_limiter_state() -> None:
    with _lock:
        _hits.clear()


def require_write_access(
    request: Request,
    x_api_key: str | None = Security(api_key_header),
) -> None:
    settings = get_settings()

    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=_error_payload("API_KEY_MISSING", "Missing X-API-Key header."),
        )

    if x_api_key != settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=_error_payload("API_KEY_INVALID", "Invalid API key."),
        )

    now = time()
    window = max(1, settings.rate_limit_window_seconds)
    limit = max(1, settings.rate_limit_max_requests)
    key = f"{x_api_key}:{request.url.path}"

    with _lock:
        bucket = _hits[key]
        cutoff = now - window
        while bucket and bucket[0] <= cutoff:
            bucket.popleft()

        if len(bucket) >= limit:
            retry_after = int(max(1, window - (now - bucket[0])))
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=_error_payload("RATE_LIMIT_EXCEEDED", "Too many requests. Try again later."),
                headers={"Retry-After": str(retry_after)},
            )

        bucket.append(now)
