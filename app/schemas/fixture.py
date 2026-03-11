"""pydantic schemas for fixture read/list payloads."""

from datetime import date

from pydantic import BaseModel, ConfigDict, Field, model_validator


class FixtureBase(BaseModel):
    home_team_id: int = Field(ge=1)
    away_team_id: int = Field(ge=1)
    fixture_date: date
    season: str = Field(min_length=1, max_length=20)

    @model_validator(mode="after")
    def validate_distinct_teams(self) -> "FixtureBase":
        if self.home_team_id == self.away_team_id:
            raise ValueError("home_team_id and away_team_id must be different")
        return self


class FixtureRead(FixtureBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class FixtureListResponse(BaseModel):
    items: list[FixtureRead]
    total: int
    skip: int
    limit: int
