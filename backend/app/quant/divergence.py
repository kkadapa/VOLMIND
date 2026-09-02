from __future__ import annotations

from app.models.prediction import ProbabilityForecast


def compute_divergence(agent_probability: float, market_probability: float) -> float:
    return agent_probability - market_probability


def probability_of_upside(forecast: ProbabilityForecast) -> float:
    """Collapse a multi-outcome forecast into P(price above spot at horizon).

    Treats the "flat" bucket as a coin flip between finishing marginally above vs.
    below spot, so this is directly comparable to the market-implied P(price above
    spot) computed from option deltas.
    """
    p = forecast.probabilities
    up = p.get("+10%", 0.0) + p.get("+5%", 0.0)
    down = p.get("-10%", 0.0) + p.get("-5%", 0.0)
    flat = p.get("flat", 0.0)
    return up + 0.5 * flat if (up or down or flat) else 0.5
