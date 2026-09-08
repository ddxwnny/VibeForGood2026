"""PostgreSQL adapter package — SQLAlchemy models and the append-only log."""

from recollect.adapters.postgres.models import Base
from recollect.adapters.postgres.observation_log import PostgresObservationLog

__all__ = ["Base", "PostgresObservationLog"]
