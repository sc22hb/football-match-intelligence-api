"""repository queries used by analytics endpoints."""

from sqlalchemy import Select, or_, select
from sqlalchemy.orm import Session

from app.models.match import Match
from app.models.team import Team


class AnalyticsRepository:
    def list_recent_team_matches(self, db: Session, team_id: int, limit: int = 5) -> list[Match]:
        stmt: Select[tuple[Match]] = (
            select(Match)
            .where(or_(Match.home_team_id == team_id, Match.away_team_id == team_id))
            .order_by(Match.match_date.desc(), Match.id.desc())
            .limit(limit)
        )
        return list(db.execute(stmt).scalars().all())

    def list_matches(self, db: Session, season: str | None = None) -> list[Match]:
        stmt: Select[tuple[Match]] = select(Match).order_by(Match.match_date.asc(), Match.id.asc())
        if season is not None:
            stmt = stmt.where(Match.season == season)
        return list(db.execute(stmt).scalars().all())

    def list_teams_by_ids(self, db: Session, team_ids: set[int]) -> list[Team]:
        if not team_ids:
            return []
        stmt: Select[tuple[Team]] = select(Team).where(Team.id.in_(team_ids))
        return list(db.execute(stmt).scalars().all())
