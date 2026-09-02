from __future__ import annotations

from app.observability import log_agent_decision
from app.orchestration.state import GraphState

NAME = "evaluator_agent"


def run(state: GraphState) -> dict:
    report = state.get("diligence_report")
    executed_trade = state.get("executed_trade")
    if report is not None and not report.passed:
        notes = f"No trade: flagged in diligence review. {state.get('diligence_notes', '')}"
    elif not state.get("risk_approved"):
        notes = f"No trade: flagged by Risk Agent. {state.get('risk_notes', 'no reason given')}"
    elif executed_trade is not None:
        strategy = executed_trade.strategy_name.replace("_", " ")
        notes = (
            f"{executed_trade.underlying_symbol} {strategy} trade submitted as a paper "
            f"order (id {executed_trade.id[:8]}) and is now being monitored."
        )
    else:
        notes = "Trade cleared all pipeline stages but execution did not submit an order."

    log_agent_decision(
        trace_id=state.get("trace_id", "unknown"),
        agent=NAME,
        input_summary={
            "diligence_passed": report.passed if report else None,
            "risk_approved": state.get("risk_approved"),
        },
        output_summary={"notes": notes, "executed_trade_id": executed_trade.id if executed_trade else None},
        confidence=None,
        decision="executed" if executed_trade else "not_executed",
        reason=notes,
    )
    return {"evaluation_notes": notes}
