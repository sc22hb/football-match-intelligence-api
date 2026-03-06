"""event business logic between routes and repository."""

from sqlalchemy.orm import Session

from app.models.event import Event
from app.repositories.event_repository import EventRepository
from app.repositories.match_repository import MatchRepository
from app.repositories.player_repository import PlayerRepository
from app.repositories.team_repository import TeamRepository
from app.schemas.event import EventCreate
from app.services.errors import NotFoundError, ServiceValidationError


class EventService:
    def __init__(
        self,
        repository: EventRepository | None = None,
        match_repository: MatchRepository | None = None,
        team_repository: TeamRepository | None = None,
        player_repository: PlayerRepository | None = None,
    ) -> None:
        self.repository = repository or EventRepository()
        self.match_repository = match_repository or MatchRepository()
        self.team_repository = team_repository or TeamRepository()
        self.player_repository = player_repository or PlayerRepository()

    def list_events(self, db: Session, skip: int, limit: int) -> tuple[list[Event], int]:
        items = self.repository.list(db=db, skip=skip, limit=limit)
        total = self.repository.count(db=db)
        return items, total

    def create_event(self, db: Session, payload: EventCreate) -> Event:
        match = self.match_repository.get_by_id(db=db, match_id=payload.match_id)
        if match is None:
            raise NotFoundError(f"Match with id={payload.match_id} was not found")

        team = self.team_repository.get_by_id(db=db, team_id=payload.team_id)
        if team is None:
            raise NotFoundError(f"Team with id={payload.team_id} was not found")

        player = self.player_repository.get_by_id(db=db, player_id=payload.player_id)
        if player is None:
            raise NotFoundError(f"Player with id={payload.player_id} was not found")

        if player.team_id != payload.team_id:
            raise ServiceValidationError("player_id does not belong to team_id")

        valid_match_teams = {match.home_team_id, match.away_team_id}
        if payload.team_id not in valid_match_teams:
            raise ServiceValidationError("team_id is not part of the match")

        return self.repository.create(db=db, payload=payload)
