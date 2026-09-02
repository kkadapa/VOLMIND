from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel

from app.models.opportunity import OptionLeg


class TradeStatus(str, Enum):
    PROPOSED = "proposed"
    OPEN = "open"
    CLOSED = "closed"
    REJECTED = "rejected"


class Trade(BaseModel):
    id: str
    opportunity_id: str
    underlying_symbol: str
    strategy_name: str
    legs: list[OptionLeg]
    quantity: int
    entry_cost: float
    max_loss: float
    max_profit: float | None = None
    status: TradeStatus
    opened_at: datetime | None = None
    closed_at: datetime | None = None
    realized_pnl: float | None = None
