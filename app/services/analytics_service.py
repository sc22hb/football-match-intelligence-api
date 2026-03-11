"""service orchestration for analytics endpoints."""

from datetime import UTC, datetime

from app.analytics.clutch_impact import ClutchEventContext, calculate_clutch_impact
from app.analytics.player_impact import calculate_player_impact
from app.analytics.league_table import calculate_league_table
from app.analytics.most_assists import calculate_most_assists
from app.analytics.team_strength import calculate_team_strength
from app.analytics.top_scorers import calculate_top_scorers
from sqlalchemy.orm import Session

from app.analytics.team_form import calculate_team_form
from app.core.config import get_settings
from app.repositories.analytics_repository import AnalyticsRepository
from app.repositories.team_repository import TeamRepository
from app.schemas.analytics import (
    AnalyticsMetadata,
    ClutchImpactResponse,
    LeagueTableResponse,
    MostAssistsResponse,
    PlayerImpactResponse,
    TeamFormResponse,
    TeamStrengthResponse,
    TopScorersResponse,
)
from app.services.errors import NotFoundError


class AnalyticsService:
    def __init__(
        self,
        repository: AnalyticsRepository | None = None,
        team_repository: TeamRepository | None = None,
    ) -> None:
        self.repository = repository or AnalyticsRepository()
        self.team_repository = team_repository or TeamRepository()
        self.settings = get_settings()

    def get_team_form(self, db: Session, team_id: int) -> TeamFormResponse:
        team = self.team_repository.get_by_id(db=db, team_id=team_id)
        if team is None:
            raise NotFoundError(f"Team with id={team_id} was not found")

        recent_matches = self.repository.list_recent_team_matches(db=db, team_id=team_id, limit=5)
        metrics = calculate_team_form(matches=recent_matches, team_id=team_id)

        return TeamFormResponse(
            team_id=team_id,
            matches_considered=metrics["matches_considered"],
            wins=metrics["wins"],
            draws=metrics["draws"],
            losses=metrics["losses"],
            points=metrics["points"],
            form_score=metrics["form_score"],
            explanation_summary=metrics["explanation_summary"],
            recent_results=metrics["recent_results"],
            metadata=self._metadata(),
        )

    def get_team_strength(self, db: Session, season: str | None = None) -> TeamStrengthResponse:
        base_rating = 1500.0
        k_factor = 32.0

        teams = self.repository.list_all_teams(db=db)
        team_ids = {team.id for team in teams}
        names_by_id = {team.id: team.name for team in teams}

        matches = self.repository.list_matches(db=db, season=season)
        ratings = calculate_team_strength(
            matches=matches,
            team_ids=team_ids,
            base_rating=base_rating,
            k_factor=k_factor,
        )

        rows = [
            {
                "team_id": team_id,
                "team_name": names_by_id.get(team_id, f"team-{team_id}"),
                "rating": values["rating"],
                "matches_played": values["matches_played"],
            }
            for team_id, values in ratings.items()
        ]
        rows.sort(key=lambda r: (-r["rating"], r["team_id"]))

        for idx, row in enumerate(rows, start=1):
            row["rank"] = idx

        return TeamStrengthResponse(
            season=season,
            base_rating=base_rating,
            k_factor=k_factor,
            teams=rows,
            metadata=self._metadata(),
        )

    def get_league_table(self, db: Session, season: str | None = None) -> LeagueTableResponse:
        matches = self.repository.list_matches(db=db, season=season)
        raw_table = calculate_league_table(matches=matches)

        team_ids = {row["team_id"] for row in raw_table}
        teams = self.repository.list_teams_by_ids(db=db, team_ids=team_ids)
        names_by_id = {team.id: team.name for team in teams}

        table_rows = [
            {
                **row,
                "team_name": names_by_id.get(row["team_id"], f"team-{row['team_id']}"),
            }
            for row in raw_table
        ]

        return LeagueTableResponse(
            season=season,
            matches_considered=len(matches),
            table=table_rows,
            metadata=self._metadata(),
        )

    def get_top_scorers(self, db: Session, season: str | None = None, limit: int = 10) -> TopScorersResponse:
        goal_events = self.repository.list_goal_events(db=db, season=season)
        ranked = calculate_top_scorers(events=goal_events)[:limit]

        player_ids = {row["player_id"] for row in ranked}
        team_ids = {row["team_id"] for row in ranked}
        players = self.repository.list_players_by_ids(db=db, player_ids=player_ids)
        teams = self.repository.list_teams_by_ids(db=db, team_ids=team_ids)

        player_names = {player.id: player.name for player in players}
        team_names = {team.id: team.name for team in teams}

        top_rows = [
            {
                **row,
                "player_name": player_names.get(row["player_id"], f"player-{row['player_id']}"),
                "team_name": team_names.get(row["team_id"], f"team-{row['team_id']}"),
            }
            for row in ranked
        ]

        return TopScorersResponse(
            season=season,
            events_considered=len(goal_events),
            top_scorers=top_rows,
            metadata=self._metadata(),
        )

    def get_most_assists(self, db: Session, season: str | None = None, limit: int = 10) -> MostAssistsResponse:
        assist_events = self.repository.list_assist_events(db=db, season=season)
        ranked = calculate_most_assists(events=assist_events)[:limit]

        player_ids = {row["player_id"] for row in ranked}
        team_ids = {row["team_id"] for row in ranked}
        players = self.repository.list_players_by_ids(db=db, player_ids=player_ids)
        teams = self.repository.list_teams_by_ids(db=db, team_ids=team_ids)

        player_names = {player.id: player.name for player in players}
        team_names = {team.id: team.name for team in teams}

        rows = [
            {
                **row,
                "player_name": player_names.get(row["player_id"], f"player-{row['player_id']}"),
                "team_name": team_names.get(row["team_id"], f"team-{row['team_id']}"),
            }
            for row in ranked
        ]

        return MostAssistsResponse(
            season=season,
            events_considered=len(assist_events),
            most_assists=rows,
            metadata=self._metadata(),
        )

    def get_player_impact(self, db: Session, season: str | None = None, limit: int = 20) -> PlayerImpactResponse:
        events = self.repository.list_events(db=db, season=season)
        ranked = calculate_player_impact(events=events)[:limit]

        player_ids = {row["player_id"] for row in ranked}
        team_ids = {row["team_id"] for row in ranked}
        players = self.repository.list_players_by_ids(db=db, player_ids=player_ids)
        teams = self.repository.list_teams_by_ids(db=db, team_ids=team_ids)

        player_names = {player.id: player.name for player in players}
        team_names = {team.id: team.name for team in teams}

        rows = [
            {
                **row,
                "player_name": player_names.get(row["player_id"], f"player-{row['player_id']}"),
                "team_name": team_names.get(row["team_id"], f"team-{row['team_id']}"),
            }
            for row in ranked
        ]

        return PlayerImpactResponse(
            season=season,
            events_considered=len(events),
            players=rows,
            metadata=self._metadata(),
        )

    def get_clutch_impact(self, db: Session, season: str | None = None, limit: int = 20) -> ClutchImpactResponse:
        events = self.repository.list_events(db=db, season=season)
        matches = self.repository.list_matches(db=db, season=season)
        match_by_id = {match.id: match for match in matches}

        contexts: list[ClutchEventContext] = []
        for event in events:
            match = match_by_id.get(event.match_id)
            if match is None:
                continue

            if event.team_id == match.home_team_id:
                goals_for = match.home_score
                goals_against = match.away_score
            else:
                goals_for = match.away_score
                goals_against = match.home_score

            if goals_for < goals_against:
                points_awarded = 0
            elif goals_for == goals_against:
                points_awarded = 1
            else:
                points_awarded = 3

            contexts.append(
                ClutchEventContext(
                    player_id=event.player_id,
                    team_id=event.team_id,
                    match_id=event.match_id,
                    minute=event.minute,
                    event_type=event.event_type,
                    points_awarded=points_awarded,
                )
            )

        ranked = calculate_clutch_impact(event_contexts=contexts)[:limit]

        player_ids = {row["player_id"] for row in ranked}
        team_ids = {row["team_id"] for row in ranked}
        players = self.repository.list_players_by_ids(db=db, player_ids=player_ids)
        teams = self.repository.list_teams_by_ids(db=db, team_ids=team_ids)

        player_names = {player.id: player.name for player in players}
        team_names = {team.id: team.name for team in teams}

        rows = [
            {
                **row,
                "player_name": player_names.get(row["player_id"], f"player-{row['player_id']}"),
                "team_name": team_names.get(row["team_id"], f"team-{row['team_id']}"),
            }
            for row in ranked
        ]

        return ClutchImpactResponse(
            season=season,
            events_considered=len(events),
            methodology=(
                "Clutch score is based on points won from goal and assist contributions only. "
                "Goals carry full weight and assists carry reduced weight, with each player's share "
                "taken from the team's final points in that match."
            ),
            players=rows,
            metadata=self._metadata(),
        )

    def _metadata(self) -> AnalyticsMetadata:
        return AnalyticsMetadata(
            data_source=self.settings.data_source,
            dataset_name=self.settings.dataset_name,
            dataset_version=self.settings.dataset_version,
            computed_at=datetime.now(UTC),
        )
