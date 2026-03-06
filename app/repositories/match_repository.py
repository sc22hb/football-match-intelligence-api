"""match repository with raw sqlalchemy query methods only."""

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from app.models.match import Match
from app.schemas.match import MatchCreate, MatchUpdate


class MatchRepository:
    def get_by_id(self, db: Session, match_id: int) -> Match | None:
        stmt: Select[tuple[Match]] = select(Match).where(Match.id == match_id)
        return db.execute(stmt).scalar_one_or_none()

    def list(self, db: Session, skip: int, limit: int) -> list[Match]:
        stmt: Select[tuple[Match]] = select(Match).offset(skip).limit(limit).order_by(Match.id)
        return list(db.execute(stmt).scalars().all())

    def count(self, db: Session) -> int:
        stmt = select(func.count(Match.id))
        return int(db.execute(stmt).scalar_one())

    def create(self, db: Session, payload: MatchCreate) -> Match:
        match = Match(**payload.model_dump())
        db.add(match)
        db.commit()
        db.refresh(match)
        return match

    def update(self, db: Session, match: Match, payload: MatchUpdate) -> Match:
        changes = payload.model_dump(exclude_unset=True)
        for field, value in changes.items():
            setattr(match, field, value)

        db.add(match)
        db.commit()
        db.refresh(match)
        return match

    def delete(self, db: Session, match: Match) -> None:
        db.delete(match)
        db.commit()
