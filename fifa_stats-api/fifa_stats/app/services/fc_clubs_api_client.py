import json
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from fifa_stats.app.settings.configuration import Configuration


class FcClubsApiClient:
    def __init__(self, cfg: Configuration | None = None):
        self.cfg = cfg or Configuration.instance()
        self.base_url = self.cfg.FC_CLUBS_API_BASE_URL.rstrip("/")
        self.timeout_seconds = self.cfg.FC_CLUBS_API_TIMEOUT_SECONDS

    def search_club(self, name: str, platform: str) -> list[dict]:
        payload = self._get_json(
            path=self.cfg.FC_CLUBS_SEARCH_PATH,
            query={
                "name": name,
                "clubName": name,
                "platform": platform,
            },
        )
        return _as_list(payload)

    def get_club_details(self, club_id: str, platform: str) -> dict:
        path = self.cfg.FC_CLUBS_DETAILS_PATH.format(club_id=club_id)
        payload = self._get_json(path=path, query={"platform": platform})
        return _as_dict(payload)

    def get_club_matches(self, club_id: str, platform: str, limit: int = 20) -> list[dict]:
        path = self.cfg.FC_CLUBS_MATCHES_PATH.format(club_id=club_id)
        payload = self._get_json(path=path, query={"platform": platform, "limit": limit})
        rows = _as_list(payload)
        return rows[:limit]

    def _get_json(self, path: str, query: dict[str, object] | None = None) -> dict | list:
        normalized_path = path if path.startswith("/") else f"/{path}"
        encoded_query = urlencode({k: v for k, v in (query or {}).items() if v not in (None, "")})
        url = f"{self.base_url}{normalized_path}"
        if encoded_query:
            url = f"{url}?{encoded_query}"

        req = Request(url=url, method="GET", headers={"Accept": "application/json"})
        with urlopen(req, timeout=self.timeout_seconds) as response:
            payload = response.read().decode("utf-8")

        data = json.loads(payload)
        if isinstance(data, dict):
            for key in ("data", "result", "results"):
                nested = data.get(key)
                if isinstance(nested, (dict, list)):
                    return nested

        return data


def _as_list(payload: dict | list) -> list[dict]:
    if isinstance(payload, list):
        return [row for row in payload if isinstance(row, dict)]
    if isinstance(payload, dict):
        for key in ("items", "clubs", "matches"):
            nested = payload.get(key)
            if isinstance(nested, list):
                return [row for row in nested if isinstance(row, dict)]
    return []


def _as_dict(payload: dict | list) -> dict:
    if isinstance(payload, dict):
        return payload
    if isinstance(payload, list):
        for row in payload:
            if isinstance(row, dict):
                return row
    return {}
