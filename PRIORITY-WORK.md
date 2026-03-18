# PRIORITY WORK — TradingBot-IN

> Read this first every session. Updated at session end.

## Current Task
**Execute the MVP build plan** — DB models → Celery → Data layer → 7 Agents → LangGraph

## Next Immediate Action
```
Say "resume" to restore context, then:
"execute the MVP plan using subagent-driven development"
```

## Plan Location
`docs/phases/2026-03-18-mvp-build.md`

## Execution Order (from plan)
1. Pre-flight: `bash scripts/check_ports.sh` + confirm `tests/conftest.py` env fixtures
2. Phase 1: `app/db/base.py` → `app/db/models.py` → Alembic init + first migration
3. Phase 2: `app/workers/celery_app.py` → `beat_schedule.py` → task stubs
4. Phase 3: `app/data/market.py` → `indicators.py` → `global_cues.py` → `news.py`
5. Phase 4: `app/agents/base.py` → `risk_manager.py` → all 7 agents → `graph.py`
6. Integration smoke test

## Critical Constraints (never violate)
- Write test FIRST, run to confirm FAIL, then implement
- `risk_manager.py` must achieve 100% test coverage (`--cov-fail-under=100`)
- `TradingState` in `graph.py` must be `TypedDict` (not dataclass)
- LangGraph node functions return `dict` partial updates (not full state)
- BullResearcher/BearResearcher fallback signal = `"SKIP"` always
- `risk_manager` is NOT an LLM agent — pure Python rules, not in AGENT_CONFIG
- TRADING_MODE=paper at all times until explicit human sign-off

## What Already Exists
- `app/main.py` — FastAPI app + health endpoint
- `app/core/` — config, security, middleware, rate_limit, exceptions
- `docker-compose.yml` — full stack with port overrides
- `tests/conftest.py` — test env fixtures (ANTHROPIC_API_KEY mocked)
- GitHub remote: https://github.com/Aadi262/Ai-Trade-Bot
