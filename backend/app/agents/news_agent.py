from __future__ import annotations

from loguru import logger
from pydantic import BaseModel, Field

from app.alpaca.news import get_recent_news
from app.llm import structured_completion
from app.models.prediction import Direction, NewsAssessment
from app.observability import log_agent_decision
from app.orchestration.state import GraphState

NAME = "news_agent"

SYSTEM_PROMPT = """You are a news analyst. Read the headlines and call the \
NewsSynthesis tool with your assessment: what changed, why it matters, whether \
it's genuinely new information, expected direction, expected magnitude, and your \
confidence. Base every claim only on the headlines given."""


class _NewsSynthesis(BaseModel):
    """LLM-facing subset of NewsAssessment.

    Citations are deliberately excluded here: we already have them verbatim from
    Alpaca, and asking a small model to also reproduce a nested list[Citation]
    object array made tool-calling far less reliable in practice (confirmed by
    direct testing -- the identical prompt succeeds consistently once the nested
    array requirement is removed). The real citations are attached in `run()`.
    """

    what_changed: str
    why_it_matters: str
    is_new_information: bool
    expected_direction: Direction
    expected_magnitude: float = Field(ge=0.0, le=1.0)
    confidence: float = Field(ge=0.0, le=1.0)


def run(state: GraphState) -> dict:
    opportunity = state["opportunity"]
    symbol = opportunity.underlying_symbol

    try:
        citations = get_recent_news(symbol)
    except Exception as exc:  # noqa: BLE001 - Alpaca outage must not crash the pipeline
        logger.warning("{}: failed to fetch news for {}: {}", NAME, symbol, exc)
        citations = []

    if not citations:
        context = f"No recent news retrieved for {symbol}."
        log_agent_decision(
            trace_id=state.get("trace_id", "unknown"),
            agent=NAME,
            input_summary={"symbol": symbol},
            output_summary={"citations": 0},
            confidence=0.0,
            decision="no_signal",
            reason="No news articles found in the lookback window.",
        )
        return {"news_context": context, "news_assessment": None}

    headline_block = "\n".join(
        f"- ({c.published_at}) {c.headline} [{c.source or 'unknown'}]" for c in citations
    )
    user_prompt = f"Underlying: {symbol}\n\nHeadlines:\n{headline_block}"

    synthesis = structured_completion(
        agent_name=NAME,
        system_prompt=SYSTEM_PROMPT,
        user_prompt=user_prompt,
        schema=_NewsSynthesis,
    )
    if synthesis is None:
        # LLM unavailable/failed: fall back to a neutral, evidence-only summary
        # rather than fabricating a directional view.
        assessment = NewsAssessment(
            underlying_symbol=symbol,
            what_changed="LLM analysis unavailable; raw headlines collected only.",
            why_it_matters="Unable to assess without LLM synthesis.",
            is_new_information=False,
            expected_direction=Direction.NEUTRAL,
            expected_magnitude=0.0,
            confidence=0.0,
            citations=citations,
        )
    else:
        assessment = NewsAssessment(
            underlying_symbol=symbol,
            citations=citations,
            **synthesis.model_dump(),
        )

    log_agent_decision(
        trace_id=state.get("trace_id", "unknown"),
        agent=NAME,
        input_summary={"symbol": symbol, "headline_count": len(citations)},
        output_summary=assessment.model_dump(mode="json"),
        confidence=assessment.confidence,
        decision=assessment.expected_direction.value,
        reason=assessment.why_it_matters,
    )
    return {"news_context": assessment.what_changed, "news_assessment": assessment}
