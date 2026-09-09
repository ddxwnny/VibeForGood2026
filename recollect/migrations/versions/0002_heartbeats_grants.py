"""heartbeats and grants

Revision ID: 0002_heartbeats_grants
Revises: 0001_initial
Create Date: 2026-09-09
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0002_heartbeats_grants"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "heartbeats",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("senior_id", sa.Uuid(), nullable=False),
        sa.Column("at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_heartbeats_senior_id", "heartbeats", ["senior_id"])

    op.create_table(
        "grants",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("senior_id", sa.Uuid(), nullable=False),
        sa.Column("role", sa.String(64), nullable=False),
        sa.Column("scope", sa.String(64), nullable=False),
        sa.Column("api_key_hash", sa.String(128), nullable=False),
        sa.Column("granted_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_grants_senior_id", "grants", ["senior_id"])
    op.create_index("ix_grants_api_key_hash", "grants", ["api_key_hash"])


def downgrade() -> None:
    op.drop_index("ix_grants_api_key_hash", table_name="grants")
    op.drop_index("ix_grants_senior_id", table_name="grants")
    op.drop_table("grants")
    op.drop_index("ix_heartbeats_senior_id", table_name="heartbeats")
    op.drop_table("heartbeats")
