# PRIORITY WORK — TradingBot-IN

> Read this first every session. Updated at session end.

## Current Task
**Build the API routes layer** — scan endpoint, signals endpoint, portfolio endpoint

## Next Immediate Action
```
Say "resume" to restore context, then:
"build the API routes: app/api/v1/scan.py, signals.py, portfolio.py"
```

## What Already Exists (MVP complete)
- `app/db/base.py` + `app/db/models.py` — async SQLAlchemy, all 5 tables
- `app/workers/` — Celery app, beat schedule, task stubs
- `app/data/` — market, indicators, global_cues, news
- `app/agents/` — base, risk_manager (100% cov), 7 agents, graph.py (LangGraph)
- `app/main.py` — FastAPI app with health endpoint
- `app/core/` — config, security, middleware, rate_limit, exceptions
- **47 tests passing, 78% coverage**

## Next Phase: API Routes

| Endpoint | File | Purpose |
|----------|------|---------|
| POST /api/v1/scan/{symbol} | app/api/v1/scan.py | Trigger scan pipeline for a symbol |
| GET /api/v1/signals | app/api/v1/signals.py | List recent signals from DB |
| GET /api/v1/portfolio | app/api/v1/portfolio.py | Open positions + daily PnL |

## Critical Constraints (never violate)
- TRADING_MODE=paper at all times
- All routes require auth (JWT via `authenticate` middleware)
- `risk_manager.py` must stay at 100% test coverage
- Write tests first (TDD)

## Environment Notes
- Python 3.14 venv — pandas-ta skipped, pure pandas indicators used
- REDIS_URL=memory:// in conftest (slowapi workaround)
- CELERY_BROKER_URL=redis://localhost:6379/0 (separate from REDIS_URL)
- pytest-cov: use dot notation `--cov=app.module.name`
