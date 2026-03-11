"""Scrape Premier League 2025/26 data into importer-compatible CSV files.

The script uses the public Fantasy Premier League API to build:
- teams.csv
- players.csv
- matches.csv
- events.csv

The generated CSVs match the schema consumed by scripts/import_football_events.py.
Event data is derived from finished gameweek live stats. Because the FPL API does
not expose a reliable per-fixture event timeline, event minutes are approximated
to 90 and double-gameweek player stats are skipped when they cannot be mapped to
one specific fixture.
"""

from __future__ import annotations

import argparse
import csv
import json
import time
import unicodedata
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

FPL_BASE = "https://fantasy.premierleague.com/api"
DEFAULT_SEASON = "2025/26"
DEFAULT_OUT_DIR = "data/premier_league_2025_26"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json",
}

POSITION_MAP = {
    1: "GKP",
    2: "DEF",
    3: "MID",
    4: "FWD",
}

EVENT_STAT_MAP = {
    "goals_scored": "goal",
    "assists": "assist",
    "yellow_cards": "yellow_card",
    "red_cards": "red_card",
    "own_goals": "own_goal",
    "penalties_saved": "penalty_saved",
    "penalties_missed": "penalty_missed",
    "saves": "save",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Scrape Premier League 2025/26 data into importer-compatible CSVs"
    )
    parser.add_argument(
        "--season",
        default=DEFAULT_SEASON,
        help="Season label written into matches.csv and events.csv",
    )
    parser.add_argument(
        "--out-dir",
        default=DEFAULT_OUT_DIR,
        help="Directory where teams.csv, players.csv, matches.csv and events.csv are written",
    )
    parser.add_argument(
        "--pause-seconds",
        type=float,
        default=0.05,
        help="Pause between retries and batches of summary requests",
    )
    parser.add_argument(
        "--max-workers",
        type=int,
        default=12,
        help="Concurrent worker count for player summary requests",
    )
    return parser.parse_args()


def get_json(url: str, params: dict[str, Any] | None = None, retries: int = 3) -> Any:
    full_url = url
    if params:
        full_url = f"{url}?{urlencode(params)}"

    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        request = Request(full_url, headers=HEADERS)
        try:
            with urlopen(request, timeout=30) as response:
                payload = response.read().decode("utf-8")
                return json.loads(payload)
        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
            last_error = exc
            print(f"Retry {attempt}/{retries} for {full_url}: {exc}")
            time.sleep(2 ** (attempt - 1))

    raise RuntimeError(f"Failed to fetch {full_url}") from last_error


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def normalize_team_name(name: str) -> str:
    lowered = name.strip().lower()
    aliases = {
        "man city": "Manchester City",
        "man utd": "Manchester United",
        "nott'm forest": "Nottingham Forest",
        "spurs": "Tottenham Hotspur",
        "tottenham": "Tottenham Hotspur",
        "wolves": "Wolverhampton Wanderers",
        "brighton": "Brighton & Hove Albion",
        "newcastle": "Newcastle United",
        "west ham": "West Ham United",
        "ipswich": "Ipswich Town",
        "leicester": "Leicester City",
    }
    return aliases.get(lowered, name.strip())


def normalize_person_name(name: str) -> str:
    replacements = str.maketrans(
        {
            "Đ": "D",
            "đ": "d",
            "Ø": "O",
            "ø": "o",
            "Ł": "L",
            "ł": "l",
        }
    )
    replaced = name.translate(replacements)
    return (
        unicodedata.normalize("NFKD", replaced)
        .encode("ascii", "ignore")
        .decode("ascii")
        .strip()
    )


def build_teams(bootstrap: dict[str, Any]) -> tuple[list[dict[str, str]], dict[int, str]]:
    rows: list[dict[str, str]] = []
    team_name_by_id: dict[int, str] = {}

    for team in bootstrap["teams"]:
        team_name = normalize_team_name(team["name"])
        team_name_by_id[team["id"]] = team_name
        rows.append(
            {
                "name": team_name,
                "league": "Premier League",
                "country": "England",
            }
        )

    rows.sort(key=lambda row: row["name"])
    return rows, team_name_by_id


