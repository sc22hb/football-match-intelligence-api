"""team database model and relation to players."""

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Team(Base):
    __tablename__ = "teams"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False, unique=True, index=True)
    league: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    country: Mapped[str] = mapped_column(String(120), nullable=False, index=True)

    players = relationship("Player", back_populates="team")
    home_matches = relationship(
        "Match",
        foreign_keys="Match.home_team_id",
        back_populates="home_team",
    )
    away_matches = relationship(
        "Match",
        foreign_keys="Match.away_team_id",
        back_populates="away_team",
    )
    home_fixtures = relationship(
        "Fixture",
        foreign_keys="Fixture.home_team_id",
        back_populates="home_team",
    )
    away_fixtures = relationship(
        "Fixture",
        foreign_keys="Fixture.away_team_id",
        back_populates="away_team",
    )
    events = relationship("Event", back_populates="team")
