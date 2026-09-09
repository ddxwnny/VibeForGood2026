"""FastAPI application.

Builds adapters from configuration, registers the versioned v1 API, and keeps
the throwaway mock static frontend at "/" so backend features can be exercised
before the Next.js surfaces land (built by dawn and kaiyi).
"""

from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from recollect.edge.api.container import build_store
from recollect.edge.api.routes import router as v1_router
from recollect.edge.api.settings import Settings, require_real_services

app = FastAPI(title="Recollect", version="0.1.0")

# Build adapters from configuration. Real services are used when configured;
# a non-dev environment fails to boot if any required service is missing.
_settings = Settings()
require_real_services(_settings)
app.state.settings = _settings
app.state.store = build_store(_settings)

app.include_router(v1_router)


@app.get("/api/health")
async def health() -> dict:
    return {"status": "ok"}


# Mock frontend (throwaway). Serves edge/api/static/ at "/" so backend features
# can be exercised before the Next.js app exists. Delete this mount when the
# real frontend lands - the v1 API contract is unchanged.
_static_dir = Path(__file__).parent / "static"
app.mount("/", StaticFiles(directory=_static_dir, html=True), name="mock")
