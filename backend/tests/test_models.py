import pytest
from pydantic import ValidationError

from app.models.prediction import Direction, FundamentalAssessment, NewsAssessment, ProbabilityForecast


def test_probability_forecast_normalizes_small_drift():
    forecast = ProbabilityForecast(
        ticker="AAPL",
        event="21d move",
        horizon="21d",
        probabilities={"+10%": 0.06, "+5%": 0.15, "flat": 0.6, "-5%": 0.14, "-10%": 0.06},
        expected_move=0.01,
        confidence=0.7,
        evidence=["strong earnings beat"],
    )
    assert sum(forecast.probabilities.values()) == pytest.approx(1.0)


def test_probability_forecast_rejects_fabricated_distribution():
    with pytest.raises(ValidationError):
        ProbabilityForecast(
            ticker="AAPL",
            event="21d move",
            horizon="21d",
            probabilities={"+10%": 0.9, "+5%": 0.9, "flat": 0.9, "-5%": 0.9, "-10%": 0.9},
            expected_move=0.01,
            confidence=0.7,
            evidence=["nonsense"],
        )


def test_probability_forecast_rejects_out_of_range_probability():
    with pytest.raises(ValidationError):
        ProbabilityForecast(
            ticker="AAPL",
            event="21d move",
            horizon="21d",
            probabilities={"+10%": 1.5, "flat": -0.5},
            expected_move=0.01,
            confidence=0.7,
            evidence=["nonsense"],
        )


def test_probability_forecast_clamps_confidence_without_evidence():
    forecast = ProbabilityForecast(
        ticker="AAPL",
        event="21d move",
        horizon="21d",
        probabilities={"+10%": 0.05, "+5%": 0.15, "flat": 0.6, "-5%": 0.15, "-10%": 0.05},
        expected_move=0.01,
        confidence=0.95,
        evidence=[],
    )
    assert forecast.confidence <= 0.3


def test_news_assessment_clamps_confidence_without_citations():
    assessment = NewsAssessment(
        underlying_symbol="AAPL",
        what_changed="rumor",
        why_it_matters="unclear",
        is_new_information=True,
        expected_direction=Direction.BULLISH,
        expected_magnitude=0.5,
        confidence=0.9,
        citations=[],
    )
    assert assessment.confidence <= 0.2


def test_fundamental_assessment_clamps_confidence_without_evidence():
    assessment = FundamentalAssessment(
        underlying_symbol="AAPL",
        directional_bias=Direction.BULLISH,
        probability_estimate=0.6,
        confidence=0.9,
        evidence=[],
        risks=[],
    )
    assert assessment.confidence <= 0.2
