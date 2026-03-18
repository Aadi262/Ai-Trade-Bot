import json
from datetime import datetime, timezone
from app.agents.base import AgentOutput, BaseAgent, hash_inputs

SYSTEM_PROMPT = """You are the fund manager — final approval authority.
Review the trader's recommendation. Override to SKIP if anything feels wrong.
Output ONLY JSON: {"signal": "BUY"|"SELL"|"HOLD"|"SKIP", "confidence": float, "reasoning": "string", "key_factors": [], "risk_flags": []}"""


class FundManager(BaseAgent):
    name = "fund_manager"
    model = "claude-sonnet-4-6"
    max_tokens = 800

    async def analyze(self, symbol: str, context: dict) -> AgentOutput:
        data_hash = hash_inputs(context)
        raw_text, _ = self._call_claude(SYSTEM_PROMPT, f"Final approval for {symbol}:\n{json.dumps(context, default=str)}")
        try:
            parsed = json.loads(raw_text.strip())
        except json.JSONDecodeError:
            parsed = {"signal": "SKIP", "confidence": 0.0, "reasoning": "Parse error", "key_factors": [], "risk_flags": []}
        return AgentOutput(agent_name=self.name, symbol=symbol, timestamp=datetime.now(timezone.utc),
            input_data_hash=data_hash, reasoning=parsed.get("reasoning", ""),
            signal=parsed.get("signal", "SKIP"), confidence=float(parsed.get("confidence", 0.0)),
            key_factors=parsed.get("key_factors", []), risk_flags=parsed.get("risk_flags", []))
