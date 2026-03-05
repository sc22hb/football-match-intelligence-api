"""team repository with raw sqlalchemy query methods only."""

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from app.models.team import Team
from app.schemas.team import TeamCreate, TeamUpdate


class TeamRepository:
    def get_by_id(self, db: Session, team_id: int) -> Team | None:
        stmt: Select[tuple[Team]] = select(Team).where(Team.id == team_id)
        return db.execute(stmt).scalar_one_or_none()

    def get_by_name(self, db: Session, name: str) -> Team | None:
        stmt: Select[tuple[Team]] = select(Team).where(Team.name == name)
        return db.execute(stmt).scalar_one_or_none()

    def list(self, db: Session, skip: int, limit: int) -> list[Team]:
        stmt: Select[tuple[Team]] = select(Team).offset(skip).limit(limit).order_by(Team.id)
        return list(db.execute(stmt).scalars().all())

    def count(self, db: Session) -> int:
        stmt = select(func.count(Team.id))
        return int(db.execute(stmt).scalar_one())

    def create(self, db: Session, payload: TeamCreate) -> Team:
        team = Team(**payload.model_dump())
        db.add(team)
        db.commit()
        db.refresh(team)
        return team

    def update(self, db: Session, team: Team, payload: TeamUpdate) -> Team:
        changes = payload.model_dump(exclude_unset=True)
        for field, value in changes.items():
            setattr(team, field, value)

        db.add(team)
        db.commit()
        db.refresh(team)
        return team

    def delete(self, db: Session, team: Team) -> None:
        db.delete(team)
        db.commit()
