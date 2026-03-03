from dataclasses import dataclass
from datetime import datetime, timezone

from fifa_stats.app.schemas.player_stats_schema import UpsertDailyStatIn


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class PlayerDailyStatItem:
    team_id: str
    player_id: str
    day: str
    name: str
    shirt_number: int
    position: str
    goals: int
    assists: int
    created_at: str
    updated_at: str

    @classmethod
    def from_payload(
        cls,
        payload: UpsertDailyStatIn,
        team_id: str,
        created_at: str | None = None,
    ) -> "PlayerDailyStatItem":
        timestamp = now_iso()
        normalized_name = payload.player_name.strip()

        return cls(
            team_id=team_id,
            player_id=f"{payload.day.isoformat()}#{normalized_name.lower()}",
            day=payload.day.isoformat(),
            name=normalized_name,
            shirt_number=payload.player_number,
            position=payload.position.strip(),
            goals=payload.goals,
            assists=payload.assists,
            created_at=created_at or timestamp,
            updated_at=timestamp,
        )

    @classmethod
    def from_item(cls, item: dict) -> "PlayerDailyStatItem":
        return cls(
            team_id=item["team_id"],
            player_id=item["player_id"],
            day=item["day"],
            name=item["name"],
            shirt_number=int(item.get("shirt_number", 0)),
            position=item.get("position", ""),
            goals=int(item.get("goals", 0)),
            assists=int(item.get("assists", 0)),
            created_at=item.get("created_at", ""),
            updated_at=item.get("updated_at", ""),
        )

    def to_item(self) -> dict:
        return {
            "team_id": self.team_id,
            "player_id": self.player_id,
            "day": self.day,
            "name": self.name,
            "shirt_number": self.shirt_number,
            "position": self.position,
            "goals": self.goals,
            "assists": self.assists,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
