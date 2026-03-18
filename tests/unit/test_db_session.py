import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.base import get_db, Base


@pytest.mark.asyncio
async def test_get_db_yields_async_session():
    """get_db() must yield an AsyncSession."""
    gen = get_db()
    session = await gen.__anext__()
    assert isinstance(session, AsyncSession)
    try:
        await gen.aclose()
    except Exception:
        pass
