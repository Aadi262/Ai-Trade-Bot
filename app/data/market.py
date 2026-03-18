import re

import pandas as pd
import structlog
import yfinance as yf

logger = structlog.get_logger(__name__)

_SYMBOL_RE = re.compile(r"^[A-Z0-9]{1,20}\.(NS|BO)$")


def validate_symbol(symbol: str) -> bool:
    return bool(_SYMBOL_RE.match(symbol))


async def fetch_ohlcv(
    symbol: str,
    period: str = "3mo",
    interval: str = "1d",
) -> pd.DataFrame:
    logger.info("fetching_ohlcv", symbol=symbol, period=period)
    df: pd.DataFrame = yf.download(
        symbol,
        period=period,
        interval=interval,
        auto_adjust=True,
        progress=False,
    )
    if df.empty:
        raise ValueError(f"No data returned from yfinance for symbol: {symbol}")
    logger.info("ohlcv_fetched", symbol=symbol, rows=len(df))
    return df


async def fetch_current_price(symbol: str) -> float:
    df = await fetch_ohlcv(symbol, period="5d", interval="1d")
    return float(df["Close"].iloc[-1])
