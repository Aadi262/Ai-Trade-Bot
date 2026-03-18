"""
Technical indicator computation using pure pandas.

pandas-ta requires numba which does not support Python 3.14+.
All indicators are implemented directly against pandas Series so
the module has zero additional runtime dependencies.
"""
from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
import structlog

logger = structlog.get_logger(__name__)


@dataclass
class IndicatorResult:
    ema_20: float | None = None
    ema_50: float | None = None
    ema_200: float | None = None
    sma_50: float | None = None
    rsi: float | None = None
    macd: float | None = None
    macd_signal: float | None = None
    macd_hist: float | None = None
    stoch_k: float | None = None
    stoch_d: float | None = None
    atr: float | None = None
    bb_upper: float | None = None
    bb_mid: float | None = None
    bb_lower: float | None = None
    bb_pct_b: float | None = None
    obv: float | None = None
    vwap: float | None = None
    adx: float | None = None
    supertrend: bool | None = None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _last(series: pd.Series | None) -> float | None:
    if series is None:
        return None
    clean = series.dropna()
    return float(clean.iloc[-1]) if not clean.empty else None


def _ema(series: pd.Series, length: int) -> pd.Series:
    return series.ewm(span=length, adjust=False).mean()


def _sma(series: pd.Series, length: int) -> pd.Series:
    return series.rolling(window=length).mean()


def _rsi(series: pd.Series, length: int = 14) -> pd.Series:
    delta = series.diff()
    gain = delta.clip(lower=0).ewm(com=length - 1, adjust=False).mean()
    loss = (-delta.clip(upper=0)).ewm(com=length - 1, adjust=False).mean()
    rs = gain / loss.replace(0, float("nan"))
    return 100.0 - (100.0 / (1.0 + rs))


def _macd(
    series: pd.Series,
    fast: int = 12,
    slow: int = 26,
    signal: int = 9,
) -> tuple[pd.Series, pd.Series, pd.Series]:
    fast_ema = _ema(series, fast)
    slow_ema = _ema(series, slow)
    macd_line = fast_ema - slow_ema
    signal_line = _ema(macd_line, signal)
    hist = macd_line - signal_line
    return macd_line, signal_line, hist


def _atr(high: pd.Series, low: pd.Series, close: pd.Series, length: int = 14) -> pd.Series:
    prev_close = close.shift(1)
    tr = pd.concat(
        [high - low, (high - prev_close).abs(), (low - prev_close).abs()],
        axis=1,
    ).max(axis=1)
    return tr.ewm(com=length - 1, adjust=False).mean()


def _bbands(
    series: pd.Series,
    length: int = 20,
    std_dev: float = 2.0,
) -> tuple[pd.Series, pd.Series, pd.Series, pd.Series]:
    mid = _sma(series, length)
    std = series.rolling(window=length).std(ddof=0)
    upper = mid + std_dev * std
    lower = mid - std_dev * std
    pct_b = (series - lower) / (upper - lower).replace(0, float("nan"))
    return upper, mid, lower, pct_b


def _stoch(
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    k_period: int = 14,
    d_period: int = 3,
) -> tuple[pd.Series, pd.Series]:
    lowest_low = low.rolling(window=k_period).min()
    highest_high = high.rolling(window=k_period).max()
    denom = (highest_high - lowest_low).replace(0, float("nan"))
    k = 100.0 * (close - lowest_low) / denom
    d = k.rolling(window=d_period).mean()
    return k, d


def _obv(close: pd.Series, volume: pd.Series) -> pd.Series:
    direction = close.diff().apply(lambda x: 1 if x > 0 else (-1 if x < 0 else 0))
    return (direction * volume).cumsum()


def _adx(
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    length: int = 14,
) -> pd.Series:
    prev_high = high.shift(1)
    prev_low = low.shift(1)
    plus_dm = (high - prev_high).clip(lower=0)
    minus_dm = (prev_low - low).clip(lower=0)
    # zero out when the other is larger
    plus_dm = plus_dm.where(plus_dm > minus_dm, 0.0)
    minus_dm = minus_dm.where(minus_dm > plus_dm, 0.0)
    atr_s = _atr(high, low, close, length)
    plus_di = 100.0 * plus_dm.ewm(com=length - 1, adjust=False).mean() / atr_s.replace(0, float("nan"))
    minus_di = 100.0 * minus_dm.ewm(com=length - 1, adjust=False).mean() / atr_s.replace(0, float("nan"))
    dx = 100.0 * (plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, float("nan"))
    return dx.ewm(com=length - 1, adjust=False).mean()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def compute_indicators(df: pd.DataFrame) -> IndicatorResult:
    close: pd.Series = df["Close"].squeeze()
    high: pd.Series = df["High"].squeeze()
    low: pd.Series = df["Low"].squeeze()
    volume: pd.Series = df["Volume"].squeeze()

    result = IndicatorResult()

    result.ema_20 = _last(_ema(close, 20))
    result.ema_50 = _last(_ema(close, 50))
    result.ema_200 = _last(_ema(close, 200))
    result.sma_50 = _last(_sma(close, 50))
    result.rsi = _last(_rsi(close, 14))

    macd_line, signal_line, hist = _macd(close)
    result.macd = _last(macd_line)
    result.macd_signal = _last(signal_line)
    result.macd_hist = _last(hist)

    stoch_k, stoch_d = _stoch(high, low, close)
    result.stoch_k = _last(stoch_k)
    result.stoch_d = _last(stoch_d)

    result.atr = _last(_atr(high, low, close, 14))

    bb_upper, bb_mid, bb_lower, bb_pct_b = _bbands(close, 20)
    result.bb_upper = _last(bb_upper)
    result.bb_mid = _last(bb_mid)
    result.bb_lower = _last(bb_lower)
    result.bb_pct_b = _last(bb_pct_b)

    result.obv = _last(_obv(close, volume))
    result.adx = _last(_adx(high, low, close, 14))

    logger.debug("indicators_computed", rsi=result.rsi, ema_20=result.ema_20)
    return result
