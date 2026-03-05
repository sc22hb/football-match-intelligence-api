"""player repository with raw sqlalchemy query methods only."""

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from app.models.player import Player
from app.schemas.player import PlayerCreate, PlayerUpdate


class PlayerRepository:
    def get_by_id(self, db: Session, player_id: int) -> Player | None:
        stmt: Select[tuple[Player]] = select(Player).where(Player.id == player_id)
        return db.execute(stmt).scalar_one_or_none()

    def get_by_name_and_team(self, db: Session, name: str, team_id: int) -> Player | None:
        stmt: Select[tuple[Player]] = select(Player).where(
            Player.name == name,
            Player.team_id == team_id,
        )
        return db.execute(stmt).scalar_one_or_none()

    def list(self, db: Session, skip: int, limit: int) -> list[Player]:
        stmt: Select[tuple[Player]] = select(Player).offset(skip).limit(limit).order_by(Player.id)
        return list(db.execute(stmt).scalars().all())

    def count(self, db: Session) -> int:
        stmt = select(func.count(Player.id))
        return int(db.execute(stmt).scalar_one())

    def create(self, db: Session, payload: PlayerCreate) -> Player:
        player = Player(**payload.model_dump())
        db.add(player)
        db.commit()
        db.refresh(player)
        return player

    def update(self, db: Session, player: Player, payload: PlayerUpdate) -> Player:
        changes = payload.model_dump(exclude_unset=True)
        for field, value in changes.items():
            setattr(player, field, value)

        db.add(player)
        db.commit()
        db.refresh(player)
        return player

    def delete(self, db: Session, player: Player) -> None:
        db.delete(player)
        db.commit()
