# TradingBot-IN — Active State

**Last Updated**: 2026-03-18 (Session 2)
**Phase**: MVP Build — ready to execute
**Status**: Plan approved, no code written yet

## Active Project State

| Field | Value |
|-------|-------|
| Last session | 2026-03-18 |
| Current phase | MVP Build (DB → Celery → Data → Agents) |
| Last thing completed | Plan approved + committed (2-round review, 11 issues fixed) |
| Currently in progress | Nothing — clean handoff |
| Blocked on | Nothing |
| Next action | `"resume"` then execute MVP plan with subagent-driven dev |

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
