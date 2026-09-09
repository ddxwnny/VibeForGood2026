"""
Delivery-layer middleware: security headers, per-IP rate limiting, and
structured request logging (api-standards: observability, security-standards:
rate limiting / security headers).

Everything here is framework-native (Starlette `BaseHTTPMiddleware`) so no extra
dependency is introduced. The rate limiter is intentionally an in-memory sliding
window — adequate for a single process (dev / single-Replica deploy). For a
multi-instance deployment swap the `_RateLimiter` storage for Redis (the
security-standards note: in-memory counters multiply across instances).

Security headers mirror the Helmet defaults called for in security-standards;
CSP is kept permissive-by-default for the static mock frontend but is applied
explicitly (never omitted), and can be tightened per environment.
"""

from __future__ import annotations

import json
import logging
import time
from collections import defaultdict, deque
from typing import Awaitable, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("recollect.access")


class _RateLimiter:
    """In-memory sliding-window limiter keyed by (route, client IP)."""

    def __init__(self) -> None:
        self._windows: dict[tuple[str, str], deque[float]] = defaultdict(deque)

    def hit(self, key: tuple[str, str], limit: int, window_seconds: float) -> tuple[bool, float]:
        now = time.monotonic()
        bucket = self._windows[key]
        while bucket and now - bucket[0] > window_seconds:
            bucket.popleft()
        bucket.append(now)
        if len(bucket) > limit:
            return True, window_seconds
        return False, 0.0

    def reset(self) -> None:
        self._windows.clear()


_limiter = _RateLimiter()


# (limit, window_seconds) budget keyed by a route prefix matcher. Auth-ish and
# enrolment/chat endpoints get the tightest budgets; general API traffic gets the
# default API budget (security-standards: auth 10/15min, general 100/min).
_RATE_RULES: list[tuple[str, int, float]] = [
    ("/v1/enrolments", 10, 900),        # auth/enrolment: 10 per 15 min
    ("/v1/seniors/", 30, 60),            # chat + telemetry write paths: 30/min
    ("/v1/", 100, 60),                   # general API: 100/min (default)
]


def _budget_for(path: str) -> tuple[int, float] | None:
    for prefix, limit, window in _RATE_RULES:
        if prefix in path or (prefix.endswith("/") and path.startswith(prefix)):
            return limit, window
    return None


_SECURITY_HEADERS: dict[str, str] = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "no-referrer",
    "X-Permitted-Cross-Domain-Policies": "none",
    "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
    # CSP is applied explicitly on every response; the static mock frontend is
    # self-contained (inline module script) so 'self' must allow inline script.
    "Content-Security-Policy": (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data:; "
        "connect-src 'self'; "
        "font-src 'self' data:; "
        "object-src 'none'; "
        "base-uri 'self'; "
        "frame-ancestors 'none'"
    ),
}


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Applies the security-header set to every response."""

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        response = await call_next(request)
        for name, value in _SECURITY_HEADERS.items():
            response.headers.setdefault(name, value)
        # HSTS is gated to production/TLS (security-standards: "HSTS in production").
        settings = request.app.state.settings
        if settings.hsts_enabled:
            response.headers.setdefault(
                "Strict-Transport-Security",
                f"max-age={settings.hsts_max_age}; includeSubDomains",
            )
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Enforces per-IP rate limits and returns the shared error envelope on 429."""

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        budget = _budget_for(request.url.path)
        if budget is not None:
            limit, window = budget
            client_ip = request.client.host if request.client else "unknown"
            blocked, retry_after = _limiter.hit((request.url.path, client_ip), limit, window)
            if blocked:
                return Response(
                    content=json.dumps(
                        {
                            "error": {
                                "code": "RATE_LIMITED",
                                "message": "Too many requests. Slow down and retry shortly.",
                                "details": {"limit": limit, "window_seconds": int(window)},
                            }
                        }
                    ),
                    status_code=429,
                    media_type="application/json",
                    headers={"Retry-After": str(int(retry_after))},
                )
        return await call_next(request)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Structured access log with a propagated request_id (api-standards: observability)."""

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        start = time.perf_counter()
        response = await call_next(request)
        latency_ms = round((time.perf_counter() - start) * 1000, 2)
        request_id = response.headers.get("X-Request-Id", "-")
        # Never log query strings (they may contain PII/tokens).
        path = request.url.path
        client_ip = request.client.host if request.client else "-"
        logger.info(
            "request",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": path,
                "status": response.status_code,
                "latency_ms": latency_ms,
                "client_ip": client_ip,
            },
        )
        return response
