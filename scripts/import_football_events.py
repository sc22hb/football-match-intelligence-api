"""imports football dataset csv files into teams, players, matches, and events."""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path

from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings
from app.models import Event, Fixture, Match, Player, Team


@dataclass
class EntityStats:
    created: int = 0
    skipped: int = 0
    failed: int = 0


@dataclass
class ImportStats:
    teams: EntityStats = field(default_factory=EntityStats)
    players: EntityStats = field(default_factory=EntityStats)
    matches: EntityStats = field(default_factory=EntityStats)
    fixtures: EntityStats = field(default_factory=EntityStats)
    events: EntityStats = field(default_factory=EntityStats)
    errors: list[str] = field(default_factory=list)

    @property
    def failed_total(self) -> int:
        return self.teams.failed + self.players.failed + self.matches.failed + self.fixtures.failed + self.events.failed


def _normalize_key(value: str) -> str:
    return "".join(ch for ch in value.lower() if ch.isalnum())


def _row_map(row: dict[str, str]) -> dict[str, str]:
    return {_normalize_key(k): (v.strip() if isinstance(v, str) else "") for k, v in row.items()}


def _get_required(row: dict[str, str], aliases: list[str]) -> str:
    for alias in aliases:
        value = row.get(_normalize_key(alias), "")
        if value:
            return value
    raise ValueError(f"Missing required column value for aliases: {aliases}")


def _get_optional(row: dict[str, str], aliases: list[str], default: str = "") -> str:
    for alias in aliases:
        value = row.get(_normalize_key(alias), "")
        if value:
            return value
    return default


def _parse_date(raw: str) -> date:
    known_formats = ["%Y-%m-%d", "%d/%m/%Y", "%Y/%m/%d", "%d-%m-%Y"]
    for fmt in known_formats:
        try:
            return datetime.strptime(raw, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"Invalid date format: {raw}")


