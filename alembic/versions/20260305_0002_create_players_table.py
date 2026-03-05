"""create players table

Revision ID: 20260305_0002
Revises: 20260305_0001
Create Date: 2026-03-05 15:05:00

"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "20260305_0002"
down_revision: str | None = "20260305_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "players",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("team_id", sa.Integer(), nullable=False),
        sa.Column("position", sa.String(length=60), nullable=False),
        sa.ForeignKeyConstraint(["team_id"], ["teams.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name", "team_id", name="uq_players_name_team_id"),
    )
    op.create_index(op.f("ix_players_id"), "players", ["id"], unique=False)
    op.create_index(op.f("ix_players_name"), "players", ["name"], unique=False)
    op.create_index(op.f("ix_players_position"), "players", ["position"], unique=False)
    op.create_index(op.f("ix_players_team_id"), "players", ["team_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_players_team_id"), table_name="players")
    op.drop_index(op.f("ix_players_position"), table_name="players")
    op.drop_index(op.f("ix_players_name"), table_name="players")
    op.drop_index(op.f("ix_players_id"), table_name="players")
    op.drop_table("players")
