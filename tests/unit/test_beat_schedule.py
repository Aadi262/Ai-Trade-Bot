from app.workers.beat_schedule import CELERYBEAT_SCHEDULE


def test_required_schedules_exist():
    required = {
        "pre-market-data-refresh",
        "session-scan-nifty50",
        "vix-regime-check",
        "daily-pnl-report",
        "weekly-tearsheet",
        "security-dep-scan",
    }
    assert required <= set(CELERYBEAT_SCHEDULE.keys())


def test_vix_check_is_in_critical_queue():
    vix = CELERYBEAT_SCHEDULE["vix-regime-check"]
    assert vix["options"]["queue"] == "critical"


def test_scan_expires_before_next_run():
    scan = CELERYBEAT_SCHEDULE["session-scan-nifty50"]
    assert scan["options"].get("expires", 999) < 30
