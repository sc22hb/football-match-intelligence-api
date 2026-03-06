"""smoke tests for csv dataset import pipeline."""

from pathlib import Path

from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.models import Event, Match, Player, Team
from scripts.import_football_events import import_dataset



def test_import_dataset_smoke_and_idempotency() -> None:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    session_factory = sessionmaker(bind=engine, autocommit=False, autoflush=False, class_=Session)

    Base.metadata.create_all(bind=engine)

    sample_dir = Path("data/sample")

    with session_factory() as db:
        first = import_dataset(db=db, dataset_dir=sample_dir)
        assert first.failed_total == 0
        assert first.teams.created == 3
        assert first.players.created == 6
        assert first.matches.created == 3
        assert first.events.created == 7
        db.commit()

        team_count = db.execute(select(func.count(Team.id))).scalar_one()
        player_count = db.execute(select(func.count(Player.id))).scalar_one()
        match_count = db.execute(select(func.count(Match.id))).scalar_one()
        event_count = db.execute(select(func.count(Event.id))).scalar_one()

        assert team_count == 3
        assert player_count == 6
        assert match_count == 3
        assert event_count == 7

        second = import_dataset(db=db, dataset_dir=sample_dir)
        assert second.failed_total == 0
        assert second.teams.created == 0
        assert second.players.created == 0
        assert second.matches.created == 0
        assert second.events.created == 0
        assert second.teams.skipped == 3
        assert second.players.skipped == 6
        assert second.matches.skipped == 3
        assert second.events.skipped == 7
