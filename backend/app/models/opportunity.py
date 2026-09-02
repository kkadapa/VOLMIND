from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class OptionType(str, Enum):
    CALL = "call"
    PUT = "put"


class OptionLeg(BaseModel):
    symbol: str
    option_type: OptionType
    strike: float
    expiry: datetime
    bid: float
    ask: float
    implied_volatility: float | None = None
    delta: float | None = None
    gamma: float | None = None
    theta: float | None = None
    vega: float | None = None
    open_interest: int | None = None
    volume: int | None = None


class Opportunity(BaseModel):
    id: str
    underlying_symbol: str
    underlying_price: float
    discovered_at: datetime
    legs: list[OptionLeg]
    source: str
    notes: str | None = None
