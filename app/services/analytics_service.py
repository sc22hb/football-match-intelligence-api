"""service orchestration for analytics endpoints."""

from app.analytics.league_table import calculate_league_table
from app.analytics.team_strength import calculate_team_strength
from app.analytics.top_scorers import calculate_top_scorers
from sqlalchemy.orm import Session

from app.analytics.team_form import calculate_team_form
from app.repositories.analytics_repository import AnalyticsRepository
from app.repositories.team_repository import TeamRepository
from app.schemas.analytics import (
    LeagueTableResponse,
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
        )
