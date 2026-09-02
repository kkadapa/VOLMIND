from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, field_validator, model_validator


class Direction(str, Enum):
    BULLISH = "bullish"
    BEARISH = "bearish"
    NEUTRAL = "neutral"


class Prediction(BaseModel):
    agent_name: str
    opportunity_id: str
    underlying_symbol: str
    direction: Direction
    probability: float
    confidence: float
    rationale: str
    created_at: datetime


class Citation(BaseModel):
    headline: str
    source: str | None = None
    url: str | None = None
    published_at: datetime | None = None


class NewsAssessment(BaseModel):
    """Output of the News Agent. Never independently approves a trade."""

    agent_name: str = "news_agent"
    underlying_symbol: str
    what_changed: str
    why_it_matters: str
    is_new_information: bool
    expected_direction: Direction
    expected_magnitude: float = Field(ge=0.0, le=1.0, description="0=negligible, 1=extreme")
    confidence: float = Field(ge=0.0, le=1.0)
    citations: list[Citation] = Field(default_factory=list)

    @model_validator(mode="after")
    def require_evidence_for_conviction(self) -> "NewsAssessment":
        # An agent claiming meaningful confidence with zero cited evidence is not
        # trustworthy input to the ensemble -- clamp it rather than propagate it.
        if not self.citations and self.confidence > 0.2:
            self.confidence = 0.2
        return self


class FundamentalAssessment(BaseModel):
    """Output of the Fundamental Agent. Never independently approves a trade."""

    agent_name: str = "fundamental_agent"
    underlying_symbol: str
    directional_bias: Direction
    probability_estimate: float = Field(ge=0.0, le=1.0)
    confidence: float = Field(ge=0.0, le=1.0)
    evidence: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def require_evidence_for_conviction(self) -> "FundamentalAssessment":
        if not self.evidence and self.confidence > 0.2:
            self.confidence = 0.2
        return self


class ProbabilityForecast(BaseModel):
    """Output of the Probability Agent -- the core ensemble forecast.

    `probabilities` maps outcome labels (e.g. "+10%", "+5%", "-5%", "-10%", "flat")
    to their estimated probability. Values must be in [0, 1] and sum to ~1; the
    normalization below absorbs small LLM rounding error but rejects outputs that
    aren't close to a valid distribution, since that signals the model invented
    numbers rather than reasoning about them.
    """

    ticker: str
    event: str
    horizon: str
    probabilities: dict[str, float]
    expected_move: float
    confidence: float = Field(ge=0.0, le=1.0)
    evidence: list[str] = Field(default_factory=list, min_length=0)
    model_version: str = "v1"

    @field_validator("probabilities")
    @classmethod
    def validate_probabilities(cls, value: dict[str, float]) -> dict[str, float]:
        if not value:
            raise ValueError("probabilities must not be empty")
        for outcome, p in value.items():
            if not (0.0 <= p <= 1.0):
                raise ValueError(f"probability for {outcome!r} out of [0,1]: {p}")
        total = sum(value.values())
        if not (0.85 <= total <= 1.15):
            raise ValueError(
                f"probabilities sum to {total:.3f}, expected ~1.0 -- looks fabricated, not reasoned"
            )
        # Normalize away small drift so downstream consumers can rely on sum == 1.
        return {k: v / total for k, v in value.items()}

    @model_validator(mode="after")
    def require_evidence_for_conviction(self) -> "ProbabilityForecast":
        if not self.evidence and self.confidence > 0.3:
            self.confidence = 0.3
        return self
