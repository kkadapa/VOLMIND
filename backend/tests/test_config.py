import pytest

from app.config import Settings, TradingBlockedError


def test_paper_trading_guard_blocks_when_not_explicitly_true():
    settings = Settings(alpaca_paper_trade=False)
    with pytest.raises(TradingBlockedError):
        settings.require_paper_trading()


def test_paper_trading_guard_allows_when_explicitly_true():
    settings = Settings(alpaca_paper_trade=True)
    settings.require_paper_trading()  # must not raise


def test_settings_defaults_to_paper_trading_disabled():
    # Fail closed: the default Settings() (as if no env var were set at all) must
    # never permit execution.
    assert Settings().alpaca_paper_trade is False


def test_settings_defaults_autonomous_mode_disabled():
    # Fail closed like everything else: the agent never trades unattended unless
    # explicitly opted in.
    assert Settings().autonomous_mode is False


def test_settings_defaults_position_management():
    settings = Settings()
    assert settings.max_open_positions == 3
    assert settings.take_profit_pct == pytest.approx(0.50)
    assert settings.stop_loss_pct == pytest.approx(0.50)
    assert settings.min_days_to_expiry_exit == 1
    assert settings.watchlist == ["AAPL", "MSFT", "NVDA", "SPY"]
