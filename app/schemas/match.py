"""pydantic schemas for match create/read/update/list payloads."""

from datetime import date

from pydantic import BaseModel, ConfigDict, Field, model_validator


class MatchBase(BaseModel):
    home_team_id: int = Field(ge=1)
    away_team_id: int = Field(ge=1)
    home_score: int = Field(default=0, ge=0)
    away_score: int = Field(default=0, ge=0)
    match_date: date
    season: str = Field(min_length=1, max_length=20)

    @model_validator(mode="after")
    def validate_distinct_teams(self) -> "MatchBase":
        if self.home_team_id == self.away_team_id:
            raise ValueError("home_team_id and away_team_id must be different")
        return self


class MatchCreate(MatchBase):
    pass


class MatchUpdate(BaseModel):
    home_team_id: int | None = Field(default=None, ge=1)
    away_team_id: int | None = Field(default=None, ge=1)
    home_score: int | None = Field(default=None, ge=0)
    away_score: int | None = Field(default=None, ge=0)
    match_date: date | None = None
    season: str | None = Field(default=None, min_length=1, max_length=20)


class MatchRead(MatchBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class MatchListResponse(BaseModel):
    items: list[MatchRead]
    total: int
    skip: int
    limit: int
