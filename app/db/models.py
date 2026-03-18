import uuid
from datetime import date, datetime, timezone

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(sa.Uuid, primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(sa.String(255), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(sa.Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), default=_utcnow
    )
    signals: Mapped[list["Signal"]] = relationship(back_populates="user")


class Signal(Base):
    __tablename__ = "signals"

    id: Mapped[uuid.UUID] = mapped_column(sa.Uuid, primary_key=True, default=uuid.uuid4)
    symbol: Mapped[str] = mapped_column(sa.String(25), nullable=False, index=True)
    signal: Mapped[str] = mapped_column(sa.String(10), nullable=False)
    confidence: Mapped[float] = mapped_column(sa.Float, nullable=False)
    entry_price: Mapped[float | None] = mapped_column(sa.Numeric(10, 2))
    stop_loss: Mapped[float | None] = mapped_column(sa.Numeric(10, 2))
    target_price: Mapped[float | None] = mapped_column(sa.Numeric(10, 2))
    india_vix_at_signal: Mapped[float | None] = mapped_column(sa.Float)
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), default=_utcnow, index=True
    )
    task_id: Mapped[str | None] = mapped_column(sa.String(100))
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        sa.Uuid, sa.ForeignKey("users.id")
    )
    user: Mapped["User | None"] = relationship(back_populates="signals")
    audit_logs: Mapped[list["AuditLog"]] = relationship(back_populates="signal")
    trades: Mapped[list["Trade"]] = relationship(back_populates="signal")


class AuditLog(Base):
    __tablename__ = "audit_log"

    id: Mapped[uuid.UUID] = mapped_column(sa.Uuid, primary_key=True, default=uuid.uuid4)
    signal_id: Mapped[uuid.UUID | None] = mapped_column(
        sa.Uuid, sa.ForeignKey("signals.id")
    )
    agent_name: Mapped[str] = mapped_column(sa.String(50), nullable=False)
    input_data_hash: Mapped[str] = mapped_column(sa.String(64), nullable=False)
    reasoning: Mapped[str] = mapped_column(sa.Text, nullable=False)
    output_signal: Mapped[str | None] = mapped_column(sa.String(10))
    confidence: Mapped[float | None] = mapped_column(sa.Float)
    key_factors: Mapped[list | None] = mapped_column(sa.JSON)
    risk_flags: Mapped[list | None] = mapped_column(sa.JSON)
    latency_ms: Mapped[int | None] = mapped_column(sa.Integer)
    model_used: Mapped[str | None] = mapped_column(sa.String(50))
    tokens_used: Mapped[int | None] = mapped_column(sa.Integer)
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), default=_utcnow, index=True
    )
    signal: Mapped["Signal | None"] = relationship(back_populates="audit_logs")


_TRADE_STATUS_OPEN = "OPEN"


class Trade(Base):
    __tablename__ = "trades"

    id: Mapped[uuid.UUID] = mapped_column(sa.Uuid, primary_key=True, default=uuid.uuid4)
    signal_id: Mapped[uuid.UUID | None] = mapped_column(
        sa.Uuid, sa.ForeignKey("signals.id")
    )
    symbol: Mapped[str] = mapped_column(sa.String(25), nullable=False, index=True)
    trade_type: Mapped[str] = mapped_column(sa.String(10), nullable=False)
    direction: Mapped[str] = mapped_column(sa.String(5), nullable=False)
    quantity: Mapped[int] = mapped_column(sa.Integer, nullable=False)
    entry_price: Mapped[float | None] = mapped_column(sa.Numeric(10, 2))
    exit_price: Mapped[float | None] = mapped_column(sa.Numeric(10, 2))
    stop_loss: Mapped[float | None] = mapped_column(sa.Numeric(10, 2))
    target_price: Mapped[float | None] = mapped_column(sa.Numeric(10, 2))
    # status has a Python-level default so that unsaved Trade objects reflect "OPEN"
    # without requiring a DB flush.
    status: Mapped[str] = mapped_column(
        sa.String(20), default=_TRADE_STATUS_OPEN, server_default=_TRADE_STATUS_OPEN
    )
    pnl: Mapped[float | None] = mapped_column(sa.Numeric(10, 2))
    brokerage_cost: Mapped[float | None] = mapped_column(sa.Numeric(10, 2))
    slippage: Mapped[float | None] = mapped_column(sa.Numeric(10, 2))
    entry_at: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True))
    exit_at: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True))
    exit_reason: Mapped[str | None] = mapped_column(sa.String(50))
    signal: Mapped["Signal | None"] = relationship(back_populates="trades")

    def __init__(self, **kwargs: object) -> None:
        kwargs.setdefault("status", _TRADE_STATUS_OPEN)
        super().__init__(**kwargs)


class DailyPnL(Base):
    __tablename__ = "daily_pnl"

    id: Mapped[uuid.UUID] = mapped_column(sa.Uuid, primary_key=True, default=uuid.uuid4)
    date: Mapped[date] = mapped_column(sa.Date, unique=True, nullable=False)
    gross_pnl: Mapped[float | None] = mapped_column(sa.Numeric(10, 2))
    net_pnl: Mapped[float | None] = mapped_column(sa.Numeric(10, 2))
    total_trades: Mapped[int | None] = mapped_column(sa.Integer)
    winning_trades: Mapped[int | None] = mapped_column(sa.Integer)
    losing_trades: Mapped[int | None] = mapped_column(sa.Integer)
    win_rate: Mapped[float | None] = mapped_column(sa.Float)
    max_drawdown_pct: Mapped[float | None] = mapped_column(sa.Float)
    sharpe_rolling_30d: Mapped[float | None] = mapped_column(sa.Float)
    india_vix_avg: Mapped[float | None] = mapped_column(sa.Float)
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), default=_utcnow
    )
