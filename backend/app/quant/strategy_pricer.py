from __future__ import annotations

from uuid import uuid4

from app.models.opportunity import Opportunity
from app.models.trade import Trade, TradeStatus


def price_strategy(opportunity: Opportunity) -> Trade | None:
    if not opportunity.legs:
        return None
    leg = min(opportunity.legs, key=lambda l: abs(l.strike - opportunity.underlying_price))
    entry_cost = leg.ask
    return Trade(
        id=str(uuid4()),
        opportunity_id=opportunity.id,
        underlying_symbol=opportunity.underlying_symbol,
        strategy_name="single_leg",
        legs=[leg],
        quantity=1,
        entry_cost=entry_cost,
        max_loss=entry_cost,
        status=TradeStatus.PROPOSED,
    )
