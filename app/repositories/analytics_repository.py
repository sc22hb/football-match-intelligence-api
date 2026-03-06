"""repository queries used by analytics endpoints."""

from sqlalchemy import Select, func, or_, select
from sqlalchemy.orm import Session

from app.models.event import Event
from app.models.match import Match
from app.models.player import Player
from app.models.team import Team


class AnalyticsRepository:
    def list_all_teams(self, db: Session) -> list[Team]:
        stmt: Select[tuple[Team]] = select(Team).order_by(Team.id.asc())
        return list(db.execute(stmt).scalars().all())

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

    def list_players_by_ids(self, db: Session, player_ids: set[int]) -> list[Player]:
        if not player_ids:
            return []
        stmt: Select[tuple[Player]] = select(Player).where(Player.id.in_(player_ids))
        return list(db.execute(stmt).scalars().all())

    def list_goal_events(self, db: Session, season: str | None = None) -> list[Event]:
        stmt: Select[tuple[Event]] = (
            select(Event)
            .join(Match, Match.id == Event.match_id)
            .where(func.lower(Event.event_type) == "goal")
            .order_by(Event.id.asc())
        )
        if season is not None:
            stmt = stmt.where(Match.season == season)
        return list(db.execute(stmt).scalars().all())
