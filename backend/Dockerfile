# Recollect v1 observation layer — FastAPI backend
# Multi-stage build: uv-managed, reproducible, non-root runtime.
# `require_real_services` in settings.py fails boot outside dev when required
# services aren't configured, so a container normally runs gated against
# RECOLLECT_* env vars rather than silently serving mocks.

# ---- Stage 1: build dependencies -------------------------------------------
FROM python:3.13-slim AS build

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=0

# uv pinned for reproducibility; bump deliberately.
COPY --from=ghcr.io/astral-sh/uv:0.5.28 /uv /uvx /bin/

WORKDIR /app

# Install only runtime deps first (cache-friendly: metadata changes rarely).
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-project

# ---- Stage 2: runtime ------------------------------------------------------
FROM python:3.13-slim AS runtime

RUN groupadd --system app && adduser --system --ingroup app app

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:0.5.28 /uv /uvx /bin/
COPY --from=build /app/.venv /app/.venv

# Project metadata + source. Install the local package non-editable so
# `recollect` is on the venv path without shipping the build toolchain.
COPY pyproject.toml uv.lock ./
COPY src ./src
COPY migrations ./migrations
COPY alembic.ini ./

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    RECOLLECT_ENVIRONMENT=production

USER app
EXPOSE 8000

CMD ["uvicorn", "recollect.edge.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
