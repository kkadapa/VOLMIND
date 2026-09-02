from __future__ import annotations

from app.observability import log_agent_decision
from app.orchestration.state import GraphState
from app.quant.implied_probability import implied_probability_from_chain

NAME = "market_probability_agent"


def run(state: GraphState) -> dict:
    opportunity = state["opportunity"]
    probability = implied_probability_from_chain(opportunity.legs, opportunity.underlying_price)
    log_agent_decision(
        trace_id=state.get("trace_id", "unknown"),
        agent=NAME,
        input_summary={"symbol": opportunity.underlying_symbol, "legs": len(opportunity.legs)},
        output_summary={"market_implied_probability": probability},
        confidence=None,
        decision="computed",
        reason="Delta-approximated P(price above spot); see quant.implied_probability docstring for assumptions.",
    )
    return {"market_implied_probability": probability}
