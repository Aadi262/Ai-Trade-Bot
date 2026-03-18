import hashlib
import json
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any, Literal

import anthropic
import structlog
from pydantic import BaseModel, Field, field_validator

from app.core.config import settings

logger = structlog.get_logger(__name__)

SignalType = Literal["BUY", "SELL", "HOLD", "SKIP"]


class AgentOutput(BaseModel):
    agent_name: str
    symbol: str
    timestamp: datetime
    input_data_hash: str = Field(..., min_length=64, max_length=64)
    reasoning: str
    signal: SignalType
    confidence: float = Field(..., ge=0.0, le=1.0)
    key_factors: list[str] = Field(default_factory=list)
    risk_flags: list[str] = Field(default_factory=list)

    @field_validator("key_factors", "risk_flags")
    @classmethod
    def max_10_items(cls, v: list) -> list:
        if len(v) > 10:
            raise ValueError("max 10 items allowed")
        return v


def hash_inputs(data: Any) -> str:
    serialized = json.dumps(data, default=str, sort_keys=True)
    return hashlib.sha256(serialized.encode()).hexdigest()


class BaseAgent(ABC):
    name: str = "base"
    model: str = "claude-haiku-4-5-20251001"
    max_tokens: int = 1000

    def __init__(self) -> None:
        self._client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

    @abstractmethod
    async def analyze(self, symbol: str, context: dict) -> AgentOutput:
        ...

    def _call_claude(self, system: str, user: str) -> tuple[str, int]:
        msg = self._client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        return msg.content[0].text, msg.usage.input_tokens + msg.usage.output_tokens
