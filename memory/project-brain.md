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

## What's Built (as of 2026-03-18)
- Project scaffold: full directory structure
- `app/core/`: config, security, middleware, rate_limit, exceptions
- `app/main.py`: FastAPI app with health endpoint
- `docker-compose.yml`, `Dockerfile`, CI pipeline
- `docs/phases/2026-03-18-mvp-build.md`: approved MVP build plan

## What's NOT Built Yet
- DB models + Alembic
- Celery workers
- Data layer (yfinance, pandas-ta, news, VIX)
- All 7 agents + LangGraph pipeline
- API routes (scan, signal, portfolio)
- Paper trading execution
