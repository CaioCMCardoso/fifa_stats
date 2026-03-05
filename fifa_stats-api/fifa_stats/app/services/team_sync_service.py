from collections import defaultdict
from datetime import UTC, date, datetime, timedelta

from fifa_stats.app.db.repositories import DynamoPlayersRepository
from fifa_stats.app.schemas.player_stats_schema import UpsertDailyStatIn
from fifa_stats.app.services.fc_clubs_api_client import FcClubsApiClient
from fifa_stats.app.settings.configuration import Configuration

NAME_KEYS = ("name", "playerName", "proName", "personaName", "pro_name")
NUMBER_KEYS = ("shirtNumber", "shirt_number", "kitNumber", "jerseyNumber", "number")
POSITION_KEYS = ("position", "pos")
GOALS_KEYS = ("goals", "goalsScored", "goals_scored", "goal")
ASSISTS_KEYS = ("assists", "assist", "assistsMade", "assists_made")
CLUB_ID_KEYS = ("clubId", "club_id", "teamId", "team_id", "id")
MATCH_ID_KEYS = ("matchId", "match_id", "id")
MATCH_DATE_KEYS = ("utcDate", "playedAt", "date", "timestamp", "createdAt")
GF_KEYS = ("goalsFor", "goals_for", "teamGoals", "scored")
GA_KEYS = ("goalsAgainst", "goals_against", "conceded")


class TeamSyncService:
    def __init__(
        self,
        repo: DynamoPlayersRepository | None = None,
        fc_client: FcClubsApiClient | None = None,
        cfg: Configuration | None = None,
    ):
        self.cfg = cfg or Configuration.instance()
        self.repo = repo or DynamoPlayersRepository()
        self.fc_client = fc_client or FcClubsApiClient(self.cfg)
        self.logger = self.cfg.get_logger()

    def get_team_overview(self, max_matches: int = 6) -> dict:
        players = self.repo.list_players()
        local_totals = {
            "players": len(players),
            "goals": sum(p["total_goals"] for p in players),
            "assists": sum(p["total_assists"] for p in players),
        }

        try:
            club_id = self._resolve_club_id()
            club_details = self.fc_client.get_club_details(club_id, self.cfg.FC_CLUBS_API_PLATFORM)
            matches = self.fc_client.get_club_matches(
                club_id, self.cfg.FC_CLUBS_API_PLATFORM, limit=max_matches
            )
        except Exception as exc:
            self.logger.warning("failed to load external club overview: %s", exc)
            return {
                "external_available": False,
                "source": self.cfg.FC_CLUBS_API_SOURCE,
                "local_totals": local_totals,
                "team": None,
                "recent_matches": [],
                "message": "Nao foi possivel carregar dados externos do time.",
            }

        return {
            "external_available": True,
            "source": self.cfg.FC_CLUBS_API_SOURCE,
            "local_totals": local_totals,
            "team": _build_team_summary(club_details, club_id, self.cfg.FC_CLUBS_API_PLATFORM),
            "recent_matches": _build_recent_matches_summary(matches),
            "message": None,
        }

    def sync_recent_matches(self, days_back: int = 7, max_matches: int = 20, dry_run: bool = False) -> dict:
        club_id = self._resolve_club_id()
        matches = self.fc_client.get_club_matches(
            club_id=club_id,
            platform=self.cfg.FC_CLUBS_API_PLATFORM,
            limit=max_matches,
        )

        cutoff_day = date.today() - timedelta(days=days_back)
        aggregated: dict[tuple[str, str], dict] = defaultdict(
            lambda: {
                "player_name": "",
                "player_number": 0,
                "position": "N/A",
                "goals": 0,
                "assists": 0,
            }
        )

        for match in matches:
            match_day = _parse_day(match)
            if match_day is None or match_day < cutoff_day:
                continue

            players = _extract_players_from_match(match, club_id=club_id)
            for player in players:
                player_name = player["player_name"].strip()
                if not player_name:
                    continue

                key = (match_day.isoformat(), player_name.lower())
                current = aggregated[key]
                current["player_name"] = player_name
                current["player_number"] = max(
                    current["player_number"], int(player.get("player_number", 0))
                )
                current["position"] = player.get("position") or current["position"]
                current["goals"] += int(player.get("goals", 0))
                current["assists"] += int(player.get("assists", 0))

        rows_prepared = len(aggregated)
        rows_upserted = 0
        players_touched: set[str] = set()

        if not dry_run:
            for (day_iso, _), row in aggregated.items():
                payload = UpsertDailyStatIn(
                    day=date.fromisoformat(day_iso),
                    player_name=row["player_name"],
                    player_number=row["player_number"],
                    position=row["position"] or "N/A",
                    goals=row["goals"],
                    assists=row["assists"],
                )
                self.repo.upsert_daily_stat(payload)
                rows_upserted += 1
                players_touched.add(row["player_name"])
        else:
            players_touched = {row["player_name"] for row in aggregated.values()}

        return {
            "success": True,
            "dry_run": dry_run,
            "club_id": club_id,
            "days_back": days_back,
            "matches_scanned": len(matches),
            "rows_prepared": rows_prepared,
            "rows_upserted": rows_upserted,
            "players_touched": sorted(players_touched),
        }

    def _resolve_club_id(self) -> str:
        configured = self.cfg.FC_CLUBS_API_CLUB_ID.strip()
        if configured:
            return configured

        name = self.cfg.FC_CLUBS_API_CLUB_NAME.strip()
        if not name:
            raise ValueError("Configure FC_CLUBS_API_CLUB_ID ou FC_CLUBS_API_CLUB_NAME.")

        clubs = self.fc_client.search_club(name=name, platform=self.cfg.FC_CLUBS_API_PLATFORM)
        if not clubs:
            raise ValueError(f"Nenhum clube encontrado para '{name}'.")

        best = clubs[0]
        club_id = (
            best.get("clubId")
            or best.get("club_id")
            or best.get("id")
            or best.get("teamId")
            or best.get("team_id")
        )
        if not club_id:
            raise ValueError("Resposta de busca nao contem identificador do clube.")

        return str(club_id)


