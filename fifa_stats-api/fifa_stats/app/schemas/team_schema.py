from pydantic import BaseModel, Field


class TeamSyncIn(BaseModel):
    days_back: int = Field(default=7, ge=1, le=60)
    max_matches: int = Field(default=20, ge=1, le=200)
    dry_run: bool = False
