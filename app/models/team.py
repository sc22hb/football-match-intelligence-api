from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Team(Base):
    __tablename__ = "teams"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False, unique=True, index=True)
    league: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    country: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
