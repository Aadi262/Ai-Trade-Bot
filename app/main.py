import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.api.v1 import health
from app.core.exceptions import AppError, app_error_handler, generic_error_handler
from app.core.middleware import RequestIDMiddleware
from app.core.rate_limit import limiter

logger = structlog.get_logger(__name__)


def create_app() -> FastAPI:
    app = FastAPI(
        title="TradingBot-IN",
        description="Multi-agent AI trading system for NSE/BSE Indian equity markets",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # Rate limiter state
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    # Custom error handlers
    app.add_exception_handler(AppError, app_error_handler)  # type: ignore[arg-type]
    app.add_exception_handler(Exception, generic_error_handler)  # type: ignore[arg-type]

    # Middleware (outermost first)
    app.add_middleware(RequestIDMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000"],  # Tighten for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Routers
    app.include_router(health.router, prefix="/api/v1")

    @app.on_event("startup")
    async def on_startup() -> None:
        logger.info("tradingbot_starting", trading_mode="paper")

    @app.on_event("shutdown")
    async def on_shutdown() -> None:
        logger.info("tradingbot_stopping")

    return app


app = create_app()
