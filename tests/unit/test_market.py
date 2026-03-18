import pandas as pd
import pytest
from unittest.mock import patch

from app.data.market import fetch_ohlcv, validate_symbol


def test_validate_symbol_accepts_ns():
    assert validate_symbol("RELIANCE.NS") is True


def test_validate_symbol_accepts_bo():
    assert validate_symbol("RELIANCE.BO") is True


def test_validate_symbol_rejects_invalid():
    assert validate_symbol("reliance") is False
    assert validate_symbol("RELIANCE") is False
    assert validate_symbol("../../etc") is False


@pytest.mark.asyncio
async def test_fetch_ohlcv_returns_dataframe():
    mock_df = pd.DataFrame({
        "Open": [100.0], "High": [105.0], "Low": [99.0],
        "Close": [103.0], "Volume": [1000000]
    })
    with patch("app.data.market.yf.download", return_value=mock_df):
        result = await fetch_ohlcv("RELIANCE.NS", period="1mo")
    assert isinstance(result, pd.DataFrame)
    assert not result.empty


@pytest.mark.asyncio
async def test_fetch_ohlcv_raises_on_empty():
    with patch("app.data.market.yf.download", return_value=pd.DataFrame()):
        with pytest.raises(ValueError, match="No data"):
            await fetch_ohlcv("FAKE.NS", period="1mo")
