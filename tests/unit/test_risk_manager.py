import pytest
from app.agents.risk_manager import RiskManager, RiskDecision, RISK_RULES
from app.agents.base import AgentOutput
from datetime import datetime


@pytest.fixture
def passing_signal() -> AgentOutput:
    return AgentOutput(
        agent_name="trader", symbol="RELIANCE.NS",
        timestamp=datetime.utcnow(), input_data_hash="a" * 64,
        reasoning="Strong breakout", signal="BUY", confidence=0.80,
        key_factors=["EMA cross", "Volume surge"], risk_flags=[],
    )


@pytest.fixture
def rm() -> RiskManager:
    return RiskManager(
        portfolio_value=100_000, open_positions=2,
        daily_pnl_pct=0.0, total_drawdown_pct=0.0, india_vix=12.0,
    )


def test_rejects_low_confidence(rm, passing_signal):
    passing_signal.confidence = 0.60
    decision = rm.evaluate(passing_signal)
    assert decision.approved is False
    assert "confidence" in decision.reason.lower()


def test_accepts_at_threshold(rm, passing_signal):
    passing_signal.confidence = 0.65
    decision = rm.evaluate(passing_signal)
    assert decision.approved is True


def test_rejects_when_vix_above_threshold(passing_signal):
    rm_high_vix = RiskManager(portfolio_value=100_000, open_positions=0,
        daily_pnl_pct=0.0, total_drawdown_pct=0.0, india_vix=17.0)
    decision = rm_high_vix.evaluate(passing_signal)
    assert decision.approved is False
    assert "vix" in decision.reason.lower()


def test_accepts_when_vix_below_pause(passing_signal):
    rm_ok_vix = RiskManager(portfolio_value=100_000, open_positions=0,
        daily_pnl_pct=0.0, total_drawdown_pct=0.0, india_vix=15.0)
    decision = rm_ok_vix.evaluate(passing_signal)
    assert decision.approved is True


def test_rejects_when_daily_loss_exceeded(passing_signal):
    rm_loss = RiskManager(portfolio_value=100_000, open_positions=0,
        daily_pnl_pct=-0.025, total_drawdown_pct=0.0, india_vix=12.0)
    decision = rm_loss.evaluate(passing_signal)
    assert decision.approved is False
    assert "daily loss" in decision.reason.lower()


def test_accepts_at_daily_loss_limit(passing_signal):
    rm_ok = RiskManager(portfolio_value=100_000, open_positions=0,
        daily_pnl_pct=-0.019, total_drawdown_pct=0.0, india_vix=12.0)
    decision = rm_ok.evaluate(passing_signal)
    assert decision.approved is True


def test_rejects_when_drawdown_exceeded(passing_signal):
    rm_dd = RiskManager(portfolio_value=100_000, open_positions=0,
        daily_pnl_pct=0.0, total_drawdown_pct=-0.16, india_vix=12.0)
    decision = rm_dd.evaluate(passing_signal)
    assert decision.approved is False
    assert "drawdown" in decision.reason.lower()


def test_rejects_when_max_positions_reached(passing_signal):
    rm_full = RiskManager(portfolio_value=100_000, open_positions=5,
        daily_pnl_pct=0.0, total_drawdown_pct=0.0, india_vix=12.0)
    decision = rm_full.evaluate(passing_signal)
    assert decision.approved is False
    assert "positions" in decision.reason.lower()


def test_position_size_max_2pct_of_portfolio(rm, passing_signal):
    decision = rm.evaluate(passing_signal)
    if decision.approved and decision.position_value is not None:
        assert decision.position_value <= rm.portfolio_value * RISK_RULES["max_position_pct"]


def test_skip_signal_always_approved(rm, passing_signal):
    passing_signal.signal = "SKIP"
    passing_signal.confidence = 0.0
    decision = rm.evaluate(passing_signal)
    assert decision.approved is True
