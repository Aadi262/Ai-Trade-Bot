import json
import time
from datetime import datetime, timezone
import structlog
from app.agents.base import AgentOutput, BaseAgent, hash_inputs

logger = structlog.get_logger(__name__)
SYSTEM_PROMPT = """You are a fundamental analyst for Indian equities.
Given PE ratio, EPS growth, debt-to-equity, and promoter holding data, output ONLY JSON:
{"signal": "BUY"|"SELL"|"HOLD"|"SKIP", "confidence": float, "reasoning": "string", "key_factors": [], "risk_flags": []}"""


class FundamentalsAgent(BaseAgent):
    name = "fundamentals"
    model = "claude-haiku-4-5-20251001"
    max_tokens = 1000

    async def analyze(self, symbol: str, context: dict) -> AgentOutput:
        import yfinance as yf
        ticker = yf.Ticker(symbol)
        info = ticker.info or {}
        input_data = {
            "symbol": symbol, "pe_ratio": info.get("trailingPE"),
            "forward_pe": info.get("forwardPE"), "eps": info.get("trailingEps"),
            "eps_growth": info.get("earningsGrowth"), "debt_to_equity": info.get("debtToEquity"),
            "promoter_holding": info.get("heldPercentInsiders"),
            "market_cap": info.get("marketCap"), "sector": info.get("sector"),
        }
        data_hash = hash_inputs(input_data)
        raw_text, _ = self._call_claude(SYSTEM_PROMPT, f"Analyze fundamentals for {symbol}:\n{json.dumps(input_data, default=str)}")
        try:
            parsed = json.loads(raw_text.strip())
        except json.JSONDecodeError:
            parsed = {"signal": "SKIP", "confidence": 0.0, "reasoning": "Parse error", "key_factors": [], "risk_flags": ["parse_error"]}
        return AgentOutput(agent_name=self.name, symbol=symbol, timestamp=datetime.now(timezone.utc),
            input_data_hash=data_hash, reasoning=parsed.get("reasoning", ""),
            signal=parsed.get("signal", "SKIP"), confidence=float(parsed.get("confidence", 0.0)),
            key_factors=parsed.get("key_factors", []), risk_flags=parsed.get("risk_flags", []))
