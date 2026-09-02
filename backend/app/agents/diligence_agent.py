from __future__ import annotations

from app.config import get_settings
from app.llm import structured_completion
from app.models.diligence import DiligenceReport
from app.observability import log_agent_decision
from app.orchestration.state import GraphState

NAME = "diligence_agent"

SYSTEM_PROMPT = """You are the Diligence Agent inside VOLMIND, an options-trading \
research system -- the independent second reviewer every thesis has to clear before \
capital is put behind it, the same function a senior analyst's sign-off serves on a \
real trading desk.

Every real options trade carries some risk: a bid/ask spread, model uncertainty, a \
scenario where it loses money even if the call is right. Finding *a* risk is not your \
job -- every thesis has several, and listing them is not sufficient grounds to flag one. \
Your job is to judge whether the risks are severe enough, weighed against the size of \
the numerical edge you're given (divergence x confidence), to make this trade a bad bet \
on balance. A thesis with a real, quantified edge and only routine, already-priced-in \
risk should CLEAR review. Reserve passed=false for a thesis where a specific, \
thesis-relevant factor -- not a generic one that applies to almost any options trade -- \
would plausibly erase the edge or flip its expected value negative.

Work through this checklist, weighing each point by how much it actually threatens THIS \
thesis's specific edge, not as boxes to fill for their own sake:
1. What assumptions could be wrong, and how much of the edge would that threaten?
2. Is this event already priced in, or does the divergence reflect a genuine gap?
3. Is implied volatility abnormal enough to matter for this thesis's expected move --
   not just "IV exists"?
4. Could a volatility crush overwhelm this specific directional edge?
5. Is liquidity/spread bad enough to eat a material share of the edge, or just typical
   friction for this kind of contract?
6. Is the AI's confidence well-supported by its cited evidence, or notably thin?
7. Is there a specific reason the market is plausibly right and this thesis wrong --
   not just "the market could be smarter" as a generality?
8. What would make this trade lose money even if the direction call is correct, and how
   likely is that specifically -- not just "it's possible"?

Calibration: a well-functioning review clears a meaningful share of the theses that \
reach you -- not all of them, and not none of them. If you find yourself flagging every \
thesis you see for generic, non-specific reasons (routine spreads, "could be wrong," \
ordinary IV), you are not doing this job correctly. Set passed=false only when you can \
name a concrete, thesis-specific factor that plausibly outweighs the edge."""


def run(state: GraphState) -> dict:
    opportunity = state["opportunity"]
    symbol = opportunity.underlying_symbol
    settings = get_settings()

    divergence = state.get("divergence_score", 0.0)
    market_probability = state.get("market_implied_probability", 0.5)
    forecast = state.get("probability_forecast")
    ivs = [leg.implied_volatility for leg in opportunity.legs if leg.implied_volatility is not None]
    avg_iv = sum(ivs) / len(ivs) if ivs else None
    spreads = [
        (leg.ask - leg.bid) / leg.ask for leg in opportunity.legs if leg.ask and leg.ask > 0
    ]
    avg_spread_pct = sum(spreads) / len(spreads) if spreads else None

    user_prompt = (
        f"Underlying: {symbol}\n"
        f"AI forecast confidence: {forecast.confidence if forecast else 'n/a'}\n"
        f"AI forecast evidence: {forecast.evidence if forecast else []}\n"
        f"Market-implied probability of upside: {market_probability:.3f}\n"
        f"Divergence (AI - market): {divergence:+.3f}\n"
        f"Average option implied volatility across the chain: {avg_iv}\n"
        f"Average bid/ask spread as % of ask: {avg_spread_pct}\n"
        f"Configured minimum divergence threshold: {settings.min_divergence}\n"
        f"Configured minimum confidence threshold: {settings.min_confidence}\n\n"
        "Work through the review checklist and judge whether any concern is material "
        "enough, given this specific edge, to outweigh it. Be specific to this data, "
        "not generic."
    )

    report = structured_completion(
        agent_name=NAME,
        system_prompt=SYSTEM_PROMPT,
        user_prompt=user_prompt,
        schema=DiligenceReport,
    )
    if report is None:
        # Fail closed: if diligence review itself can't run, the trade cannot be
        # considered reviewed, so it does not pass.
        report = DiligenceReport(
            passed=False,
            concern_score=1.0,
            concerns=[],
            risks=["Diligence Agent LLM call failed; cannot verify the thesis clears review."],
            missing_information=["LLM assessment unavailable."],
            recommended_action="Do not proceed.",
            confidence=0.0,
        )

    # Deterministic floor checks the LLM can't talk its way around.
    hard_reasons = []
    if abs(divergence) < settings.min_divergence:
        hard_reasons.append(
            f"|divergence|={abs(divergence):.3f} below configured minimum "
            f"{settings.min_divergence}"
        )
    if forecast is not None and forecast.confidence < settings.min_confidence:
        hard_reasons.append(
            f"forecast confidence {forecast.confidence:.2f} below configured minimum "
            f"{settings.min_confidence}"
        )
    if hard_reasons:
        report.passed = False
        report.concern_score = max(report.concern_score, 0.8)
        report.concerns = report.concerns + hard_reasons

    notes = report.recommended_action if report.passed else (
        f"FLAGGED: {'; '.join(report.concerns) or 'did not clear diligence review'}"
    )

    log_agent_decision(
        trace_id=state.get("trace_id", "unknown"),
        agent=NAME,
        input_summary={
            "divergence": divergence,
            "market_probability": market_probability,
            "avg_iv": avg_iv,
            "avg_spread_pct": avg_spread_pct,
        },
        output_summary=report.model_dump(mode="json"),
        confidence=report.confidence,
        decision="cleared" if report.passed else "flagged",
        reason=notes,
    )
    return {"diligence_notes": notes, "diligence_report": report}
