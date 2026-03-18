import json
from datetime import datetime, timezone
import structlog
from app.agents.base import AgentOutput, BaseAgent, hash_inputs
from app.data.global_cues import fetch_all_cues

logger = structlog.get_logger(__name__)
SYSTEM_PROMPT = """You are a macro analyst for Indian markets.
Given India VIX, USD/INR, FII/DII flows context, output ONLY JSON:
{"signal": "BUY"|"SELL"|"HOLD"|"SKIP", "confidence": float, "reasoning": "string", "key_factors": [], "risk_flags": []}"""


class MacroAgent(BaseAgent):
    name = "macro"
    model = "claude-haiku-4-5-20251001"
    max_tokens = 800

    async def analyze(self, symbol: str, context: dict) -> AgentOutput:
        cues = await fetch_all_cues()
        input_data = {"symbol": symbol, "india_vix": cues.india_vix, "usdinr": cues.usdinr, "sgx_nifty": cues.sgx_nifty, "trading_paused": cues.should_pause_trading()}
        data_hash = hash_inputs(input_data)
        if cues.should_pause_trading():
            return AgentOutput(agent_name=self.name, symbol=symbol, timestamp=datetime.now(timezone.utc),
                input_data_hash=data_hash, reasoning=f"VIX {cues.india_vix:.1f} exceeds threshold",
                signal="SKIP", confidence=0.0, key_factors=[f"VIX: {cues.india_vix:.1f}"], risk_flags=["vix_gate_active"])
        raw_text, _ = self._call_claude(SYSTEM_PROMPT, f"Analyze macro environment:\n{json.dumps(input_data, default=str)}")
        try:
            parsed = json.loads(raw_text.strip())
        except json.JSONDecodeError:
            parsed = {"signal": "HOLD", "confidence": 0.5, "reasoning": "Parse error", "key_factors": [], "risk_flags": []}
        return AgentOutput(agent_name=self.name, symbol=symbol, timestamp=datetime.now(timezone.utc),
            input_data_hash=data_hash, reasoning=parsed.get("reasoning", ""),
            signal=parsed.get("signal", "HOLD"), confidence=float(parsed.get("confidence", 0.5)),
            key_factors=parsed.get("key_factors", []), risk_flags=parsed.get("risk_flags", []))
