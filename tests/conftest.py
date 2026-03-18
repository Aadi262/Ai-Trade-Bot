import os

import pytest
from httpx import AsyncClient, ASGITransport

# Set test env vars BEFORE importing any app modules that read Settings at import time
os.environ.setdefault("SECRET_KEY", "test-secret-key-32-chars-minimum!!")
os.environ.setdefault("JWT_SECRET", "test-jwt-secret-32-chars-minimum!!")
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./test.db")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/1")
os.environ.setdefault("ANTHROPIC_API_KEY", "test-placeholder-key")
os.environ.setdefault("POSTGRES_PASSWORD", "test")
os.environ.setdefault("TRADING_MODE", "paper")

from app.main import app  # noqa: E402 — must come after env setup


@pytest.fixture
async def client() -> AsyncClient:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac
