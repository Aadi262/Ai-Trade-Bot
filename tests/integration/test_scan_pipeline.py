import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.agents.graph import run_pipeline


@pytest.mark.asyncio
async def test_pipeline_returns_trading_state():
    mock_output = MagicMock()
    mock_output.signal = "HOLD"
    mock_output.confidence = 0.55
    mock_output.reasoning = "Mixed signals"
    mock_output.key_factors = []
    mock_output.risk_flags = []
    mock_output.model_dump.return_value = {}

    with patch("app.agents.technical.TechnicalAgent.analyze", new_callable=AsyncMock, return_value=mock_output), \
         patch("app.agents.fundamentals.FundamentalsAgent.analyze", new_callable=AsyncMock, return_value=mock_output), \
         patch("app.agents.sentiment.SentimentAgent.analyze", new_callable=AsyncMock, return_value=mock_output), \
         patch("app.agents.macro.MacroAgent.analyze", new_callable=AsyncMock, return_value=mock_output), \
         patch("app.agents.bull_researcher.BullResearcher.analyze", new_callable=AsyncMock, return_value=mock_output), \
         patch("app.agents.bear_researcher.BearResearcher.analyze", new_callable=AsyncMock, return_value=mock_output), \
         patch("app.agents.trader.TraderAgent.analyze", new_callable=AsyncMock, return_value=mock_output), \
         patch("app.agents.fund_manager.FundManager.analyze", new_callable=AsyncMock, return_value=mock_output):
        state = await run_pipeline("RELIANCE.NS")

    assert isinstance(state, dict)
    assert state.get("final_signal", "SKIP") in ("BUY", "SELL", "HOLD", "SKIP")
