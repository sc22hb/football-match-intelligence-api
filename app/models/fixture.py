"""upcoming fixture database model linking home and away teams."""

from datetime import date

from sqlalchemy import Date, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Fixture(Base):
    __tablename__ = "fixtures"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    home_team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), nullable=False, index=True)
    away_team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), nullable=False, index=True)
    fixture_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    season: Mapped[str] = mapped_column(String(20), nullable=False, index=True)

    home_team = relationship("Team", foreign_keys=[home_team_id], back_populates="home_fixtures")
    away_team = relationship("Team", foreign_keys=[away_team_id], back_populates="away_fixtures")
