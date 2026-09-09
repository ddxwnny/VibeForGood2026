# Recollect — Database Tier

This directory manages the relational database persistence, schema migrations, and local containerized database services for the Recollect application.

## Structure

```text
database/
├── alembic.ini          # Alembic migration configuration
├── docker-compose.yml   # Local PostgreSQL service container
├── migrations/          # Schema versions and environment scripts
│   ├── env.py
│   ├── script.py.mako
│   └── versions/        # Migration steps
│       ├── 0001_initial.py
│       └── 0002_heartbeats_grants.py
└── README.md            # This documentation
```

## Supported Databases

1. **SQLite (Development & Serverless default)**:
   - Zero-configuration embedded database.
   - For serverless runtimes (like Vercel), the database is automatically replicated to `/tmp/recollect_local.db` with read-write capabilities.
   - Connection URL: `sqlite+aiosqlite:///recollect_local.db`

2. **PostgreSQL (Production & Containerized Local)**:
   - Production relational store with asyncpg driver.
   - Connection URL format: `postgresql+asyncpg://user:password@host:5432/dbname`

## Running Local PostgreSQL

Start the local PostgreSQL container using Docker Compose:

```bash
docker compose -f database/docker-compose.yml up -d
```

## Running Migrations

To apply the latest database migrations:

```bash
# Using uv from backend environment
uv run --directory backend alembic -c database/alembic.ini upgrade head
```

To create a new migration after updating models in `backend/src/recollect/adapters/postgres/models.py`:

```bash
uv run --directory backend alembic -c database/alembic.ini revision --autogenerate -m "describe changes"
```
