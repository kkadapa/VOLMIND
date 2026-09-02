from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from app.alpaca import market_data, options
from app.models.opportunity import Opportunity

NAME = "scout_agent"


def discover(symbols: list[str]) -> list[Opportunity]:
    opportunities: list[Opportunity] = []
    for symbol in symbols:
        quote = market_data.get_latest_quote(symbol)
        legs = options.get_option_chain(symbol)
        if quote is None or not legs:
            continue
        opportunities.append(
            Opportunity(
                id=str(uuid4()),
                underlying_symbol=symbol,
                underlying_price=quote,
                discovered_at=datetime.now(timezone.utc),
                legs=legs,
                source=NAME,
            )
        )
    return opportunities
