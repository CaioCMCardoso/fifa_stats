from fastapi import APIRouter

from fifa_stats.app.exceptions.exceptions import AppException
from fifa_stats.app.schemas.team_schema import TeamSyncIn
from fifa_stats.app.services.team_sync_service import TeamSyncService

router = APIRouter(prefix="/team", tags=["team"])

service = TeamSyncService()


@router.get("/overview")
def get_team_overview():
    return service.get_team_overview()


@router.post("/sync")
def post_team_sync(payload: TeamSyncIn):
    try:
        return service.sync_recent_matches(
            days_back=payload.days_back,
            max_matches=payload.max_matches,
            dry_run=payload.dry_run,
        )
    except ValueError as exc:
        raise AppException(str(exc), status_code=400) from exc
