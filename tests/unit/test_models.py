from app.db.models import Signal, AuditLog, Trade, DailyPnL, User


def test_signal_columns():
    cols = {c.name for c in Signal.__table__.columns}
    assert {"id", "symbol", "signal", "confidence", "entry_price",
            "stop_loss", "target_price", "india_vix_at_signal",
            "created_at", "task_id", "user_id"} <= cols


def test_audit_log_columns():
    cols = {c.name for c in AuditLog.__table__.columns}
    assert {"id", "signal_id", "agent_name", "input_data_hash",
            "reasoning", "output_signal", "confidence",
            "key_factors", "risk_flags", "latency_ms",
            "model_used", "tokens_used", "created_at"} <= cols


def test_trade_columns():
    cols = {c.name for c in Trade.__table__.columns}
    assert {"id", "signal_id", "symbol", "trade_type", "direction",
            "quantity", "entry_price", "exit_price", "stop_loss",
            "target_price", "status", "pnl", "brokerage_cost",
            "slippage", "entry_at", "exit_at", "exit_reason"} <= cols


def test_daily_pnl_columns():
    cols = {c.name for c in DailyPnL.__table__.columns}
    assert {"id", "date", "gross_pnl", "net_pnl", "total_trades",
            "winning_trades", "losing_trades", "win_rate",
            "max_drawdown_pct", "sharpe_rolling_30d",
            "india_vix_avg", "created_at"} <= cols


def test_signal_valid_values():
    import sqlalchemy as sa
    col = Signal.__table__.columns["signal"]
    assert isinstance(col.type, sa.String)


def test_trade_status_default():
    t = Trade(
        symbol="RELIANCE.NS",
        trade_type="PAPER",
        direction="BUY",
        quantity=1,
    )
    assert t.status == "OPEN"
