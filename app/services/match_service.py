"""match business logic between routes and repository."""

from sqlalchemy.orm import Session

from app.models.match import Match
from app.repositories.match_repository import MatchRepository
from app.repositories.team_repository import TeamRepository
from app.schemas.match import MatchCreate, MatchUpdate
from app.services.errors import NotFoundError, ServiceValidationError


class MatchService:
    def __init__(
        self,
        repository: MatchRepository | None = None,
        team_repository: TeamRepository | None = None,
    ) -> None:
        self.repository = repository or MatchRepository()
        self.team_repository = team_repository or TeamRepository()

    def list_matches(self, db: Session, skip: int, limit: int) -> tuple[list[Match], int]:
        items = self.repository.list(db=db, skip=skip, limit=limit)
        total = self.repository.count(db=db)
        return items, total

    def get_match(self, db: Session, match_id: int) -> Match:
        match = self.repository.get_by_id(db=db, match_id=match_id)
        if match is None:
            raise NotFoundError(f"Match with id={match_id} was not found")
        return match

    def create_match(self, db: Session, payload: MatchCreate) -> Match:
        self._validate_teams_exist(db, payload.home_team_id, payload.away_team_id)
        self._validate_distinct_teams(payload.home_team_id, payload.away_team_id)
        return self.repository.create(db=db, payload=payload)

    def update_match(self, db: Session, match_id: int, payload: MatchUpdate) -> Match:
        match = self.get_match(db=db, match_id=match_id)

        next_home = payload.home_team_id if payload.home_team_id is not None else match.home_team_id
        next_away = payload.away_team_id if payload.away_team_id is not None else match.away_team_id

        self._validate_teams_exist(db, next_home, next_away)
        self._validate_distinct_teams(next_home, next_away)

        return self.repository.update(db=db, match=match, payload=payload)

    def delete_match(self, db: Session, match_id: int) -> None:
        match = self.get_match(db=db, match_id=match_id)
        self.repository.delete(db=db, match=match)

    def _validate_teams_exist(self, db: Session, home_team_id: int, away_team_id: int) -> None:
        home_team = self.team_repository.get_by_id(db=db, team_id=home_team_id)
        if home_team is None:
            raise NotFoundError(f"Team with id={home_team_id} was not found")

        away_team = self.team_repository.get_by_id(db=db, team_id=away_team_id)
        if away_team is None:
            raise NotFoundError(f"Team with id={away_team_id} was not found")

    def _validate_distinct_teams(self, home_team_id: int, away_team_id: int) -> None:
        if home_team_id == away_team_id:
            raise ServiceValidationError("home_team_id and away_team_id must be different")
