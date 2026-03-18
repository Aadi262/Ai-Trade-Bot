import json
import time
from datetime import datetime, timezone
import structlog
from app.agents.base import AgentOutput, BaseAgent, hash_inputs
from app.data.indicators import compute_indicators
from app.data.market import fetch_ohlcv

logger = structlog.get_logger(__name__)

SYSTEM_PROMPT = """You are a technical analyst for Indian equities (NSE/BSE).
Analyze the provided indicator data and return ONLY a JSON object with these fields:
{"signal": "BUY"|"SELL"|"HOLD"|"SKIP", "confidence": float 0.0-1.0,
 "reasoning": "chain-of-thought 2-3 sentences",
 "key_factors": ["factor1", "factor2"], "risk_flags": []}
Rules: BUY=clear uptrend, SELL=clear downtrend, HOLD=mixed, SKIP=insufficient data.
confidence < 0.65 → always SKIP. Be conservative."""


class TechnicalAgent(BaseAgent):
    name = "technical"
    model = "claude-haiku-4-5-20251001"
    max_tokens = 800

    async def analyze(self, symbol: str, context: dict) -> AgentOutput:
        start = time.monotonic()
        df = await fetch_ohlcv(symbol, period="3mo")
        indicators = compute_indicators(df)

        input_data = {
            "symbol": symbol,
            "ema_20": indicators.ema_20, "ema_50": indicators.ema_50,
            "ema_200": indicators.ema_200, "rsi": indicators.rsi,
            "macd": indicators.macd, "macd_signal": indicators.macd_signal,
            "atr": indicators.atr, "bb_pct_b": indicators.bb_pct_b,
            "adx": indicators.adx, "obv": indicators.obv,
        }
        data_hash = hash_inputs(input_data)
        user_msg = f"Analyze technical indicators for {symbol}:\n{json.dumps(input_data, default=str)}"
        raw_text, tokens = self._call_claude(SYSTEM_PROMPT, user_msg)

        try:
            parsed = json.loads(raw_text.strip())
        except json.JSONDecodeError:
            parsed = {"signal": "SKIP", "confidence": 0.0,
                      "reasoning": "Failed to parse LLM response",
                      "key_factors": [], "risk_flags": ["parse_error"]}

        latency_ms = int((time.monotonic() - start) * 1000)
        logger.info("technical_agent_complete", symbol=symbol, latency_ms=latency_ms, tokens=tokens)
        return AgentOutput(
            agent_name=self.name, symbol=symbol,
            timestamp=datetime.now(timezone.utc),
            input_data_hash=data_hash,
            reasoning=parsed.get("reasoning", ""),
            signal=parsed.get("signal", "SKIP"),
            confidence=float(parsed.get("confidence", 0.0)),
            key_factors=parsed.get("key_factors", []),
            risk_flags=parsed.get("risk_flags", []),
        )
