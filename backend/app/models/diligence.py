from __future__ import annotations

from pydantic import BaseModel, Field


class DiligenceReport(BaseModel):
    """Output of the Diligence Agent's independent pre-trade review.

    This agent's job is to stress-test the thesis before capital is put behind it --
    the same function a second analyst's sign-off serves on a real desk. `passed=False`
    halts the pipeline before the Options Architect ever runs -- no strategy is built,
    let alone risk-checked or executed, for a thesis that didn't clear review.
    """

    passed: bool
    concern_score: float = Field(ge=0.0, le=1.0, description="0=no concerns, 1=material concerns")
    concerns: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    missing_information: list[str] = Field(default_factory=list)
    recommended_action: str
    confidence: float = Field(ge=0.0, le=1.0)
