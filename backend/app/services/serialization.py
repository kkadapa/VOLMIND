from __future__ import annotations

from typing import Any

from app.orchestration.state import GraphState


def _status(state: GraphState) -> str:
    report = state.get("diligence_report")
    if report is not None and not report.passed:
        return "no_trade_diligence"
    if state.get("proposed_trade") is None:
        return "screening"
    if not state.get("risk_approved"):
        return "no_trade_risk"
    return "cleared"


def _opportunity_score(state: GraphState) -> float:
    """Simplified magnitude-of-edge score for the Market Radar's sort column.

    Not the full risk/liquidity-adjusted opportunity score described in the
    product spec (Agent 6) -- just |divergence| scaled by forecast confidence,
    so a big gap the model isn't sure about doesn't outrank a smaller, confident one.
    """
    divergence = state.get("divergence_score") or 0.0
    forecast = state.get("probability_forecast")
    confidence = forecast.confidence if forecast else 0.0
    return round(abs(divergence) * confidence, 4)


def serialize_state(state: GraphState) -> dict[str, Any]:
    opportunity = state["opportunity"]
    news_assessment = state.get("news_assessment")
    fundamental_assessment = state.get("fundamental_assessment")
    forecast = state.get("probability_forecast")
    diligence_report = state.get("diligence_report")
    proposed_trade = state.get("proposed_trade")
    executed_trade = state.get("executed_trade")

    return {
        "trace_id": state.get("trace_id"),
        "ticker": opportunity.underlying_symbol,
        "price": opportunity.underlying_price,
        "discovered_at": opportunity.discovered_at.isoformat(),
        "opportunity": opportunity.model_dump(mode="json"),
        "news_assessment": news_assessment.model_dump(mode="json") if news_assessment else None,
        "fundamental_assessment": (
            fundamental_assessment.model_dump(mode="json") if fundamental_assessment else None
        ),
        "probability_forecast": forecast.model_dump(mode="json") if forecast else None,
        "market_implied_probability": state.get("market_implied_probability"),
        "divergence_score": state.get("divergence_score"),
        "opportunity_score": _opportunity_score(state),
        "diligence_report": diligence_report.model_dump(mode="json") if diligence_report else None,
        "proposed_trade": proposed_trade.model_dump(mode="json") if proposed_trade else None,
        "executed_trade": executed_trade.model_dump(mode="json") if executed_trade else None,
        "risk_approved": state.get("risk_approved"),
        "risk_notes": state.get("risk_notes"),
        "evaluation_notes": state.get("evaluation_notes"),
        "status": _status(state),
    }
