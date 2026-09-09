"""FastAPI application.

Builds adapters from configuration, registers the versioned v1 API, and keeps
the throwaway mock static frontend at "/" so backend features can be exercised
before the Next.js surfaces land (built by dawn and kaiyi).
"""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from recollect.edge.api.container import build_store
from recollect.edge.api.errors import register_exception_handlers
from recollect.edge.api.middleware import (
    RateLimitMiddleware,
    RequestLoggingMiddleware,
    SecurityHeadersMiddleware,
)
from recollect.edge.api.routes import router as v1_router
from recollect.edge.api.settings import Settings, require_real_services


@asynccontextmanager
async def lifespan(app: FastAPI):
    engine = getattr(app.state.store, "engine", None)
    if engine is not None:
        from recollect.adapters.postgres.models import Base
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    settings = getattr(app.state, "settings", None)
    should_seed = getattr(settings, "seed_demo_data", True) if settings is not None else True
    if should_seed:
        try:
            from recollect.edge.api.demo_seed import seed_demo_seniors_if_empty
            await seed_demo_seniors_if_empty(app.state.store)
        except Exception as exc:
            import logging
            logging.getLogger(__name__).warning("Demo seed skipped: %s", exc)
    yield


app = FastAPI(title="Recollect", version="0.1.0", lifespan=lifespan)

# Build adapters from configuration. Real services are used when configured;
# a non-dev environment fails to boot if any required service is missing.
_settings = Settings()
require_real_services(_settings)
app.state.settings = _settings
app.state.store = build_store(_settings)

# --- CORS: explicit allowlist (api-standards: never "*" in production) ---
# allow_credentials is only safe alongside an explicit origin list.
_origins = _settings.cors_origin_list
app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins or ["*"],
    allow_credentials=False if (_origins and "*" in _origins) else bool(_origins),
    allow_methods=["GET", "POST", "HEAD", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

# --- Security headers, rate limiting, structured access logging ---
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(RequestLoggingMiddleware)

register_exception_handlers(app)

app.include_router(v1_router)


@app.get("/api/health")
async def health() -> dict:
    return {"status": "ok"}


# Serve frontend assets: prefer project root frontend/ if available, fallback to static/
_frontend_dir = Path(__file__).resolve().parents[5] / "frontend"
_static_dir = _frontend_dir if _frontend_dir.is_dir() else (Path(__file__).parent / "static")
app.mount("/", StaticFiles(directory=_static_dir, html=True), name="frontend")
