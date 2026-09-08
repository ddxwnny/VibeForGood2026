"""initial observation-log schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-09-09
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "seniors",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("display_name", sa.String(255), nullable=False),
        sa.Column("preferred_language", sa.String(64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "enrolments",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("senior_id", sa.Uuid(), nullable=False),
        sa.Column("enrolled_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("artefacts", postgresql.JSONB(), nullable=False),
        sa.Column("withdrawn_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_enrolments_senior_id", "enrolments", ["senior_id"], unique=True)

    op.create_table(
        "interactions",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("senior_id", sa.Uuid(), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("idempotency_key", sa.String(255), nullable=False),
    )
    op.create_index("ix_interactions_senior_id", "interactions", ["senior_id"])
    op.create_index("ix_interactions_idempotency_key", "interactions", ["idempotency_key"], unique=True)

    op.create_table(
        "observations",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("senior_id", sa.Uuid(), nullable=False),
        sa.Column("interaction_id", sa.Uuid(), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("signal_type", sa.String(64), nullable=False),
        sa.Column("item_variant", sa.String(255), nullable=True),
        sa.Column("extraction_model_id", sa.String(255), nullable=True),
        sa.Column("prompt_version", sa.String(64), nullable=True),
        sa.Column("stt_model_version", sa.String(64), nullable=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("outcome", sa.String(64), nullable=True),
        sa.Column("supersedes_id", sa.Uuid(), nullable=True),
    )
    op.create_index("ix_observations_senior_id", "observations", ["senior_id"])
    op.create_index("ix_observations_interaction_id", "observations", ["interaction_id"])
    op.create_index("ix_observations_occurred_at", "observations", ["occurred_at"])

    op.create_table(
        "gaps",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("senior_id", sa.Uuid(), nullable=False),
        sa.Column("reason", sa.String(64), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_gaps_senior_id", "gaps", ["senior_id"])

    op.create_table(
        "tombstones",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("senior_id", sa.Uuid(), nullable=False),
        sa.Column("reason", sa.String(64), nullable=False),
        sa.Column("shredded_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("stores_shredded", postgresql.JSONB(), nullable=False),
    )
    op.create_index("ix_tombstones_senior_id", "tombstones", ["senior_id"], unique=True)


def downgrade() -> None:
    op.drop_table("tombstones")
    op.drop_table("gaps")
    op.drop_table("observations")
    op.drop_table("interactions")
    op.drop_table("enrolments")
    op.drop_table("seniors")
