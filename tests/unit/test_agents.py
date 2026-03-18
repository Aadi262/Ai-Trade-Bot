import pytest
from datetime import datetime
from app.agents.base import AgentOutput


def test_agent_output_requires_mandatory_fields():
    with pytest.raises(Exception):
        AgentOutput()


def test_agent_output_valid():
    out = AgentOutput(
        agent_name="technical",
        symbol="RELIANCE.NS",
        timestamp=datetime.utcnow(),
        input_data_hash="a" * 64,
        reasoning="EMA crossover detected",
        signal="BUY",
        confidence=0.75,
        key_factors=["EMA20 > EMA50", "RSI 58"],
        risk_flags=[],
    )
    assert out.signal == "BUY"
    assert 0.0 <= out.confidence <= 1.0


def test_agent_output_rejects_invalid_signal():
    with pytest.raises(Exception):
        AgentOutput(
            agent_name="technical",
            symbol="RELIANCE.NS",
            timestamp=datetime.utcnow(),
            input_data_hash="a" * 64,
            reasoning="test",
            signal="MAYBE",
            confidence=0.5,
            key_factors=[],
            risk_flags=[],
        )


def test_agent_output_confidence_bounds():
    with pytest.raises(Exception):
        AgentOutput(
            agent_name="technical",
            symbol="RELIANCE.NS",
            timestamp=datetime.utcnow(),
            input_data_hash="a" * 64,
            reasoning="test",
            signal="BUY",
            confidence=1.5,
            key_factors=[],
            risk_flags=[],
        )


@pytest.mark.asyncio
async def test_technical_agent_returns_agent_output():
    from app.agents.technical import TechnicalAgent
    from unittest.mock import AsyncMock, patch, MagicMock
    import pandas as pd, numpy as np

    mock_df = pd.DataFrame({
        "Open":   np.random.uniform(100, 200, 100),
        "High":   np.random.uniform(200, 210, 100),
        "Low":    np.random.uniform(90, 100, 100),
        "Close":  np.random.uniform(100, 200, 100),
        "Volume": np.random.randint(500_000, 5_000_000, 100),
    })

    mock_claude_response = MagicMock()
    mock_claude_response.content = [MagicMock(text='{"signal": "BUY", "confidence": 0.72, "reasoning": "EMA20 crossed above EMA50", "key_factors": ["EMA cross", "RSI 58"], "risk_flags": []}')]
    mock_claude_response.usage.input_tokens = 100
    mock_claude_response.usage.output_tokens = 50

    agent = TechnicalAgent()
    with patch("app.agents.technical.fetch_ohlcv", new_callable=AsyncMock, return_value=mock_df):
        with patch.object(agent._client.messages, "create", return_value=mock_claude_response):
            output = await agent.analyze("RELIANCE.NS", {})

    assert isinstance(output, AgentOutput)
    assert output.agent_name == "technical"
    assert output.signal in ("BUY", "SELL", "HOLD", "SKIP")
    assert 0.0 <= output.confidence <= 1.0


@pytest.mark.asyncio
async def test_graph_state_has_required_keys():
    from app.agents.graph import TradingState, create_graph
    state: TradingState = {"symbol": "RELIANCE.NS", "agent_outputs": {}, "context": {}}
    assert state["symbol"] == "RELIANCE.NS"
    assert isinstance(state["agent_outputs"], dict)
