"""player business logic between routes and repository."""

from sqlalchemy.orm import Session

from app.models.player import Player
from app.repositories.player_repository import PlayerRepository
from app.repositories.team_repository import TeamRepository
from app.schemas.player import PlayerCreate, PlayerUpdate
from app.services.errors import ConflictError, NotFoundError


class PlayerService:
    def __init__(
        self,
        repository: PlayerRepository | None = None,
        team_repository: TeamRepository | None = None,
    ) -> None:
        self.repository = repository or PlayerRepository()
        self.team_repository = team_repository or TeamRepository()

    def list_players(self, db: Session, skip: int, limit: int) -> tuple[list[Player], int]:
        items = self.repository.list(db=db, skip=skip, limit=limit)
        total = self.repository.count(db=db)
        return items, total

    def get_player(self, db: Session, player_id: int) -> Player:
        player = self.repository.get_by_id(db=db, player_id=player_id)
        if player is None:
            raise NotFoundError(f"Player with id={player_id} was not found")
        return player

    def create_player(self, db: Session, payload: PlayerCreate) -> Player:
        team = self.team_repository.get_by_id(db=db, team_id=payload.team_id)
        if team is None:
            raise NotFoundError(f"Team with id={payload.team_id} was not found")

        existing = self.repository.get_by_name_and_team(
            db=db,
            name=payload.name,
            team_id=payload.team_id,
        )
        if existing is not None:
            raise ConflictError(
                f"Player '{payload.name}' already exists for team_id={payload.team_id}"
            )

        return self.repository.create(db=db, payload=payload)

    def update_player(self, db: Session, player_id: int, payload: PlayerUpdate) -> Player:
        player = self.get_player(db=db, player_id=player_id)

        next_team_id = payload.team_id if payload.team_id is not None else player.team_id
        next_name = payload.name if payload.name is not None else player.name

        team = self.team_repository.get_by_id(db=db, team_id=next_team_id)
        if team is None:
            raise NotFoundError(f"Team with id={next_team_id} was not found")

        existing = self.repository.get_by_name_and_team(
            db=db,
            name=next_name,
            team_id=next_team_id,
        )
        if existing is not None and existing.id != player.id:
            raise ConflictError(
                f"Player '{next_name}' already exists for team_id={next_team_id}"
            )

        return self.repository.update(db=db, player=player, payload=payload)

    def delete_player(self, db: Session, player_id: int) -> None:
        player = self.get_player(db=db, player_id=player_id)
        self.repository.delete(db=db, player=player)
