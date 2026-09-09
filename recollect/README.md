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

## Deploy (Docker)

```bash
docker compose up --build      # API + PostgreSQL, real adapters
```

The API runs in `production` mode inside the container and refuses to boot
against mock data (`require_real_services`). Set the vendor secrets in `.env`
(copy `.env.example`).

## HTTP API

The production API is versioned under `/v1`. Response models are typed and
domain rule violations (`RecollectError`) map to HTTP 400.

Authentication (NFR-15): the senior never authenticates. Two callers do:

- **Device** — presents `RECOLLECT_DEVICE_API_KEY` as a bearer token to record
  heartbeats and addressed turns. Permissive in dev; enforced in production.
- **Phone surfaces** (care worker, named recipient) — present a per-grant API
  key resolved against the `grants` table (AD-7). Grants are minted
  out-of-band; senior-specific access is enforced per route.

Key endpoints:

| Method | Path | Purpose |
| --- | --- | --- |
| POST | `/v1/enrolments` | Care-worker enrolment (Epic 2) |
| POST | `/v1/device/heartbeat` | Device liveness (AD-6) |
| POST | `/v1/turns` | Addressed turn capture — device mints the Interaction (AD-14) |
| POST | `/v1/turns/unrecognised` | Gap(unrecognised) (AD-6) |
| POST | `/v1/seniors/{id}/observations` | Task/observation write (AD-1, AD-4) |
| GET  | `/v1/seniors/{id}/observations` | Windowed read model (AD-3) |
| GET  | `/v1/roster` | Fixed-order roster (AD-7, FR-29) |
| POST | `/v1/seniors/{id}/window` | Weekly window (AD-8, FR-15..20) |
| POST | `/v1/seniors/{id}/erase` | Crypto-shred erasure (AD-13) |
| POST | `/v1/device/instrument/decision` | Instrument scheduler (AD-9) |
| POST | `/v1/jobs/heartbeat-sweep` | Liveness sweep job (AD-6) |
| POST | `/v1/jobs/retention-sweep` | Raw-audio retention sweep (Story 7.1) |

## Mock frontend

`edge/api/static/` is a throwaway mock so backend features can be exercised before
the Next.js app exists (built by dawn and kaiyi). It only calls the API — it owns
no data or logic. Delete it when the real frontend lands; the v1 API contract is unchanged.

## Epics

See `regarding the app/epics.md` for the epic/story breakdown and owners.
