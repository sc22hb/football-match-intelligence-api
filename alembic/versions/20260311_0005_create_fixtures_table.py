"""create fixtures table

Revision ID: 20260311_0005
Revises: 20260306_0004
Create Date: 2026-03-11 16:10:00

"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "20260311_0005"
down_revision: str | None = "20260306_0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "fixtures",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("home_team_id", sa.Integer(), nullable=False),
        sa.Column("away_team_id", sa.Integer(), nullable=False),
        sa.Column("fixture_date", sa.Date(), nullable=False),
        sa.Column("season", sa.String(length=20), nullable=False),
        sa.ForeignKeyConstraint(["away_team_id"], ["teams.id"]),
        sa.ForeignKeyConstraint(["home_team_id"], ["teams.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_fixtures_id"), "fixtures", ["id"], unique=False)
    op.create_index(op.f("ix_fixtures_home_team_id"), "fixtures", ["home_team_id"], unique=False)
    op.create_index(op.f("ix_fixtures_away_team_id"), "fixtures", ["away_team_id"], unique=False)
    op.create_index(op.f("ix_fixtures_fixture_date"), "fixtures", ["fixture_date"], unique=False)
    op.create_index(op.f("ix_fixtures_season"), "fixtures", ["season"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_fixtures_season"), table_name="fixtures")
    op.drop_index(op.f("ix_fixtures_fixture_date"), table_name="fixtures")
    op.drop_index(op.f("ix_fixtures_away_team_id"), table_name="fixtures")
    op.drop_index(op.f("ix_fixtures_home_team_id"), table_name="fixtures")
    op.drop_index(op.f("ix_fixtures_id"), table_name="fixtures")
    op.drop_table("fixtures")
