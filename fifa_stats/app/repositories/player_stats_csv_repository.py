import csv
import os
from typing import Dict, List

from fifa_stats.app.schemas.player_stats_schema import UpsertDailyStatIn

CSV_HEADERS = ["day", "player_name", "player_number", "position", "goals", "assists"]


class PlayerStatsCsvRepository:
    def __init__(self, csv_path: str):
        self.csv_path = csv_path

    def _ensure_csv_exists(self) -> None:
        os.makedirs(os.path.dirname(self.csv_path) or ".", exist_ok=True)
        if not os.path.exists(self.csv_path):
            with open(self.csv_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
                writer.writeheader()

    def _read_all_rows(self) -> List[dict]:
        self._ensure_csv_exists()
        with open(self.csv_path, "r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            return list(reader)

    def _write_all_rows(self, rows: List[dict]) -> None:
        self._ensure_csv_exists()
        with open(self.csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
            writer.writeheader()
            writer.writerows(rows)

    def upsert_daily_stat(self, payload: UpsertDailyStatIn) -> dict:
        rows = self._read_all_rows()

        key_day = payload.day.isoformat()
        key_name = payload.player_name.strip()

        updated = False
        for r in rows:
            if r.get("day") == key_day and r.get("player_name") == key_name:
                r["player_number"] = str(payload.player_number)
                r["position"] = payload.position.strip()
                r["goals"] = str(payload.goals)
                r["assists"] = str(payload.assists)
                updated = True
                break

        if not updated:
            rows.append(
                {
                    "day": key_day,
                    "player_name": key_name,
                    "player_number": str(payload.player_number),
                    "position": payload.position.strip(),
                    "goals": str(payload.goals),
                    "assists": str(payload.assists),
                }
            )

        self._write_all_rows(rows)

        return {
            "success": True,
            "action": "updated" if updated else "created",
            "day": key_day,
            "player_name": key_name,
            "player_number": payload.player_number,
            "position": payload.position,
            "goals": payload.goals,
            "assists": payload.assists,
        }

    def list_players(self) -> List[dict]:
        rows = self._read_all_rows()

        players: Dict[str, dict] = {}

        for r in rows:
            name = (r.get("player_name") or "").strip()
            if not name:
                continue

            number = int(r.get("player_number") or 0)
            position = (r.get("position") or "").strip()
            goals = int(r.get("goals") or 0)
            assists = int(r.get("assists") or 0)
            day = r.get("day") or ""

            if name not in players:
                players[name] = {
                    "name": name,
                    "number": number,
                    "position": position,
                    "total_goals": 0,
                    "total_assists": 0,
                    "history": [],
                }

            players[name]["number"] = number or players[name]["number"]
            players[name]["position"] = position or players[name]["position"]

            players[name]["total_goals"] += goals
            players[name]["total_assists"] += assists
            players[name]["history"].append({"day": day, "goals": goals, "assists": assists})

        out = list(players.values())
        for p in out:
            p["history"] = sorted(p["history"], key=lambda x: x["day"])
        out.sort(key=lambda x: x["name"].lower())

        return out