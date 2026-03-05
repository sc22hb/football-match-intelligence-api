"""team business logic between routes and repository."""

from sqlalchemy.orm import Session

from app.models.team import Team
from app.repositories.team_repository import TeamRepository
from app.schemas.team import TeamCreate, TeamUpdate
from app.services.errors import ConflictError, NotFoundError


class TeamService:
    def __init__(self, repository: TeamRepository | None = None) -> None:
        self.repository = repository or TeamRepository()

    def list_teams(self, db: Session, skip: int, limit: int) -> tuple[list[Team], int]:
        items = self.repository.list(db=db, skip=skip, limit=limit)
        total = self.repository.count(db=db)
        return items, total

    def get_team(self, db: Session, team_id: int) -> Team:
        team = self.repository.get_by_id(db=db, team_id=team_id)
        if team is None:
            raise NotFoundError(f"Team with id={team_id} was not found")
        return team

    def create_team(self, db: Session, payload: TeamCreate) -> Team:
        existing = self.repository.get_by_name(db=db, name=payload.name)
        if existing is not None:
            raise ConflictError(f"Team name '{payload.name}' already exists")
        return self.repository.create(db=db, payload=payload)

    def update_team(self, db: Session, team_id: int, payload: TeamUpdate) -> Team:
        team = self.get_team(db=db, team_id=team_id)

        if payload.name and payload.name != team.name:
            existing = self.repository.get_by_name(db=db, name=payload.name)
            if existing is not None:
                raise ConflictError(f"Team name '{payload.name}' already exists")

        return self.repository.update(db=db, team=team, payload=payload)

    def delete_team(self, db: Session, team_id: int) -> None:
        team = self.get_team(db=db, team_id=team_id)
        self.repository.delete(db=db, team=team)
