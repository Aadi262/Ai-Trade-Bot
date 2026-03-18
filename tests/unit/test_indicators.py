import pandas as pd
import numpy as np
import pytest
from app.data.indicators import compute_indicators, IndicatorResult


@pytest.fixture
def sample_ohlcv() -> pd.DataFrame:
    n = 100
    return pd.DataFrame({
        "Open":   np.random.uniform(100, 200, n),
        "High":   np.random.uniform(200, 210, n),
        "Low":    np.random.uniform(90, 100, n),
        "Close":  np.random.uniform(100, 200, n),
        "Volume": np.random.randint(500_000, 5_000_000, n),
    })


def test_compute_indicators_returns_result(sample_ohlcv):
    result = compute_indicators(sample_ohlcv)
    assert isinstance(result, IndicatorResult)


def test_ema_values_present(sample_ohlcv):
    result = compute_indicators(sample_ohlcv)
    assert result.ema_20 is not None
    assert result.ema_50 is not None


def test_rsi_in_range(sample_ohlcv):
    result = compute_indicators(sample_ohlcv)
    if result.rsi is not None:
        assert 0.0 <= result.rsi <= 100.0


def test_macd_fields_present(sample_ohlcv):
    result = compute_indicators(sample_ohlcv)
    assert hasattr(result, "macd")
    assert hasattr(result, "macd_signal")


def test_atr_positive(sample_ohlcv):
    result = compute_indicators(sample_ohlcv)
    if result.atr is not None:
        assert result.atr > 0
