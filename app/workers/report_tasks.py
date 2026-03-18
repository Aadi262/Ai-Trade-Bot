import subprocess

import structlog

from app.workers.celery_app import celery_app

logger = structlog.get_logger(__name__)


@celery_app.task(name="tasks.v1.generate_daily_report")
def generate_daily_report_task() -> None:
    logger.info("daily_report_started")


@celery_app.task(name="tasks.v1.generate_quantstats_tearsheet")
def generate_tearsheet_task() -> None:
    logger.info("tearsheet_generation_started")


@celery_app.task(name="tasks.v1.run_pip_audit")
def run_pip_audit_task() -> None:
    result = subprocess.run(
        ["pip-audit", "-r", "requirements.txt", "--format=json"],
        capture_output=True,
        text=True,
    )
    logger.info("pip_audit_completed", returncode=result.returncode)
