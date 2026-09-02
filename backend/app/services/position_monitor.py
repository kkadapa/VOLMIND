from __future__ import annotations

from datetime import datetime, timezone
from typing import Callable

from loguru import logger

from app.alpaca.options import get_option_quote
from app.alpaca.trading import close_position
from app.config import get_settings
from app.memory.agent_reputation import PIPELINE_AGENTS, AgentReputation
from app.memory.trade_memory import TradeMemory
from app.models.trade import Trade, TradeStatus
from app.observability import log_agent_decision
from app.quant.constants import CONTRACT_MULTIPLIER

NAME = "position_monitor"

QuoteFn = Callable[[str], "tuple[float, float] | None"]
CloseFn = Callable[[Trade], object]


class PositionMonitor:
    """Marks open trades to market and closes anything that hits an exit rule.

    Exit rules, in the order they're checked: take-profit, stop-loss, then a
    days-to-expiry cutoff (closing early avoids pin/assignment risk right at
    expiration). The first rule that trips wins; a trade with no rule triggered
    stays open for the next cycle.
    """

    def __init__(
        self,
        trade_memory: TradeMemory | None = None,
        quote_fn: QuoteFn = get_option_quote,
        close_fn: CloseFn = close_position,
        reputation: AgentReputation | None = None,
    ):
        self.trade_memory = trade_memory or TradeMemory()
        self.quote_fn = quote_fn
        self.close_fn = close_fn
        self.reputation = reputation or AgentReputation()

    def run_cycle(self) -> list[Trade]:
        closed: list[Trade] = []
        for trade in self.trade_memory.load_open():
            exit_reason = self._check_exit(trade)
            if exit_reason is not None:
                closed_trade = self._close(trade, exit_reason)
                if closed_trade is not None:
                    closed.append(closed_trade)
        return closed

    def _check_exit(self, trade: Trade) -> str | None:
        settings = get_settings()
        leg = trade.legs[0]

        days_to_expiry = (leg.expiry - datetime.now(timezone.utc)).days
        if days_to_expiry <= settings.min_days_to_expiry_exit:
            return f"{days_to_expiry}d to expiry (limit {settings.min_days_to_expiry_exit}d)"

        quote = self.quote_fn(leg.symbol)
        if quote is None:
            return None
        bid, _ask = quote

        pnl_pct = (bid - trade.entry_cost) / trade.entry_cost if trade.entry_cost else 0.0
        if pnl_pct >= settings.take_profit_pct:
            return f"take-profit: +{pnl_pct:.0%} (target {settings.take_profit_pct:.0%})"
        if pnl_pct <= -settings.stop_loss_pct:
            return f"stop-loss: {pnl_pct:.0%} (limit -{settings.stop_loss_pct:.0%})"

        return None

    def _close(self, trade: Trade, exit_reason: str) -> Trade | None:
        settings = get_settings()
        settings.require_paper_trading()

        quote = self.quote_fn(trade.legs[0].symbol)
        exit_price = quote[0] if quote is not None else trade.entry_cost
        realized_pnl = (exit_price - trade.entry_cost) * trade.quantity * CONTRACT_MULTIPLIER

        try:
            self.close_fn(trade)
        except Exception:
            logger.exception("position_monitor: failed to submit close order for {}", trade.id)
            return None

        trade.status = TradeStatus.CLOSED
        trade.closed_at = datetime.now(timezone.utc)
        trade.realized_pnl = realized_pnl
        self.trade_memory.save(trade)

        correct = realized_pnl > 0
        brier_score = 0.0 if correct else 1.0
        for agent_name in PIPELINE_AGENTS:
            self.reputation.record_outcome(agent_name, correct, brier_score)

        log_agent_decision(
            trace_id=trade.id,
            agent=NAME,
            input_summary={"trade_id": trade.id, "symbol": trade.underlying_symbol},
            output_summary={"realized_pnl": realized_pnl, "exit_reason": exit_reason},
            confidence=None,
            decision="closed",
            reason=exit_reason,
        )
        return trade
