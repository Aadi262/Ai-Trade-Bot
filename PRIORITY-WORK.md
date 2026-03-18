# PRIORITY WORK — TradingBot-IN

> Read this first every session. Updated at session end.

## Current Task
**Build the API routes layer** — scan, signals, portfolio endpoints + paper trade execution

## Next Immediate Action
```
Say "resume" to restore context, then answer auth question:
"Should scan/signals/portfolio require JWT auth, or open for now?"
→ Then Claude will build all 4 things
```

## Open Design Question (answer at start of next session)
**Auth strategy for API routes:**
- A) No auth — open endpoints, ship fast (recommended for personal MVP)
- B) JWT required — needs Bearer token (auth system exists but no login endpoint yet)

## What Already Exists (MVP complete)
- `app/db/base.py` + `app/db/models.py` — async SQLAlchemy, all 5 tables
- `app/workers/` — Celery app, beat schedule, task stubs
- `app/data/` — market, indicators, global_cues, news
- `app/agents/` — base, risk_manager (100% cov), 7 agents, graph.py (LangGraph)
- `app/main.py` — FastAPI app with health endpoint only
- `app/core/` — config (extra=ignore), security, middleware, rate_limit, exceptions
- **47 tests passing, 78% coverage**
- **CI green** — native GitHub Actions, ~30s, no Docker
- **Local server works** — `uvicorn` installed, `.env` created, SQLite + memory://

## Next Phase: API Routes + Paper Trade Execution

| Thing | File | Purpose |
|-------|------|---------|
| POST /api/v1/scan/{symbol} | app/api/v1/scan.py | Run LangGraph pipeline, save Signal to DB |
| GET /api/v1/signals | app/api/v1/signals.py | List recent signals from DB |
| GET /api/v1/portfolio | app/api/v1/portfolio.py | Open trades + daily PnL |
| Paper trade executor | app/execution/paper.py | Create Trade row from RiskDecision |

## Critical Constraints (never violate)
- TRADING_MODE=paper at all times
- `risk_manager.py` must stay at 100% test coverage
- Write tests alongside code (TDD where possible)

## Environment Notes
- Python 3.14 venv — pandas-ta skipped, pure pandas indicators used
- REDIS_URL=memory:// in conftest (slowapi workaround)
- CELERY_BROKER_URL=redis://localhost:6379/0 (separate from REDIS_URL)
- pytest-cov: use dot notation `--cov=app.module.name`
- Local .env: SQLite + memory://, no Docker needed
- CI: uses requirements-ci.txt (no torch/transformers)
