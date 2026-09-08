"""FastAPI application.

Minimal scaffold. Real endpoints land story-by-story; the append-only
observation log and its write-path consent gate come with Epic 1 and 2.
"""

from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from recollect.edge.api.container import build_store
from recollect.edge.api.routes import router
from recollect.edge.api.settings import Settings, require_real_services

app = FastAPI(title="Recollect", version="0.1.0")

# Build adapters from configuration. Real services are used when configured;
# a non-dev environment fails to boot if any required service is missing.
_settings = Settings()
require_real_services(_settings)
app.state.store = build_store(_settings)

app.include_router(router)


@app.get("/api/health")
async def health() -> dict:
    return {"status": "ok"}


# Mock frontend (throwaway). Serves edge/api/static/ at "/" so backend features
# can be exercised before the Next.js app exists (built by dawn and kaiyi).
# Delete this mount when the real frontend lands — the API contract is unchanged.
_static_dir = Path(__file__).parent / "static"
app.mount("/", StaticFiles(directory=_static_dir, html=True), name="mock")
