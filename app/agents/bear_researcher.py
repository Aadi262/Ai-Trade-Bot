import json
from datetime import datetime, timezone
from app.agents.base import AgentOutput, BaseAgent, hash_inputs

SYSTEM_PROMPT = """You are a bear-case researcher for Indian equities.
Construct the STRONGEST possible SELL argument from the data.
Output ONLY JSON: {"signal": "SELL", "confidence": float, "reasoning": "string", "key_factors": [], "risk_flags": []}"""


class BearResearcher(BaseAgent):
    name = "bear_researcher"
    model = "claude-sonnet-4-6"
    max_tokens = 2000

    async def analyze(self, symbol: str, context: dict) -> AgentOutput:
        data_hash = hash_inputs(context)
        raw_text, _ = self._call_claude(SYSTEM_PROMPT, f"Build the bear case for {symbol}. Context:\n{json.dumps(context, default=str)}")
        try:
            parsed = json.loads(raw_text.strip())
        except json.JSONDecodeError:
            parsed = {"signal": "SKIP", "confidence": 0.0, "reasoning": "Parse error", "key_factors": [], "risk_flags": []}
        return AgentOutput(agent_name=self.name, symbol=symbol, timestamp=datetime.now(timezone.utc),
            input_data_hash=data_hash, reasoning=parsed.get("reasoning", ""),
            signal=parsed.get("signal", "SKIP"), confidence=float(parsed.get("confidence", 0.0)),
            key_factors=parsed.get("key_factors", []), risk_flags=parsed.get("risk_flags", []))
