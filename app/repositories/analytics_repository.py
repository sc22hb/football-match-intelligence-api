"""repository queries used by analytics endpoints."""

from sqlalchemy import Select, or_, select
from sqlalchemy.orm import Session

from app.models.match import Match


class AnalyticsRepository:
    def list_recent_team_matches(self, db: Session, team_id: int, limit: int = 5) -> list[Match]:
        stmt: Select[tuple[Match]] = (
            select(Match)
            .where(or_(Match.home_team_id == team_id, Match.away_team_id == team_id))
            .order_by(Match.match_date.desc(), Match.id.desc())
            .limit(limit)
        )
        return list(db.execute(stmt).scalars().all())