def build_players(
    bootstrap: dict[str, Any],
    team_name_by_id: dict[int, str],
) -> tuple[list[dict[str, str]], dict[int, dict[str, Any]]]:
    rows: list[dict[str, str]] = []
    player_info_by_id: dict[int, dict[str, Any]] = {}

    for player in bootstrap["elements"]:
        team_name = team_name_by_id.get(player["team"])
        if not team_name:
            continue

        full_name = normalize_person_name(f"{player['first_name']} {player['second_name']}".strip())
        row = {
            "name": full_name,
            "team_name": team_name,
            "position": POSITION_MAP.get(player["element_type"], "UNK"),
        }
        rows.append(row)
        player_info_by_id[player["id"]] = {
            **row,
            "team_id": player["team"],
        }

    rows.sort(key=lambda row: (row["team_name"], row["name"]))
    return rows, player_info_by_id


def build_matches(
    fixtures: list[dict[str, Any]],
    team_name_by_id: dict[int, str],
    season: str,
) -> tuple[list[dict[str, Any]], dict[int, dict[str, Any]], dict[int, list[dict[str, Any]]]]:
    match_rows: list[dict[str, Any]] = []
    match_by_fixture_id: dict[int, dict[str, Any]] = {}
    fixtures_by_gameweek: dict[int, list[dict[str, Any]]] = defaultdict(list)

    for fixture in fixtures:
        gameweek = fixture.get("event")
        if gameweek is not None:
            fixtures_by_gameweek[gameweek].append(fixture)

        if not fixture.get("finished"):
            continue
        if fixture.get("team_h_score") is None or fixture.get("team_a_score") is None:
            continue

        home_team = team_name_by_id.get(fixture["team_h"])
        away_team = team_name_by_id.get(fixture["team_a"])
        kickoff = fixture.get("kickoff_time") or ""
        match_date = kickoff[:10] if kickoff else ""
        if not home_team or not away_team or not match_date:
            continue

        row = {
            "match_date": match_date,
            "season": season,
            "home_team": home_team,
            "away_team": away_team,
            "home_score": fixture["team_h_score"],
            "away_score": fixture["team_a_score"],
        }
        match_rows.append(row)
        match_by_fixture_id[fixture["id"]] = row

    match_rows.sort(key=lambda row: (row["match_date"], row["home_team"], row["away_team"]))
    return match_rows, match_by_fixture_id, fixtures_by_gameweek


