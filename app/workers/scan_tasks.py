import structlog

from app.workers.celery_app import celery_app

logger = structlog.get_logger(__name__)


@celery_app.task(name="tasks.v1.scan_symbol", bind=True, max_retries=3)
def scan_symbol_task(self, symbol: str, user_id: str) -> dict:
    logger.info("scan_task_started", symbol=symbol, user_id=user_id)
    return {"symbol": symbol, "status": "queued"}


@celery_app.task(name="tasks.v1.scan_watchlist")
def scan_watchlist_task() -> None:
    logger.info("scan_watchlist_started")


@celery_app.task(name="tasks.v1.refresh_market_data")
def refresh_market_data_task() -> None:
    logger.info("market_data_refresh_started")


@celery_app.task(name="tasks.v1.check_india_vix")
def check_india_vix_task() -> None:
    logger.info("vix_check_started")
