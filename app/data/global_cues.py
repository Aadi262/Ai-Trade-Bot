from __future__ import annotations

from dataclasses import dataclass

import structlog

from app.data.market import fetch_ohlcv

logger = structlog.get_logger(__name__)

_VIX_TICKER = "^INDIAVIX"
_USDINR_TICKER = "USDINR=X"
VIX_PAUSE_THRESHOLD = 16.0
VIX_RESUME_THRESHOLD = 14.0


@dataclass
class GlobalCues:
    india_vix: float
    usdinr: float | None
    sgx_nifty: float | None

    def should_pause_trading(self) -> bool:
        return self.india_vix > VIX_PAUSE_THRESHOLD


async def fetch_india_vix() -> float:
    df = await fetch_ohlcv(_VIX_TICKER, period="5d", interval="1d")
    return float(df["Close"].iloc[-1])


async def fetch_usdinr() -> float:
    df = await fetch_ohlcv(_USDINR_TICKER, period="5d", interval="1d")
    return float(df["Close"].iloc[-1])


async def fetch_all_cues() -> GlobalCues:
    india_vix = await fetch_india_vix()
    try:
        usdinr = await fetch_usdinr()
    except Exception:
        logger.warning("usdinr_fetch_failed")
        usdinr = None
    cues = GlobalCues(india_vix=india_vix, usdinr=usdinr, sgx_nifty=None)
    logger.info("global_cues_fetched", vix=india_vix, paused=cues.should_pause_trading())
    return cues
