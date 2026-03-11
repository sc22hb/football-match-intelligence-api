"""fixture repository with raw sqlalchemy query methods only."""

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from app.models.fixture import Fixture


class FixtureRepository:
    def list(self, db: Session, skip: int, limit: int, season: str | None = None) -> list[Fixture]:
        stmt: Select[tuple[Fixture]] = (
            select(Fixture)
            .order_by(Fixture.fixture_date.asc(), Fixture.id.asc())
            .offset(skip)
            .limit(limit)
        )
        if season is not None:
            stmt = stmt.where(Fixture.season == season)
        return list(db.execute(stmt).scalars().all())

    def count(self, db: Session, season: str | None = None) -> int:
        stmt = select(func.count(Fixture.id))
        if season is not None:
            stmt = stmt.where(Fixture.season == season)
        return int(db.execute(stmt).scalar_one())
