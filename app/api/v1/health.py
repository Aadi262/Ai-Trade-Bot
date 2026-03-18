from datetime import datetime, timezone

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    version: str = "1.0.0"
    trading_mode: str


@router.get("/health", response_model=HealthResponse, summary="Health check")
async def health_check() -> HealthResponse:
    from app.core.config import settings

    return HealthResponse(
        status="ok",
        timestamp=datetime.now(timezone.utc),
        trading_mode=settings.TRADING_MODE,
    )
