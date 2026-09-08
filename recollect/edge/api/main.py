"""FastAPI application.

Minimal scaffold. Real endpoints land story-by-story; the append-only
observation log and its write-path consent gate come with Epic 1 and 2.
"""

from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="Recollect", version="0.1.0")


@app.get("/api/health")
async def health() -> dict:
    return {"status": "ok"}


# Mock frontend (throwaway). Serves edge/api/static/ at "/" so backend features
# can be exercised before the Next.js app exists (built by dawn and kaiyi).
# Delete this mount when the real frontend lands — the API contract is unchanged.
_static_dir = Path(__file__).parent / "static"
app.mount("/", StaticFiles(directory=_static_dir, html=True), name="mock")
