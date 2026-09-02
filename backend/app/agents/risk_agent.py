from __future__ import annotations

from app.memory.trade_memory import TradeMemory
from app.observability import log_agent_decision
from app.orchestration.state import GraphState
from app.quant.risk import evaluate_trade_risk

NAME = "risk_agent"


def run(state: GraphState) -> dict:
    trade = state.get("proposed_trade")
    if trade is None:
        approved, notes = False, "No trade proposed."
    else:
        trade_memory = TradeMemory()
        open_position_count = len(trade_memory.load_open())
        realized_loss_today = sum(
            t.realized_pnl for t in trade_memory.load_closed_today() if t.realized_pnl is not None
        )
        approved, notes = evaluate_trade_risk(trade, open_position_count, realized_loss_today)

    log_agent_decision(
        trace_id=state.get("trace_id", "unknown"),
        agent=NAME,
        input_summary={"trade_id": trade.id if trade else None},
        output_summary={"risk_approved": approved, "risk_notes": notes},
        confidence=None,
        decision="approved" if approved else "vetoed",
        reason=notes,
    )
    return {"risk_approved": approved, "risk_notes": notes}
