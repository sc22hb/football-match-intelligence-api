"""create events table

Revision ID: 20260306_0004
Revises: 20260306_0003
Create Date: 2026-03-06 10:35:00

"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "20260306_0004"
down_revision: str | None = "20260306_0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "events",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("match_id", sa.Integer(), nullable=False),
        sa.Column("team_id", sa.Integer(), nullable=False),
        sa.Column("player_id", sa.Integer(), nullable=False),
        sa.Column("minute", sa.Integer(), nullable=False),
        sa.Column("event_type", sa.String(length=50), nullable=False),
        sa.Column("event_detail", sa.String(length=255), nullable=False),
        sa.CheckConstraint("minute >= 0", name="ck_events_minute_non_negative"),
        sa.ForeignKeyConstraint(["match_id"], ["matches.id"]),
        sa.ForeignKeyConstraint(["team_id"], ["teams.id"]),
        sa.ForeignKeyConstraint(["player_id"], ["players.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_events_event_type"), "events", ["event_type"], unique=False)
    op.create_index(op.f("ix_events_id"), "events", ["id"], unique=False)
    op.create_index(op.f("ix_events_match_id"), "events", ["match_id"], unique=False)
    op.create_index(op.f("ix_events_minute"), "events", ["minute"], unique=False)
    op.create_index(op.f("ix_events_player_id"), "events", ["player_id"], unique=False)
    op.create_index(op.f("ix_events_team_id"), "events", ["team_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_events_team_id"), table_name="events")
    op.drop_index(op.f("ix_events_player_id"), table_name="events")
    op.drop_index(op.f("ix_events_minute"), table_name="events")
    op.drop_index(op.f("ix_events_match_id"), table_name="events")
    op.drop_index(op.f("ix_events_id"), table_name="events")
    op.drop_index(op.f("ix_events_event_type"), table_name="events")
    op.drop_table("events")
