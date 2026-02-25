from fastapi import APIRouter
import os

from fifa_stats.app.settings.configuration import Configuration

router = APIRouter(prefix="", tags=["health"])

cfg = Configuration.instance()


@router.get("/health")
def health():
    folder = os.path.dirname(cfg.CSV_PATH) or "."
    os.makedirs(folder, exist_ok=True)
    return {"status": "ok"}