from __future__ import annotations

from app.observability import log_agent_decision
from app.orchestration.state import GraphState
from app.services.execution_service import ExecutionService

NAME = "execution_agent"


def run(state: GraphState) -> dict:
    trade = ExecutionService().execute(state)

    log_agent_decision(
        trace_id=state.get("trace_id", "unknown"),
        agent=NAME,
        input_summary={
            "trade_id": state["proposed_trade"].id if state.get("proposed_trade") else None,
            "risk_approved": state.get("risk_approved"),
        },
        output_summary={"executed_trade_id": trade.id if trade else None},
        confidence=None,
        decision="submitted" if trade else "skipped",
        reason="Risk-approved trade submitted as a paper order."
        if trade
        else "No risk-approved trade to execute.",
    )
    return {"executed_trade": trade}
