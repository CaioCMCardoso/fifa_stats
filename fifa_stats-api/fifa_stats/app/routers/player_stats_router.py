from fastapi import APIRouter

from fifa_stats.app.exceptions.exceptions import AppException
from fifa_stats.app.settings.configuration import Configuration
from fifa_stats.app.schemas.player_stats_schema import UpsertDailyStatIn, PlayerOut
from fifa_stats.app.repositories.player_stats_csv_repository import PlayerStatsCsvRepository

router = APIRouter(prefix="", tags=["players"])

cfg = Configuration.instance()
repo = PlayerStatsCsvRepository(cfg.CSV_PATH)


@router.get("/players", response_model=list[PlayerOut])
def get_players():
    return repo.list_players()


@router.post("/players/stats")
def post_player_stats(payload: UpsertDailyStatIn):
    return repo.upsert_daily_stat(payload)


@router.delete("/players/{player_name}")
def delete_player(player_name: str):
    result = repo.delete_player(player_name)
    if not result["success"]:
        raise AppException("Jogador não encontrado", status_code=404)
    return result
