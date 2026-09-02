from __future__ import annotations

from app.observability import log_agent_decision
from app.orchestration.state import GraphState
from app.quant.strategy_pricer import price_strategy

NAME = "options_architect_agent"


def run(state: GraphState) -> dict:
    opportunity = state["opportunity"]
    trade = price_strategy(opportunity)
    log_agent_decision(
        trace_id=state.get("trace_id", "unknown"),
        agent=NAME,
        input_summary={"symbol": opportunity.underlying_symbol, "legs": len(opportunity.legs)},
        output_summary={"trade_id": trade.id if trade else None, "strategy": trade.strategy_name if trade else None},
        confidence=None,
        decision="proposed" if trade else "no_strategy",
        reason="Nearest-ATM single-leg pricer; multi-strategy comparison not yet implemented.",
    )
    return {"proposed_trade": trade}
