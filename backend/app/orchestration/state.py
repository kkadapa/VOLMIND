from __future__ import annotations

from typing import Annotated, TypedDict

from app.models.diligence import DiligenceReport
from app.models.opportunity import Opportunity
from app.models.prediction import FundamentalAssessment, NewsAssessment, Prediction, ProbabilityForecast
from app.models.trade import Trade


def _append(existing: list, new: list) -> list:
    return existing + new


class GraphState(TypedDict, total=False):
    trace_id: str
    opportunity: Opportunity

    news_context: str
    news_assessment: NewsAssessment | None
    fundamental_context: str
    fundamental_assessment: FundamentalAssessment | None

    predictions: Annotated[list[Prediction], _append]
    probability_forecast: ProbabilityForecast | None

    market_implied_probability: float
    divergence_score: float

    diligence_notes: str
    diligence_report: DiligenceReport | None

    proposed_trade: Trade | None
    risk_approved: bool
    risk_notes: str
    executed_trade: Trade | None
    evaluation_notes: str