def _build_team_summary(club_details: dict, club_id: str, platform: str) -> dict:
    return {
        "club_id": club_id,
        "name": _pick_str(club_details, ("name", "clubName", "teamName")),
        "platform": platform,
        "region": _pick_str(club_details, ("region", "country")),
        "members": _pick_int(club_details, ("members", "memberCount", "totalMembers")),
        "wins": _pick_int(club_details, ("wins", "win", "victories")),
        "draws": _pick_int(club_details, ("draws", "ties")),
        "losses": _pick_int(club_details, ("losses", "defeats")),
        "points": _pick_int(club_details, ("points", "pts")),
    }


def _build_recent_matches_summary(matches: list[dict]) -> list[dict]:
    output: list[dict] = []
    for row in matches[:6]:
        goals_for = _pick_int(row, GF_KEYS)
        goals_against = _pick_int(row, GA_KEYS)
        match_day = _parse_day(row)
        output.append(
            {
                "match_id": _pick_str(row, MATCH_ID_KEYS),
                "day": match_day.isoformat() if match_day else None,
                "goals_for": goals_for,
                "goals_against": goals_against,
                "result": _infer_result(goals_for, goals_against),
                "opponent": _pick_str(row, ("opponentName", "opponent", "rivalName")),
            }
        )
    return output


def _infer_result(goals_for: int | None, goals_against: int | None) -> str | None:
    if goals_for is None or goals_against is None:
        return None
    if goals_for > goals_against:
        return "W"
    if goals_for < goals_against:
        return "L"
    return "D"


def _extract_players_from_match(match: dict, club_id: str) -> list[dict]:
    team_nodes = _extract_team_nodes(match, club_id)
    candidates = team_nodes if team_nodes else [match]

    out: list[dict] = []
    seen: set[tuple[str, int, str, int, int]] = set()
    for node in candidates:
        for player in _extract_players_from_node(node):
            signature = (
                player["player_name"].lower(),
                player["player_number"],
                player["position"],
                player["goals"],
                player["assists"],
            )
            if signature not in seen:
                seen.add(signature)
                out.append(player)

    return out


def _extract_team_nodes(match: dict, club_id: str) -> list[dict]:
    nodes: list[dict] = []
    if not club_id:
        return nodes

    for value in match.values():
        if isinstance(value, dict):
            if _dict_has_club_id(value, club_id):
                nodes.append(value)
            nodes.extend(_extract_team_nodes(value, club_id))
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    if _dict_has_club_id(item, club_id):
                        nodes.append(item)
                    nodes.extend(_extract_team_nodes(item, club_id))
    return nodes


def _dict_has_club_id(payload: dict, club_id: str) -> bool:
    for key in CLUB_ID_KEYS:
        value = payload.get(key)
        if value is not None and str(value) == str(club_id):
            return True
    return False


def _extract_players_from_node(node: object) -> list[dict]:
    players: list[dict] = []
    if isinstance(node, list):
        for item in node:
            players.extend(_extract_players_from_node(item))
        return players

    if not isinstance(node, dict):
        return players

    stats = node.get("stats")
    stats_obj = stats if isinstance(stats, dict) else {}
    name = _pick_str(node, NAME_KEYS)
    goals = _pick_int(node, GOALS_KEYS, fallback=0)
    assists = _pick_int(node, ASSISTS_KEYS, fallback=0)

    if goals is None:
        goals = _pick_int(stats_obj, GOALS_KEYS, fallback=0)
    if assists is None:
        assists = _pick_int(stats_obj, ASSISTS_KEYS, fallback=0)

    if name:
        players.append(
            {
                "player_name": name.strip(),
                "player_number": _pick_int(node, NUMBER_KEYS, fallback=0) or 0,
                "position": _pick_str(node, POSITION_KEYS, fallback="N/A") or "N/A",
                "goals": goals or 0,
                "assists": assists or 0,
            }
        )

    for value in node.values():
        players.extend(_extract_players_from_node(value))

    return players


def _parse_day(match: dict) -> date | None:
    raw = _pick_any(match, MATCH_DATE_KEYS)
    if raw is None:
        return None

    if isinstance(raw, (int, float)):
        timestamp = raw / 1000 if raw > 1_000_000_000_000 else raw
        try:
            return datetime.fromtimestamp(timestamp, tz=UTC).date()
        except Exception:
            return None

    if isinstance(raw, str):
        try:
            return datetime.fromisoformat(raw.replace("Z", "+00:00")).date()
        except ValueError:
            pass

        if raw.isdigit():
            return _parse_day({"timestamp": int(raw)})

    return None


def _pick_any(payload: dict, keys: tuple[str, ...]) -> object | None:
    for key in keys:
        if key in payload and payload[key] not in (None, ""):
            return payload[key]
    return None


def _pick_str(payload: dict, keys: tuple[str, ...], fallback: str | None = None) -> str | None:
    raw = _pick_any(payload, keys)
    if raw is None:
        return fallback
    return str(raw)


def _pick_int(
    payload: dict, keys: tuple[str, ...], fallback: int | None = None
) -> int | None:
    raw = _pick_any(payload, keys)
    if raw is None:
        return fallback
    try:
        return int(raw)
    except (TypeError, ValueError):
        return fallback