def build_fixtures(
    fixtures: list[dict[str, Any]],
    team_name_by_id: dict[int, str],
    season: str,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for fixture in fixtures:
        if fixture.get("finished"):
            continue

        home_team = team_name_by_id.get(fixture["team_h"])
        away_team = team_name_by_id.get(fixture["team_a"])
        kickoff = fixture.get("kickoff_time") or ""
        fixture_date = kickoff[:10] if kickoff else ""
        if not home_team or not away_team or not fixture_date:
            continue

        rows.append(
            {
                "fixture_date": fixture_date,
                "season": season,
                "home_team": home_team,
                "away_team": away_team,
            }
        )

    rows.sort(key=lambda row: (row["fixture_date"], row["home_team"], row["away_team"]))
    return rows


def build_events(
    player_ids: list[int],
    match_by_fixture_id: dict[int, dict[str, Any]],
    player_info_by_id: dict[int, dict[str, Any]],
    max_workers: int,
    pause_seconds: float,
) -> list[dict[str, Any]]:
    event_rows: list[dict[str, Any]] = []
    fetched = 0

    def fetch_history(player_id: int) -> tuple[int, list[dict[str, Any]]]:
        summary = get_json(f"{FPL_BASE}/element-summary/{player_id}/")
        return player_id, summary.get("history", [])

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_map = {executor.submit(fetch_history, player_id): player_id for player_id in player_ids}
        for future in as_completed(future_map):
            player_id, history_rows = future.result()
            player_info = player_info_by_id.get(player_id)
            if player_info is None:
                continue
            fetched += 1
            if fetched % 50 == 0:
                print(f"Fetched {fetched}/{len(player_ids)} player summaries...")
                time.sleep(pause_seconds)

            for history in history_rows:
                fixture_id = history.get("fixture")
                match = match_by_fixture_id.get(fixture_id)
                if match is None:
                    continue
                minute = int(history.get("minutes") or 0)
                minute = max(1, min(minute, 90))
                round_id = history.get("round", "")

                for stat_key, event_type in EVENT_STAT_MAP.items():
                    count = int(history.get(stat_key) or 0)
                    if count <= 0:
                        continue

                    for occurrence in range(count):
                        suffix = f" #{occurrence + 1}" if count > 1 else ""
                        event_rows.append(
                            {
                                "match_date": match["match_date"],
                                "season": match["season"],
                                "home_team": match["home_team"],
                                "away_team": match["away_team"],
                                "team_name": player_info["team_name"],
                                "player_name": player_info["name"],
                                "minute": minute,
                                "event_type": event_type,
                                "event_detail": f"{event_type} from FPL fixture history GW{round_id}{suffix}",
                            }
                        )

    event_rows.sort(
        key=lambda row: (
            row["match_date"],
            row["home_team"],
            row["away_team"],
            row["team_name"],
            row["player_name"],
            row["minute"],
            row["event_type"],
        )
    )
    return event_rows


def main() -> int:
    args = parse_args()
    out_dir = Path(args.out_dir)

    print("Fetching FPL bootstrap data...")
    bootstrap = get_json(f"{FPL_BASE}/bootstrap-static/")

    print("Building teams.csv...")
    team_rows, team_name_by_id = build_teams(bootstrap)
    write_csv(out_dir / "teams.csv", team_rows, ["name", "league", "country"])

    print("Building players.csv...")
    player_rows, player_info_by_id = build_players(bootstrap, team_name_by_id)
    write_csv(out_dir / "players.csv", player_rows, ["name", "team_name", "position"])
    player_ids = sorted(player_info_by_id.keys())

    print("Fetching fixtures...")
    fixtures = get_json(f"{FPL_BASE}/fixtures/")

    print("Building matches.csv...")
    match_rows, match_by_fixture_id, _fixtures_by_gameweek = build_matches(
        fixtures=fixtures,
        team_name_by_id=team_name_by_id,
        season=args.season,
    )
    write_csv(
        out_dir / "matches.csv",
        match_rows,
        ["match_date", "season", "home_team", "away_team", "home_score", "away_score"],
    )

    print("Building fixtures.csv...")
    fixture_rows = build_fixtures(
        fixtures=fixtures,
        team_name_by_id=team_name_by_id,
        season=args.season,
    )
    write_csv(
        out_dir / "fixtures.csv",
        fixture_rows,
        ["fixture_date", "season", "home_team", "away_team"],
    )

    print("Building events.csv...")
    event_rows = build_events(
        player_ids=player_ids,
        match_by_fixture_id=match_by_fixture_id,
        player_info_by_id=player_info_by_id,
        max_workers=args.max_workers,
        pause_seconds=args.pause_seconds,
    )
    write_csv(
        out_dir / "events.csv",
        event_rows,
        [
            "match_date",
            "season",
            "home_team",
            "away_team",
            "team_name",
            "player_name",
            "minute",
            "event_type",
            "event_detail",
        ],
    )

    print()
    print(f"teams.csv   -> {len(team_rows)} rows")
    print(f"players.csv -> {len(player_rows)} rows")
    print(f"matches.csv -> {len(match_rows)} rows")
    print(f"fixtures.csv -> {len(fixture_rows)} rows")
    print(f"events.csv  -> {len(event_rows)} rows")
    print(f"Output dir  -> {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
