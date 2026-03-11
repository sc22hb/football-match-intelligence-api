"""smoke tests for csv dataset import pipeline."""

from pathlib import Path

from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.models import Event, Fixture, Match, Player, Team
from scripts.import_football_events import import_dataset



def test_import_dataset_smoke_and_idempotency() -> None:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    session_factory = sessionmaker(bind=engine, autocommit=False, autoflush=False, class_=Session)

    Base.metadata.create_all(bind=engine)

    sample_dir = Path("data/premier_league_2025_26")

    with session_factory() as db:
        first = import_dataset(db=db, dataset_dir=sample_dir)
        assert first.failed_total == 0
        assert first.teams.created > 0
        assert first.players.created > 0
        assert first.matches.created > 0
        assert first.events.created > 0
        assert first.fixtures.created >= 0
        db.commit()

        team_count = db.execute(select(func.count(Team.id))).scalar_one()
        player_count = db.execute(select(func.count(Player.id))).scalar_one()
        match_count = db.execute(select(func.count(Match.id))).scalar_one()
        fixture_count = db.execute(select(func.count(Fixture.id))).scalar_one()
        event_count = db.execute(select(func.count(Event.id))).scalar_one()

        assert team_count == first.teams.created
        assert player_count == first.players.created
        assert match_count == first.matches.created
        assert fixture_count == first.fixtures.created
        assert event_count == first.events.created

        second = import_dataset(db=db, dataset_dir=sample_dir)
        assert second.failed_total == 0
        assert second.teams.created == 0
        assert second.players.created == 0
        assert second.matches.created == 0
        assert second.fixtures.created == 0
        assert second.events.created == 0
        assert second.teams.skipped == team_count
        assert second.players.skipped == player_count
        assert second.matches.skipped == match_count
        assert second.fixtures.skipped == fixture_count
        assert second.events.skipped == event_count
