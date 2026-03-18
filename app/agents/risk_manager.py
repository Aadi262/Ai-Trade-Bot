from dataclasses import dataclass
import structlog
from app.agents.base import AgentOutput

logger = structlog.get_logger(__name__)

RISK_RULES = {
    "max_position_pct": 0.02,
    "max_open_positions": 5,
    "min_confidence": 0.65,
    "india_vix_pause_threshold": 16.0,
    "india_vix_resume_threshold": 14.0,
    "max_daily_loss_pct": 0.02,
    "max_drawdown_pct": 0.15,
    "order_type": "LIMIT",
    "limit_buffer_ticks": 2,
    "default_stop_loss_pct": 0.01,
    "default_target_pct": 0.02,
    "min_edge_pct": 0.003,
    "estimated_slippage_pct": 0.001,
    "zerodha_brokerage": 20,
}


@dataclass
class RiskDecision:
    approved: bool
    reason: str
    position_value: float | None = None
    stop_loss_pct: float = RISK_RULES["default_stop_loss_pct"]
    target_pct: float = RISK_RULES["default_target_pct"]


class RiskManager:
    """Hardcoded risk gate. Rules in RISK_RULES are sacred — never bypass."""

    def __init__(self, portfolio_value: float, open_positions: int,
                 daily_pnl_pct: float, total_drawdown_pct: float, india_vix: float) -> None:
        self.portfolio_value = portfolio_value
        self.open_positions = open_positions
        self.daily_pnl_pct = daily_pnl_pct
        self.total_drawdown_pct = total_drawdown_pct
        self.india_vix = india_vix

    def evaluate(self, signal: AgentOutput) -> RiskDecision:
        if signal.signal == "SKIP":
            return RiskDecision(approved=True, reason="SKIP signal — no position")

        if signal.confidence < RISK_RULES["min_confidence"]:
            reason = f"confidence {signal.confidence:.2f} below minimum {RISK_RULES['min_confidence']}"
            logger.info("risk_gate_rejected", gate="confidence", symbol=signal.symbol, reason=reason)
            return RiskDecision(approved=False, reason=reason)

        if self.india_vix > RISK_RULES["india_vix_pause_threshold"]:
            reason = f"india vix {self.india_vix:.1f} exceeds pause threshold {RISK_RULES['india_vix_pause_threshold']}"
            logger.info("risk_gate_rejected", gate="vix", symbol=signal.symbol, reason=reason)
            return RiskDecision(approved=False, reason=reason)

        if self.daily_pnl_pct <= -RISK_RULES["max_daily_loss_pct"]:
            reason = f"daily loss {self.daily_pnl_pct:.1%} hit limit {-RISK_RULES['max_daily_loss_pct']:.1%}"
            logger.info("risk_gate_rejected", gate="daily_loss", symbol=signal.symbol, reason=reason)
            return RiskDecision(approved=False, reason=reason)

        if self.total_drawdown_pct <= -RISK_RULES["max_drawdown_pct"]:
            reason = f"drawdown {self.total_drawdown_pct:.1%} exceeds max {-RISK_RULES['max_drawdown_pct']:.1%}"
            logger.info("risk_gate_rejected", gate="drawdown", symbol=signal.symbol, reason=reason)
            return RiskDecision(approved=False, reason=reason)

        if self.open_positions >= RISK_RULES["max_open_positions"]:
            reason = f"max open positions {RISK_RULES['max_open_positions']} reached ({self.open_positions} open)"
            logger.info("risk_gate_rejected", gate="positions", symbol=signal.symbol, reason=reason)
            return RiskDecision(approved=False, reason=reason)

        position_value = self.portfolio_value * RISK_RULES["max_position_pct"]
        logger.info("risk_gate_approved", symbol=signal.symbol, position_value=position_value)
        return RiskDecision(approved=True, reason="all risk gates passed", position_value=position_value)
