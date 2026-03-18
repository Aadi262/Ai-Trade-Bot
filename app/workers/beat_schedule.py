from celery.schedules import crontab

from app.workers.celery_app import celery_app

CELERYBEAT_SCHEDULE: dict = {
    "pre-market-data-refresh": {
        "task": "tasks.v1.refresh_market_data",
        "schedule": crontab(hour=3, minute=15),
        "options": {"queue": "high"},
    },
    "session-scan-nifty50": {
        "task": "tasks.v1.scan_watchlist",
        "schedule": 30.0,
        "options": {"queue": "high", "expires": 29},
    },
    "vix-regime-check": {
        "task": "tasks.v1.check_india_vix",
        "schedule": 300.0,
        "options": {"queue": "critical"},
    },
    "daily-pnl-report": {
        "task": "tasks.v1.generate_daily_report",
        "schedule": crontab(hour=10, minute=30),
        "options": {"queue": "default"},
    },
    "weekly-tearsheet": {
        "task": "tasks.v1.generate_quantstats_tearsheet",
        "schedule": crontab(day_of_week=6, hour=2, minute=30),
        "options": {"queue": "default"},
    },
    "security-dep-scan": {
        "task": "tasks.v1.run_pip_audit",
        "schedule": crontab(hour=20, minute=30),
        "options": {"queue": "default"},
    },
}

celery_app.conf.beat_schedule = CELERYBEAT_SCHEDULE
