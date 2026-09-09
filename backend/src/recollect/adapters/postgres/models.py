"""
SQLAlchemy 2.0 ORM models for the append-only observation log (AD-1).

The same models run on PostgreSQL (asyncpg) in production and SQLite (aiosqlite)
in tests — JSON columns use a JSONB variant on Postgres and plain JSON on
SQLite. Every timestamp is stored UTC (AD-11); the adapter normalises reads to
timezone-aware UTC because SQLite returns naive datetimes.
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import JSON, DateTime, String, Text, Uuid
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

JSONType = JSON().with_variant(JSONB(), "postgresql")


class Base(DeclarativeBase):
    pass


class SeniorRow(Base):
    __tablename__ = "seniors"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    display_name: Mapped[str] = mapped_column(String(255))
    preferred_language: Mapped[str] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class EnrolmentRow(Base):
    __tablename__ = "enrolments"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    senior_id: Mapped[UUID] = mapped_column(Uuid, unique=True, index=True)
    enrolled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    artefacts: Mapped[list] = mapped_column(JSONType)          # list[str] of ConsentArtifactKind
    withdrawn_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class InteractionRow(Base):
    __tablename__ = "interactions"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    senior_id: Mapped[UUID] = mapped_column(Uuid, index=True)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    idempotency_key: Mapped[str] = mapped_column(String(255), unique=True, index=True)


class ObservationRow(Base):
    __tablename__ = "observations"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    senior_id: Mapped[UUID] = mapped_column(Uuid, index=True)
    interaction_id: Mapped[UUID] = mapped_column(Uuid, index=True)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    signal_type: Mapped[str] = mapped_column(String(64))
    item_variant: Mapped[str | None] = mapped_column(String(255), nullable=True)
    extraction_model_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    prompt_version: Mapped[str | None] = mapped_column(String(64), nullable=True)
    stt_model_version: Mapped[str | None] = mapped_column(String(64), nullable=True)
    content: Mapped[str] = mapped_column(Text)
    outcome: Mapped[str | None] = mapped_column(String(64), nullable=True)
    supersedes_id: Mapped[UUID | None] = mapped_column(Uuid, nullable=True)


class GapRow(Base):
    __tablename__ = "gaps"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    senior_id: Mapped[UUID] = mapped_column(Uuid, index=True)
    reason: Mapped[str] = mapped_column(String(64))
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class TombstoneRow(Base):
    __tablename__ = "tombstones"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    senior_id: Mapped[UUID] = mapped_column(Uuid, unique=True, index=True)
    reason: Mapped[str] = mapped_column(String(64))
    shredded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    stores_shredded: Mapped[list] = mapped_column(JSONType)     # list[str]


class HeartbeatRow(Base):
    __tablename__ = "heartbeats"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    senior_id: Mapped[UUID] = mapped_column(Uuid, index=True)
    at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)


class GrantRow(Base):
    __tablename__ = "grants"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    senior_id: Mapped[UUID] = mapped_column(Uuid, index=True)
    role: Mapped[str] = mapped_column(String(64))
    scope: Mapped[str] = mapped_column(String(64))
    api_key_hash: Mapped[str] = mapped_column(String(128), index=True)
    granted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
