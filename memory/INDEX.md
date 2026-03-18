# TradingBot-IN — Active State

**Last Updated**: 2026-03-19 (Session 3)
**Phase**: MVP Build — COMPLETE. Next: API routes layer.
**Status**: 47 tests passing, 78% coverage, all agents + LangGraph wired

## Active Project State

| Field | Value |
|-------|-------|
| Last session | 2026-03-19 |
| Current phase | API Routes (next phase after MVP build) |
| Last thing completed | Full MVP backend: DB + Celery + Data + 7 Agents + LangGraph (47 tests) |
| Currently in progress | Nothing — clean handoff |
| Blocked on | Nothing |
| Next action | Build `app/api/v1/scan.py`, `signals.py`, `portfolio.py` |

## Port Map (local dev)
Run `bash scripts/check_ports.sh` before starting — auto-detects conflicts.
Default ports (overridable via .env):
- API: 8000 → `API_PORT`
- Flower: 5555 → `FLOWER_PORT`
- Redis: 6379 → `REDIS_PORT`
- Postgres: 5432 → `POSTGRES_PORT`
- Prometheus: 9090 → `PROMETHEUS_PORT`
- Grafana: 3001 → `GRAFANA_PORT`

## Key Files
- **Plan**: `docs/phases/2026-03-18-mvp-build.md`
- **Config**: `app/core/config.py` (already exists)
- **Main app**: `app/main.py` (health endpoint working)
- **Test fixtures**: `tests/conftest.py` (env vars set, ANTHROPIC_API_KEY mocked)
- **GitHub**: https://github.com/Aadi262/Ai-Trade-Bot
