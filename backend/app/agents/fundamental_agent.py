from __future__ import annotations

from app.llm import structured_completion
from app.models.prediction import Direction, FundamentalAssessment
from app.observability import log_agent_decision
from app.orchestration.state import GraphState

NAME = "fundamental_agent"

SYSTEM_PROMPT = """You are a fundamental equity analyst. Analyze the company using \
the news context given and your general knowledge, then call the \
FundamentalAssessment tool with your assessment. Label any evidence that comes \
from general knowledge rather than the supplied news. Don't invent exact figures \
(EPS, revenue) you weren't given."""


def run(state: GraphState) -> dict:
    opportunity = state["opportunity"]
    symbol = opportunity.underlying_symbol
    news_context = state.get("news_context", "No news context available.")

    user_prompt = (
        f"Underlying: {symbol}\nUnderlying price: {opportunity.underlying_price}\n"
        f"News context so far: {news_context}\n\n"
        "Assess the company's fundamental/company-specific and sector context "
        "(earnings, guidance, margins, valuation, catalysts) to the extent you can "
        "reason about it. State directional bias, a probability estimate that the "
        "stock moves in that direction over the near term, your confidence, the "
        "evidence you're relying on (label anything from general knowledge as such), "
        "and the key risks to this view."
    )

    assessment = structured_completion(
        agent_name=NAME,
        system_prompt=SYSTEM_PROMPT,
        user_prompt=user_prompt,
        schema=FundamentalAssessment,
    )
    if assessment is None:
        assessment = FundamentalAssessment(
            underlying_symbol=symbol,
            directional_bias=Direction.NEUTRAL,
            probability_estimate=0.5,
            confidence=0.0,
            evidence=[],
            risks=["LLM analysis unavailable for this run."],
        )
    else:
        assessment.underlying_symbol = symbol

    context = (
        f"{assessment.directional_bias.value} bias, "
        f"p={assessment.probability_estimate:.2f}, conf={assessment.confidence:.2f}"
    )
    log_agent_decision(
        trace_id=state.get("trace_id", "unknown"),
        agent=NAME,
        input_summary={"symbol": symbol, "news_context": news_context},
        output_summary=assessment.model_dump(mode="json"),
        confidence=assessment.confidence,
        decision=assessment.directional_bias.value,
        reason="; ".join(assessment.evidence) or "No evidence cited.",
    )
    return {"fundamental_context": context, "fundamental_assessment": assessment}