def _read_csv_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(f"CSV file not found: {path}")

    with path.open("r", encoding="utf-8-sig", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        return [_row_map(row) for row in reader]


def _find_team_by_name(db: Session, name: str) -> Team | None:
    stmt = select(Team).where(func.lower(Team.name) == name.lower())
    return db.execute(stmt).scalar_one_or_none()


def _find_player_by_name_and_team(db: Session, name: str, team_id: int) -> Player | None:
    stmt = select(Player).where(
        func.lower(Player.name) == name.lower(),
        Player.team_id == team_id,
    )
    return db.execute(stmt).scalar_one_or_none()


def _find_match(
    db: Session,
    home_team_id: int,
    away_team_id: int,
    match_date: date,
    season: str,
) -> Match | None:
    stmt = select(Match).where(
        Match.home_team_id == home_team_id,
        Match.away_team_id == away_team_id,
        Match.match_date == match_date,
        Match.season == season,
    )
    return db.execute(stmt).scalar_one_or_none()


def _find_fixture(
    db: Session,
    home_team_id: int,
    away_team_id: int,
    fixture_date: date,
    season: str,
) -> Fixture | None:
    stmt = select(Fixture).where(
        Fixture.home_team_id == home_team_id,
        Fixture.away_team_id == away_team_id,
        Fixture.fixture_date == fixture_date,
        Fixture.season == season,
    )
    return db.execute(stmt).scalar_one_or_none()


def _find_event(
    db: Session,
    match_id: int,
    team_id: int,
    player_id: int,
    minute: int,
    event_type: str,
    event_detail: str,
) -> Event | None:
    stmt = select(Event).where(
        Event.match_id == match_id,
        Event.team_id == team_id,
        Event.player_id == player_id,
        Event.minute == minute,
        func.lower(Event.event_type) == event_type.lower(),
        func.lower(Event.event_detail) == event_detail.lower(),
    )
    return db.execute(stmt).scalar_one_or_none()


def _import_teams(db: Session, rows: list[dict[str, str]], stats: ImportStats) -> None:
    for idx, row in enumerate(rows, start=1):
        try:
            name = _get_required(row, ["name", "team_name", "team"])
            league = _get_required(row, ["league", "competition"])
            country = _get_required(row, ["country", "nation"])

            existing = _find_team_by_name(db, name)
            if existing is not None:
                stats.teams.skipped += 1
                continue

            db.add(Team(name=name, league=league, country=country))
            db.flush()
            stats.teams.created += 1
        except Exception as exc:  # noqa: BLE001
            stats.teams.failed += 1
            stats.errors.append(f"teams row {idx}: {exc}")


def _import_players(db: Session, rows: list[dict[str, str]], stats: ImportStats) -> None:
    for idx, row in enumerate(rows, start=1):
        try:
            name = _get_required(row, ["name", "player_name", "player"])
            team_name = _get_required(row, ["team_name", "team", "club"])
            position = _get_required(row, ["position", "role"])

            team = _find_team_by_name(db, team_name)
            if team is None:
                raise ValueError(f"Unknown team '{team_name}'")

            existing = _find_player_by_name_and_team(db, name, team.id)
            if existing is not None:
                stats.players.skipped += 1
                continue

            db.add(Player(name=name, team_id=team.id, position=position))
            db.flush()
            stats.players.created += 1
        except Exception as exc:  # noqa: BLE001
            stats.players.failed += 1
            stats.errors.append(f"players row {idx}: {exc}")


def _import_matches(db: Session, rows: list[dict[str, str]], stats: ImportStats) -> None:
    for idx, row in enumerate(rows, start=1):
        try:
            home_team_name = _get_required(row, ["home_team", "home_team_name", "hometeam"])
            away_team_name = _get_required(row, ["away_team", "away_team_name", "awayteam"])
            raw_match_date = _get_required(row, ["match_date", "date"])
            season = _get_required(row, ["season"])
            home_score = int(_get_required(row, ["home_score", "fthg", "homegoals"]))
            away_score = int(_get_required(row, ["away_score", "ftag", "awaygoals"]))

            home_team = _find_team_by_name(db, home_team_name)
            away_team = _find_team_by_name(db, away_team_name)
            if home_team is None:
                raise ValueError(f"Unknown home team '{home_team_name}'")
            if away_team is None:
                raise ValueError(f"Unknown away team '{away_team_name}'")
            if home_team.id == away_team.id:
                raise ValueError("home and away team cannot be the same")

            match_date = _parse_date(raw_match_date)
            existing = _find_match(db, home_team.id, away_team.id, match_date, season)
            if existing is not None:
                stats.matches.skipped += 1
                continue

            db.add(
                Match(
                    home_team_id=home_team.id,
                    away_team_id=away_team.id,
                    home_score=home_score,
                    away_score=away_score,
                    match_date=match_date,
                    season=season,
                )
            )
            db.flush()
            stats.matches.created += 1
        except Exception as exc:  # noqa: BLE001
            stats.matches.failed += 1
            stats.errors.append(f"matches row {idx}: {exc}")


def _import_events(db: Session, rows: list[dict[str, str]], stats: ImportStats) -> None:
    for idx, row in enumerate(rows, start=1):
        try:
            home_team_name = _get_required(row, ["home_team", "home_team_name", "hometeam"])
            away_team_name = _get_required(row, ["away_team", "away_team_name", "awayteam"])
            raw_match_date = _get_required(row, ["match_date", "date"])
            season = _get_required(row, ["season"])
            team_name = _get_required(row, ["team_name", "team", "club"])
            player_name = _get_required(row, ["player_name", "player"])
            minute = int(_get_required(row, ["minute", "event_minute"]))
            event_type = _get_required(row, ["event_type", "type"])
            event_detail = _get_optional(row, ["event_detail", "detail", "description"], default=event_type)

            home_team = _find_team_by_name(db, home_team_name)
            away_team = _find_team_by_name(db, away_team_name)
            event_team = _find_team_by_name(db, team_name)
            if home_team is None or away_team is None or event_team is None:
                raise ValueError("Unknown team reference in event row")

            match_date = _parse_date(raw_match_date)
            match = _find_match(db, home_team.id, away_team.id, match_date, season)
            if match is None:
                raise ValueError("Matching match row not found for event")

            player = _find_player_by_name_and_team(db, player_name, event_team.id)
            if player is None:
                raise ValueError(f"Unknown player '{player_name}' for team '{team_name}'")

            existing = _find_event(
                db,
                match_id=match.id,
                team_id=event_team.id,
                player_id=player.id,
                minute=minute,
                event_type=event_type,
                event_detail=event_detail,
            )
            if existing is not None:
                stats.events.skipped += 1
                continue

            db.add(
                Event(
                    match_id=match.id,
                    team_id=event_team.id,
                    player_id=player.id,
                    minute=minute,
                    event_type=event_type,
                    event_detail=event_detail,
                )
            )
            db.flush()
            stats.events.created += 1
        except Exception as exc:  # noqa: BLE001
            stats.events.failed += 1
            stats.errors.append(f"events row {idx}: {exc}")


def _import_fixtures(db: Session, rows: list[dict[str, str]], stats: ImportStats) -> None:
    for idx, row in enumerate(rows, start=1):
        try:
            home_team_name = _get_required(row, ["home_team", "home_team_name", "hometeam"])
            away_team_name = _get_required(row, ["away_team", "away_team_name", "awayteam"])
            raw_fixture_date = _get_required(row, ["fixture_date", "match_date", "date"])
            season = _get_required(row, ["season"])

            home_team = _find_team_by_name(db, home_team_name)
            away_team = _find_team_by_name(db, away_team_name)
            if home_team is None:
                raise ValueError(f"Unknown home team '{home_team_name}'")
            if away_team is None:
                raise ValueError(f"Unknown away team '{away_team_name}'")
            if home_team.id == away_team.id:
                raise ValueError("home and away team cannot be the same")

            fixture_date = _parse_date(raw_fixture_date)
            existing = _find_fixture(db, home_team.id, away_team.id, fixture_date, season)
            if existing is not None:
                stats.fixtures.skipped += 1
                continue

            db.add(
                Fixture(
                    home_team_id=home_team.id,
                    away_team_id=away_team.id,
                    fixture_date=fixture_date,
                    season=season,
                )
            )
            db.flush()
            stats.fixtures.created += 1
        except Exception as exc:  # noqa: BLE001
            stats.fixtures.failed += 1
            stats.errors.append(f"fixtures row {idx}: {exc}")


def import_dataset(
    db: Session,
    dataset_dir: Path,
    teams_file: str = "teams.csv",
    players_file: str = "players.csv",
    matches_file: str = "matches.csv",
    fixtures_file: str = "fixtures.csv",
    events_file: str = "events.csv",
) -> ImportStats:
    stats = ImportStats()

    team_rows = _read_csv_rows(dataset_dir / teams_file)
    player_rows = _read_csv_rows(dataset_dir / players_file)
    match_rows = _read_csv_rows(dataset_dir / matches_file)
    fixture_rows = _read_csv_rows(dataset_dir / fixtures_file) if (dataset_dir / fixtures_file).exists() else []
    event_rows = _read_csv_rows(dataset_dir / events_file)

    _import_teams(db=db, rows=team_rows, stats=stats)
    _import_players(db=db, rows=player_rows, stats=stats)
    _import_matches(db=db, rows=match_rows, stats=stats)
    _import_fixtures(db=db, rows=fixture_rows, stats=stats)
    _import_events(db=db, rows=event_rows, stats=stats)

    return stats


def _print_summary(stats: ImportStats, dry_run: bool) -> None:
    print("\nImport summary")
    print("-" * 60)
    print(f"Teams   : created={stats.teams.created} skipped={stats.teams.skipped} failed={stats.teams.failed}")
    print(f"Players : created={stats.players.created} skipped={stats.players.skipped} failed={stats.players.failed}")
    print(f"Matches : created={stats.matches.created} skipped={stats.matches.skipped} failed={stats.matches.failed}")
    print(f"Fixtures: created={stats.fixtures.created} skipped={stats.fixtures.skipped} failed={stats.fixtures.failed}")
    print(f"Events  : created={stats.events.created} skipped={stats.events.skipped} failed={stats.events.failed}")
    print(f"Mode    : {'dry-run (rolled back)' if dry_run else 'commit'}")

    if stats.errors:
        print("\nErrors")
        print("-" * 60)
        for message in stats.errors[:20]:
            print(f"- {message}")
        if len(stats.errors) > 20:
            print(f"- ... {len(stats.errors) - 20} more errors omitted")


def run_import(
    database_url: str,
    dataset_dir: Path,
    teams_file: str,
    players_file: str,
    matches_file: str,
    fixtures_file: str,
    events_file: str,
    dry_run: bool,
) -> ImportStats:
    local_engine = create_engine(database_url, pool_pre_ping=True)
    session_factory = sessionmaker(
        bind=local_engine,
        autocommit=False,
        autoflush=False,
        class_=Session,
    )

    with session_factory() as db:
        try:
            stats = import_dataset(
                db=db,
                dataset_dir=dataset_dir,
                teams_file=teams_file,
                players_file=players_file,
                matches_file=matches_file,
                fixtures_file=fixtures_file,
                events_file=events_file,
            )

            if dry_run or stats.failed_total > 0:
                db.rollback()
            else:
                db.commit()

            return stats
        except Exception:
            db.rollback()
            raise


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Import football CSV dataset into the API database")
    parser.add_argument("--dataset-dir", default="data/sample", help="Directory containing dataset CSV files")
    parser.add_argument("--teams-file", default="teams.csv", help="Teams CSV filename")
    parser.add_argument("--players-file", default="players.csv", help="Players CSV filename")
    parser.add_argument("--matches-file", default="matches.csv", help="Matches CSV filename")
    parser.add_argument("--fixtures-file", default="fixtures.csv", help="Fixtures CSV filename")
    parser.add_argument("--events-file", default="events.csv", help="Events CSV filename")
    parser.add_argument("--database-url", default="", help="SQLAlchemy database URL override")
    parser.add_argument("--dry-run", action="store_true", help="Parse and validate data but rollback changes")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    settings = get_settings()
    database_url = args.database_url or settings.database_url
    dataset_dir = Path(args.dataset_dir)

    stats = run_import(
        database_url=database_url,
        dataset_dir=dataset_dir,
        teams_file=args.teams_file,
        players_file=args.players_file,
        matches_file=args.matches_file,
        fixtures_file=args.fixtures_file,
        events_file=args.events_file,
        dry_run=args.dry_run,
    )

    _print_summary(stats=stats, dry_run=args.dry_run)
    return 1 if stats.failed_total > 0 else 0


if __name__ == "__main__":
    raise SystemExit(main())
