from datetime import datetime, timezone
from unittest.mock import patch

import pytest

from app.config import Settings
from app.models.opportunity import OptionLeg, OptionType
from app.models.trade import Trade, TradeStatus
from app.quant import risk as risk_module
from app.quant.divergence import compute_divergence
from app.quant.risk import evaluate_trade_risk, kelly_fraction


def test_compute_divergence():
    assert compute_divergence(0.7, 0.5) == pytest.approx(0.2)


def test_kelly_fraction_bounds():
    assert kelly_fraction(0.6, 2.0) == pytest.approx(0.4)
    assert kelly_fraction(0.1, 1.0) == 0.0


def _trade(max_loss: float = 4.0, quantity: int = 1) -> Trade:
    leg = OptionLeg(
        symbol="AAPL250101C00150000",
        option_type=OptionType.CALL,
        strike=150.0,
        expiry=datetime.now(timezone.utc),
        bid=max_loss,
        ask=max_loss,
    )
    return Trade(
        id="t1",
        opportunity_id="o1",
        underlying_symbol="AAPL",
        strategy_name="single_leg",
        legs=[leg],
        quantity=quantity,
        entry_cost=max_loss,
        max_loss=max_loss,
        status=TradeStatus.PROPOSED,
    )


def test_risk_approves_within_all_limits():
    settings = Settings(max_position_risk=500.0, max_open_positions=3, max_daily_loss=1500.0)
    # $4/share * 1 contract * 100 shares/contract = $400 <= $500.
    with patch.object(risk_module, "get_settings", return_value=settings):
        approved, _ = evaluate_trade_risk(_trade(max_loss=4.0), open_position_count=0, realized_loss_today=0.0)
    assert approved


def test_risk_applies_contract_multiplier_to_max_loss():
    settings = Settings(max_position_risk=500.0)
    # $6/share * 1 contract * 100 = $600 > $500 -- would pass without the multiplier.
    with patch.object(risk_module, "get_settings", return_value=settings):
        approved, notes = evaluate_trade_risk(_trade(max_loss=6.0))
    assert not approved
    assert "Max loss" in notes


def test_risk_vetoes_when_max_open_positions_reached():
    settings = Settings(max_open_positions=2)
    with patch.object(risk_module, "get_settings", return_value=settings):
        approved, notes = evaluate_trade_risk(_trade(), open_position_count=2)
    assert not approved
    assert "already open" in notes


def test_risk_vetoes_when_daily_loss_limit_hit():
    settings = Settings(max_daily_loss=100.0)
    with patch.object(risk_module, "get_settings", return_value=settings):
        approved, notes = evaluate_trade_risk(_trade(), realized_loss_today=-150.0)
    assert not approved
    assert "daily limit" in notes
