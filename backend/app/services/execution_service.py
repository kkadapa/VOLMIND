from __future__ import annotations

from datetime import datetime, timezone

from loguru import logger

from app.alpaca.trading import submit_trade
from app.config import get_settings
from app.memory.trade_memory import TradeMemory
from app.models.trade import Trade, TradeStatus
from app.orchestration.state import GraphState


class ExecutionService:
    def __init__(self, trade_memory: TradeMemory | None = None):
        self.trade_memory = trade_memory or TradeMemory()

    def execute(self, state: GraphState) -> Trade | None:
        trade = state.get("proposed_trade")
        if trade is None or not state.get("risk_approved"):
            return None

        # Fail closed: this call raises unless ALPACA_PAPER_TRADE is exactly "true".
        # No trade reaches Alpaca without passing this guard, regardless of what
        # upstream agents approved.
        get_settings().require_paper_trading()
        logger.info("execution_service: submitting paper trade {}", trade.id)

        limit_price = trade.entry_cost
        submit_trade(trade, limit_price)

        trade.status = TradeStatus.OPEN
        trade.opened_at = datetime.now(timezone.utc)
        self.trade_memory.save(trade)
        return trade
