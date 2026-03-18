import os

from celery import Celery
from kombu import Exchange, Queue

# Use CELERY_BROKER_URL if set explicitly.
# REDIS_URL may be "memory://" in the test environment, so we keep a
# separate env var for Celery and fall back to a real Redis default.
_broker = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/0")
_backend = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

celery_app = Celery("tradingbot")

celery_app.conf.update(
    broker_url=_broker,
    result_backend=_backend,
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="Asia/Kolkata",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_queues=(
        Queue(
            "critical",
            Exchange("critical"),
            routing_key="critical",
            queue_arguments={"x-max-priority": 10},
        ),
        Queue(
            "high",
            Exchange("high"),
            routing_key="high",
            queue_arguments={"x-max-priority": 7},
        ),
        Queue(
            "default",
            Exchange("default"),
            routing_key="default",
            queue_arguments={"x-max-priority": 3},
        ),
    ),
    task_default_queue="default",
    task_routes={
        "tasks.v1.check_india_vix": {"queue": "critical"},
        "tasks.v1.scan_watchlist": {"queue": "high"},
        "tasks.v1.refresh_market_data": {"queue": "high"},
        "tasks.v1.generate_daily_report": {"queue": "default"},
        "tasks.v1.generate_quantstats_tearsheet": {"queue": "default"},
        "tasks.v1.run_pip_audit": {"queue": "default"},
    },
)

celery_app.autodiscover_tasks(["app.workers"])
