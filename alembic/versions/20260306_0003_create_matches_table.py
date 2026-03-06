"""create matches table

Revision ID: 20260306_0003
Revises: 20260305_0002
Create Date: 2026-03-06 10:10:00

"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "20260306_0003"
down_revision: str | None = "20260305_0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "matches",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("home_team_id", sa.Integer(), nullable=False),
        sa.Column("away_team_id", sa.Integer(), nullable=False),
        sa.Column("home_score", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("away_score", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("match_date", sa.Date(), nullable=False),
        sa.Column("season", sa.String(length=20), nullable=False),
        sa.CheckConstraint("home_team_id <> away_team_id", name="ck_matches_distinct_teams"),
        sa.CheckConstraint("home_score >= 0", name="ck_matches_home_score_non_negative"),
        sa.CheckConstraint("away_score >= 0", name="ck_matches_away_score_non_negative"),
        sa.ForeignKeyConstraint(["away_team_id"], ["teams.id"]),
        sa.ForeignKeyConstraint(["home_team_id"], ["teams.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_matches_away_team_id"), "matches", ["away_team_id"], unique=False)
    op.create_index(op.f("ix_matches_home_team_id"), "matches", ["home_team_id"], unique=False)
    op.create_index(op.f("ix_matches_id"), "matches", ["id"], unique=False)
    op.create_index(op.f("ix_matches_match_date"), "matches", ["match_date"], unique=False)
    op.create_index(op.f("ix_matches_season"), "matches", ["season"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_matches_season"), table_name="matches")
    op.drop_index(op.f("ix_matches_match_date"), table_name="matches")
    op.drop_index(op.f("ix_matches_id"), table_name="matches")
    op.drop_index(op.f("ix_matches_home_team_id"), table_name="matches")
    op.drop_index(op.f("ix_matches_away_team_id"), table_name="matches")
    op.drop_table("matches")
