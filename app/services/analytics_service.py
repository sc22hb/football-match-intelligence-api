"""service orchestration for analytics endpoints."""

from sqlalchemy.orm import Session

from app.analytics.team_form import calculate_team_form
from app.repositories.analytics_repository import AnalyticsRepository
from app.repositories.team_repository import TeamRepository
from app.schemas.analytics import TeamFormResponse
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
            recent_results=metrics["recent_results"],
        )
