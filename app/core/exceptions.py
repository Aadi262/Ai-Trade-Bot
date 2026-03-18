from datetime import datetime, timezone
from fastapi import Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel


class TradingBotError(BaseModel):
    error_code: str
    message: str
    request_id: str
    timestamp: datetime


class AppError(Exception):
    def __init__(self, message: str, status_code: int = 400, error_code: str = "APP_ERROR"):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        super().__init__(message)


async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content=TradingBotError(
            error_code=exc.error_code,
            message=exc.message,
            request_id=request.headers.get("X-Request-ID", ""),
            timestamp=datetime.now(timezone.utc),
        ).model_dump(mode="json"),
    )


async def generic_error_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content=TradingBotError(
            error_code="INTERNAL_ERROR",
            message="An unexpected error occurred",
            request_id=request.headers.get("X-Request-ID", ""),
            timestamp=datetime.now(timezone.utc),
        ).model_dump(mode="json"),
    )
