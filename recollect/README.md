# Recollect — backend (v1 observation layer)

FastAPI backend, per the Architecture Spine (`regarding the app/architecture/architecture-recollect-2026-09-08/ARCHITECTURE-SPINE.md`).

## Layout

```
src/recollect/core/      domain entities, rules, ports — depends on nothing
src/recollect/app/       use cases (enrol, ingest, compose weekly, read window)
src/recollect/adapters/  postgres, LLM, STT/TTS, notify — depend on core
src/recollect/edge/api/  FastAPI app + mock frontend (throwaway)
src/recollect/edge/device/  Raspberry Pi agent (later)
tests/                   pytest, incl. architecture tests (AD-2 egress, AD-3 direction)
```

## Run

```bash
uv sync                 # or: pip install -e ".[dev]"
uvicorn edge.api.main:app --reload
```

Open http://127.0.0.1:8000/ for the mock frontend and http://127.0.0.1:8000/docs for Swagger.

## Test

```bash
pytest
```

## Mock frontend

`edge/api/static/` is a throwaway mock so backend features can be exercised before
the Next.js app exists (built by dawn and kaiyi). It only calls the API — it owns
no data or logic. Delete it when the real frontend lands; the API contract is unchanged.

## Epics

See `regarding the app/epics.md` for the epic/story breakdown and owners.
