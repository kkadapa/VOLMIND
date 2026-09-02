from __future__ import annotations

from datetime import datetime, timezone

from app.llm import structured_completion
from app.models.prediction import Direction, Prediction, ProbabilityForecast
from app.observability import log_agent_decision
from app.orchestration.state import GraphState
from app.quant.divergence import probability_of_upside

NAME = "probability_agent"
OUTCOMES = ["+10%", "+5%", "flat", "-5%", "-10%"]
HORIZON = "21d"

SYSTEM_PROMPT = f"""You are the Probability Agent inside VOLMIND, an options-trading \
research system. You are the core forecasting agent: given evidence from the News \
and Fundamental agents, you must estimate a probability distribution over price \
outcomes for one underlying at a fixed horizon, over exactly these mutually \
exclusive buckets: {", ".join(OUTCOMES)} (probabilities must sum to 1.0).

You MUST ground every number in the evidence you were given -- list the specific \
pieces of evidence you used in `evidence`. If the evidence is thin or contradictory, \
say so and keep the distribution close to a neutral prior (most mass on "flat") with \
low confidence. Do not invent probabilities with no basis in the evidence provided.
"""


def _fallback_forecast(symbol: str) -> ProbabilityForecast:
    return ProbabilityForecast(
        ticker=symbol,
        event=f"{HORIZON} price move",
        horizon=HORIZON,
        probabilities={"+10%": 0.05, "+5%": 0.15, "flat": 0.6, "-5%": 0.15, "-10%": 0.05},
        expected_move=0.0,
        confidence=0.0,
        evidence=[],
        model_version="fallback-neutral-prior",
    )


def run(state: GraphState) -> dict:
    opportunity = state["opportunity"]
    symbol = opportunity.underlying_symbol
    news_assessment = state.get("news_assessment")
    fundamental_assessment = state.get("fundamental_assessment")

    evidence_lines = []
    if news_assessment:
        evidence_lines.append(
            f"News ({news_assessment.confidence:.2f} conf): {news_assessment.what_changed} "
            f"-> expects {news_assessment.expected_direction.value}, "
            f"magnitude {news_assessment.expected_magnitude:.2f}"
        )
    if fundamental_assessment:
        evidence_lines.append(
            f"Fundamental ({fundamental_assessment.confidence:.2f} conf): "
            f"{fundamental_assessment.directional_bias.value} bias, "
            f"p={fundamental_assessment.probability_estimate:.2f}, "
            f"evidence: {'; '.join(fundamental_assessment.evidence) or 'none'}"
        )
    evidence_block = "\n".join(evidence_lines) or "No upstream agent evidence available."

    user_prompt = (
        f"Underlying: {symbol}\nCurrent price: {opportunity.underlying_price}\n"
        f"Horizon: {HORIZON}\n\nUpstream evidence:\n{evidence_block}\n\n"
        f"Produce probabilities for outcomes {OUTCOMES}, an expected_move (signed, "
        "as a fraction e.g. 0.03 for +3%), your confidence, and the evidence list "
        "you actually used."
    )

    forecast = structured_completion(
        agent_name=NAME,
        system_prompt=SYSTEM_PROMPT,
        user_prompt=user_prompt,
        schema=ProbabilityForecast,
    )
    if forecast is None:
        forecast = _fallback_forecast(symbol)
    else:
        forecast.ticker = symbol
        forecast.horizon = HORIZON

    upside_probability = probability_of_upside(forecast)
    direction = (
        Direction.BULLISH
        if upside_probability > 0.55
        else Direction.BEARISH
        if upside_probability < 0.45
        else Direction.NEUTRAL
    )
    prediction = Prediction(
        agent_name=NAME,
        opportunity_id=opportunity.id,
        underlying_symbol=symbol,
        direction=direction,
        probability=upside_probability,
        confidence=forecast.confidence,
        rationale="; ".join(forecast.evidence) or "Neutral prior; insufficient evidence.",
        created_at=datetime.now(timezone.utc),
    )

    log_agent_decision(
        trace_id=state.get("trace_id", "unknown"),
        agent=NAME,
        input_summary={"symbol": symbol, "evidence": evidence_block},
        output_summary=forecast.model_dump(mode="json"),
        confidence=forecast.confidence,
        decision=direction.value,
        reason=f"P(up)={upside_probability:.2f}",
    )
    return {"probability_forecast": forecast, "predictions": [prediction]}
