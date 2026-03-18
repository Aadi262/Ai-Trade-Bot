# Project Brain — TradingBot-IN

> Permanent project knowledge. Never delete — only append or correct.

## Identity
- **Name**: TradingBot-IN
- **GitHub**: https://github.com/Aadi262/Ai-Trade-Bot
- **Purpose**: Multi-agent AI trading system for NSE/BSE Indian equity markets
- **Stack**: FastAPI + Celery + PostgreSQL + Redis + LangGraph + Claude API

## Architecture Decisions (locked in)

### LangGraph State
- `TradingState` must be `TypedDict` — LangGraph `StateGraph` does not support `dataclass`
- Node functions return `dict` partial updates, not the full state object
- Initial state must be a plain dict: `{"symbol": "...", "agent_outputs": {}, ...}`

### Agent Design
- `risk_manager` is a **pure-Python rules engine** — NOT an LLM agent, NOT in `AGENT_CONFIG`
- All agent fallbacks on JSON parse error → `signal="SKIP", confidence=0.0` (never BUY/SELL at 0 confidence)
- All agents extend `BaseAgent` — `analyze(symbol, context) -> AgentOutput`
- `AgentOutput` is a Pydantic model with strict validation (signal literal, confidence 0-1)

### Testing
- `tests/conftest.py` sets env vars (including `ANTHROPIC_API_KEY="test-placeholder-key"`) BEFORE importing app
- `risk_manager.py` requires `--cov-fail-under=100`
- All external calls (yfinance, Claude API, feedparser) must be mocked in unit tests

### Port Management
- All docker-compose ports use `${PORT:-default}` env var overrides
- `bash scripts/check_ports.sh` auto-detects conflicts before startup
- User has other projects on local ports — ALWAYS check before running

### Security
- TRADING_MODE defaults to `paper` — never switch to `live` without explicit human confirmation
- All secrets via `app/core/config.py` (pydantic-settings) — never hardcoded

## What's Built (as of 2026-03-19)
- Project scaffold + `app/core/` + `app/main.py` + docker-compose + CI
- **DB layer**: `app/db/base.py` (async session), `app/db/models.py` (5 models), Alembic async env
- **Celery**: `app/workers/celery_app.py` (3-priority queues), beat_schedule (6 crons), task stubs
- **Data layer**: market.py (yfinance), indicators.py (pandas-based), global_cues.py (VIX), news.py (RSS)
- **Agents**: base.py, risk_manager.py (100% cov), technical, fundamentals, sentiment, macro, bull_researcher, bear_researcher, trader, fund_manager
- **LangGraph**: `app/agents/graph.py` — full 7-agent sequential pipeline, `run_pipeline(symbol)`
- **Tests**: 47 passing, 78% coverage, integration smoke test

## Environment Gotchas
- Python 3.14 in venv — `pandas-ta` incompatible (needs numba). Use pure pandas for indicators.
- `REDIS_URL=memory://` in conftest — prevents slowapi import-time Redis connection
- `CELERY_BROKER_URL` must be set separately from `REDIS_URL` (defaults to redis://localhost:6379/0)
- pytest-cov: use dot notation `--cov=app.agents.risk_manager`, NOT path notation
- SQLite test DB: engine must skip `pool_size`/`max_overflow` kwargs

## CI / Local Dev (as of 2026-03-19 Session 4)
- CI uses `requirements-ci.txt` — no torch/transformers, runs natively in ~30s
- `safety` removed from CI (v3 requires paid account) — `pip-audit` only with `continue-on-error`
- Deploy job skips gracefully if `VPS_HOST` GitHub secret not set
- Local dev: `.env` with SQLite + `REDIS_URL=memory://` — no Docker needed
- `uvicorn` installed in venv — start with `.venv/bin/uvicorn app.main:app --port 8000 --reload`
- `Settings.extra = "ignore"` — docker-compose port vars silently ignored by pydantic

## What's NOT Built Yet
- API routes (scan, signals, portfolio endpoints)
- Paper trading execution (Trade creation from RiskDecision)
- Auth endpoints (JWT login/register)
- VPS auto-deploy (deferred — user has issue with VPS setup)
- Frontend / dashboard
