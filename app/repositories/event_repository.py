"""event repository with raw sqlalchemy query methods only."""

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from app.models.event import Event
from app.schemas.event import EventCreate


class EventRepository:
    def list(self, db: Session, skip: int, limit: int) -> list[Event]:
        stmt: Select[tuple[Event]] = select(Event).offset(skip).limit(limit).order_by(Event.id)
        return list(db.execute(stmt).scalars().all())

    def count(self, db: Session) -> int:
        stmt = select(func.count(Event.id))
        return int(db.execute(stmt).scalar_one())

    def create(self, db: Session, payload: EventCreate) -> Event:
        event = Event(**payload.model_dump())
        db.add(event)
        db.commit()
        db.refresh(event)
        return event
