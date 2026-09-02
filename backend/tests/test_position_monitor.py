from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import pytest

from app.config import Settings, TradingBlockedError
from app.memory.agent_reputation import AgentReputation
from app.memory.trade_memory import TradeMemory
from app.models.opportunity import OptionLeg, OptionType
from app.models.trade import Trade, TradeStatus
from app.services import position_monitor as position_monitor_module
from app.services.position_monitor import PositionMonitor

SETTINGS = Settings(
    alpaca_paper_trade=True,
    take_profit_pct=0.50,
    stop_loss_pct=0.50,
    min_days_to_expiry_exit=1,
)


def _open_trade(entry_cost: float = 2.0, days_to_expiry: int = 30) -> Trade:
    leg = OptionLeg(
        symbol="AAPL250101C00150000",
        option_type=OptionType.CALL,
        strike=150.0,
        expiry=datetime.now(timezone.utc) + timedelta(days=days_to_expiry),
        bid=entry_cost,
        ask=entry_cost,
    )
    return Trade(
        id="t1",
        opportunity_id="o1",
        underlying_symbol="AAPL",
        strategy_name="single_leg",
        legs=[leg],
        quantity=1,
        entry_cost=entry_cost,
        max_loss=entry_cost,
        status=TradeStatus.OPEN,
        opened_at=datetime.now(timezone.utc),
    )


def _monitor(tmp_path, quote_fn, close_fn=None):
    trade_memory = TradeMemory(data_dir=tmp_path / "trades")
    reputation = AgentReputation(path=tmp_path / "scores.json")
    return PositionMonitor(
        trade_memory=trade_memory,
        quote_fn=quote_fn,
        close_fn=close_fn or (lambda trade: None),
        reputation=reputation,
    ), trade_memory


def test_take_profit_closes_and_records_gain(tmp_path):
    trade = _open_trade(entry_cost=2.0)
    monitor, trade_memory = _monitor(tmp_path, quote_fn=lambda symbol: (3.5, 3.6))  # +75%
    trade_memory.save(trade)

    with patch.object(position_monitor_module, "get_settings", return_value=SETTINGS):
        closed = monitor.run_cycle()

    assert len(closed) == 1
    assert closed[0].status == TradeStatus.CLOSED
    assert closed[0].realized_pnl == pytest.approx((3.5 - 2.0) * 1 * 100)
    assert trade_memory.load(trade.id).status == TradeStatus.CLOSED


def test_stop_loss_closes_and_records_loss(tmp_path):
    trade = _open_trade(entry_cost=2.0)
    monitor, trade_memory = _monitor(tmp_path, quote_fn=lambda symbol: (0.8, 0.9))  # -60%
    trade_memory.save(trade)

    with patch.object(position_monitor_module, "get_settings", return_value=SETTINGS):
        closed = monitor.run_cycle()

    assert len(closed) == 1
    assert closed[0].realized_pnl < 0


def test_expiry_cutoff_closes_regardless_of_price(tmp_path):
    trade = _open_trade(entry_cost=2.0, days_to_expiry=0)
    monitor, trade_memory = _monitor(tmp_path, quote_fn=lambda symbol: (2.0, 2.0))  # flat
    trade_memory.save(trade)

    with patch.object(position_monitor_module, "get_settings", return_value=SETTINGS):
        closed = monitor.run_cycle()

    assert len(closed) == 1


def test_no_exit_condition_leaves_trade_open(tmp_path):
    trade = _open_trade(entry_cost=2.0)
    close_calls = []
    monitor, trade_memory = _monitor(
        tmp_path, quote_fn=lambda symbol: (2.1, 2.2), close_fn=lambda t: close_calls.append(t)
    )
    trade_memory.save(trade)

    with patch.object(position_monitor_module, "get_settings", return_value=SETTINGS):
        closed = monitor.run_cycle()

    assert closed == []
    assert close_calls == []
    assert trade_memory.load(trade.id).status == TradeStatus.OPEN


def test_close_is_fail_closed_without_paper_trading(tmp_path):
    trade = _open_trade(entry_cost=2.0)
    blocked_settings = Settings(alpaca_paper_trade=False, take_profit_pct=0.50, stop_loss_pct=0.50)
    monitor, trade_memory = _monitor(tmp_path, quote_fn=lambda symbol: (10.0, 10.0))
    trade_memory.save(trade)

    with patch.object(position_monitor_module, "get_settings", return_value=blocked_settings):
        with pytest.raises(TradingBlockedError):
            monitor.run_cycle()
