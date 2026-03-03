from boto3.dynamodb.conditions import Key

from fifa_stats.app.db.connector import DynamoConnector
from fifa_stats.app.db.models import PlayerDailyStatItem
from fifa_stats.app.schemas.player_stats_schema import UpsertDailyStatIn


class DynamoPlayersRepository:
    def __init__(self, connector: DynamoConnector | None = None):
        self.connector = connector or DynamoConnector()
        self.team_id = self.connector.team_id
        self.table = self.connector.table

    def _query_all_team_items(self) -> list[dict]:
        response = self.table.query(KeyConditionExpression=Key("team_id").eq(self.team_id))
        items = response.get("Items", [])

        while "LastEvaluatedKey" in response:
            response = self.table.query(
                KeyConditionExpression=Key("team_id").eq(self.team_id),
                ExclusiveStartKey=response["LastEvaluatedKey"],
            )
            items.extend(response.get("Items", []))

        return items

    def list_players(self) -> list[dict]:
        players: dict[str, dict] = {}

        for item in self._query_all_team_items():
            stat = PlayerDailyStatItem.from_item(item)

            if stat.name not in players:
                players[stat.name] = {
                    "name": stat.name,
                    "number": stat.shirt_number,
                    "position": stat.position,
                    "total_goals": 0,
                    "total_assists": 0,
                    "history": [],
                }

            players[stat.name]["number"] = stat.shirt_number or players[stat.name]["number"]
            players[stat.name]["position"] = stat.position or players[stat.name]["position"]
            players[stat.name]["total_goals"] += stat.goals
            players[stat.name]["total_assists"] += stat.assists
            players[stat.name]["history"].append(
                {"day": stat.day, "goals": stat.goals, "assists": stat.assists}
            )

        output = list(players.values())
        for player in output:
            player["history"] = sorted(player["history"], key=lambda row: row["day"])

        output.sort(key=lambda row: row["name"].lower())
        return output

    def upsert_daily_stat(self, payload: UpsertDailyStatIn) -> dict:
        draft = PlayerDailyStatItem.from_payload(payload=payload, team_id=self.team_id)
        existing = self.table.get_item(
            Key={"team_id": self.team_id, "player_id": draft.player_id}
        ).get("Item")

        stat = PlayerDailyStatItem.from_payload(
            payload=payload,
            team_id=self.team_id,
            created_at=(existing or {}).get("created_at"),
        )

        self.table.put_item(Item=stat.to_item())

        return {
            "success": True,
            "action": "updated" if existing else "created",
            "day": stat.day,
            "player_name": stat.name,
            "player_number": stat.shirt_number,
            "position": stat.position,
            "goals": stat.goals,
            "assists": stat.assists,
        }

    def delete_player(self, player_name: str) -> dict:
        key_name = player_name.strip()
        items = self._query_all_team_items()
        items_to_delete = [
            item for item in items if (item.get("name") or "").strip() == key_name
        ]

        if not items_to_delete:
            return {"success": False, "deleted_rows": 0, "player_name": key_name}

        with self.table.batch_writer() as batch:
            for item in items_to_delete:
                batch.delete_item(
                    Key={"team_id": item["team_id"], "player_id": item["player_id"]}
                )

        return {
            "success": True,
            "deleted_rows": len(items_to_delete),
            "player_name": key_name,
        }
