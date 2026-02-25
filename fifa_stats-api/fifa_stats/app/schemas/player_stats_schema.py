from datetime import date
from pydantic import BaseModel, Field


class UpsertDailyStatIn(BaseModel):
    day: date
    player_name: str = Field(..., min_length=1, max_length=120)

    player_number: int = Field(..., ge=0, le=99)
    position: str = Field(..., min_length=1, max_length=20)  # "ST", "CM", "GK" etc.

    goals: int = Field(default=0, ge=0)
    assists: int = Field(default=0, ge=0)


class DailyStatOut(BaseModel):
    day: date
    goals: int
    assists: int


class PlayerOut(BaseModel):
    name: str
    number: int
    position: str

    total_goals: int
    total_assists: int
    history: list[DailyStatOut]