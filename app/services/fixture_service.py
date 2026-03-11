"""fixture business logic between routes and repository."""

from sqlalchemy.orm import Session

from app.models.fixture import Fixture
from app.repositories.fixture_repository import FixtureRepository


class FixtureService:
    def __init__(self, repository: FixtureRepository | None = None) -> None:
        self.repository = repository or FixtureRepository()

    def list_fixtures(
        self,
        db: Session,
        skip: int,
        limit: int,
        season: str | None = None,
    ) -> tuple[list[Fixture], int]:
        items = self.repository.list(db=db, skip=skip, limit=limit, season=season)
        total = self.repository.count(db=db, season=season)
        return items, total
