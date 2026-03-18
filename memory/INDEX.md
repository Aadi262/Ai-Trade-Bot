# TradingBot-IN — Active State

**Last Updated**: 2026-03-19 (Session 4)
**Phase**: API Routes Layer (next after MVP Build)
**Status**: 47 tests passing, CI green, server runs locally

## Active Project State

| Field | Value |
|-------|-------|
| Last session | 2026-03-19 |
| Current phase | API Routes + Paper Trade Execution |
| Last thing completed | CI fixed, local server running (`uvicorn` + `.env` set up) |
| Currently in progress | Nothing — clean handoff |
| Blocked on | Nothing |
| Next action | Brainstorm auth strategy (open vs JWT), then build `app/api/v1/scan.py`, `signals.py`, `portfolio.py` + paper trade execution |

## Port Map (local dev)
Run `bash scripts/check_ports.sh` before starting — auto-detects conflicts.
Default ports (overridable via .env):
- API: 8000 → `API_PORT`
- Flower: 5555 → `FLOWER_PORT`
- Redis: 6379 → `REDIS_PORT`
- Postgres: 5432 → `POSTGRES_PORT`
- Prometheus: 9090 → `PROMETHEUS_PORT`
- Grafana: 3001 → `GRAFANA_PORT`

## Start Server Locally
```bash
.venv/bin/uvicorn app.main:app --port 8000 --reload
# then open: http://localhost:8000/docs
```
No Docker needed — uses SQLite + memory:// Redis via .env

## Key Files
- **Plan**: `docs/phases/2026-03-18-mvp-build.md`
- **Config**: `app/core/config.py` (extra="ignore" — docker port vars silently skipped)
- **Main app**: `app/main.py` (health endpoint working)
- **Test fixtures**: `tests/conftest.py` (env vars set, ANTHROPIC_API_KEY mocked)
- **CI**: `.github/workflows/ci.yml` (native, no docker-compose, ~30s)
- **GitHub**: https://github.com/Aadi262/Ai-Trade-Bot
