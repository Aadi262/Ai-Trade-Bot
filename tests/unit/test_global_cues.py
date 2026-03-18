import pytest
from unittest.mock import patch, AsyncMock
import pandas as pd

from app.data.global_cues import fetch_india_vix, fetch_usdinr, GlobalCues, fetch_all_cues


@pytest.mark.asyncio
async def test_fetch_india_vix_returns_float():
    mock_df = pd.DataFrame({"Close": [14.5]})
    with patch("app.data.global_cues.fetch_ohlcv", new_callable=AsyncMock, return_value=mock_df):
        vix = await fetch_india_vix()
    assert isinstance(vix, float)
    assert vix > 0


@pytest.mark.asyncio
async def test_fetch_all_cues_returns_global_cues():
    mock_df = pd.DataFrame({"Close": [14.5]})
    with patch("app.data.global_cues.fetch_ohlcv", new_callable=AsyncMock, return_value=mock_df):
        cues = await fetch_all_cues()
    assert isinstance(cues, GlobalCues)
    assert cues.india_vix > 0


def test_vix_gate_logic():
    cues = GlobalCues(india_vix=17.0, usdinr=83.5, sgx_nifty=None)
    assert cues.should_pause_trading() is True


def test_vix_gate_ok():
    cues = GlobalCues(india_vix=13.0, usdinr=83.5, sgx_nifty=None)
    assert cues.should_pause_trading() is False
