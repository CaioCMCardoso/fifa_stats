from fastapi import Request
from fastapi.responses import JSONResponse
from fifa_stats.app.exceptions.exceptions import AppException


def register_exception_handlers(app):
    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"success": False, "message": exc.message},
        )