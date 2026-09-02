from __future__ import annotations

from app.observability import log_agent_decision
from app.orchestration.state import GraphState
from app.quant.divergence import compute_divergence

NAME = "divergence_agent"


def run(state: GraphState) -> dict:
    predictions = state["predictions"]
    market_probability = state["market_implied_probability"]
    agent_probability = predictions[-1].probability if predictions else 0.5
    score = compute_divergence(agent_probability, market_probability)
    log_agent_decision(
        trace_id=state.get("trace_id", "unknown"),
        agent=NAME,
        input_summary={"ai_probability": agent_probability, "market_probability": market_probability},
        output_summary={"divergence_score": score},
        confidence=None,
        decision="computed",
        reason=f"AI {agent_probability:.2f} vs market {market_probability:.2f}",
    )
    return {"divergence_score": score}
