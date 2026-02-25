import uvicorn
from fastapi import FastAPI

from fifa_stats.app.settings.configuration import Configuration
from fifa_stats.app.routers.health_router import router as health_router
from fifa_stats.app.routers.player_stats_router import router as player_stats_router

cfg = Configuration.instance()
logger = cfg.get_logger()

app = FastAPI(title=cfg.APP_NAME, version="0.1.0")

app.include_router(health_router)
app.include_router(player_stats_router)


@app.get("/")
def root():
    return {"service": cfg.APP_NAME, "env": cfg.ENV}


def iniciar_servico():
    logger.info("Starting service %s", cfg.APP_NAME)
    uvicorn.run("fifa_stats.app.main:app", host="0.0.0.0", port=8000, reload=cfg.DEBUG)