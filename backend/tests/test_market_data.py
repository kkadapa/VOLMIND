from unittest.mock import MagicMock, patch

from app.alpaca import market_data


def _quote(bid: float, ask: float):
    q = MagicMock()
    q.bid_price = bid
    q.ask_price = ask
    return q


def _trade(price: float):
    t = MagicMock()
    t.price = price
    return t


def test_uses_midpoint_when_both_sides_present():
    client = MagicMock()
    client.get_stock_latest_quote.return_value = {"AAPL": _quote(150.0, 151.0)}
    with patch.object(market_data, "get_stock_data_client", return_value=client):
        assert market_data.get_latest_quote("AAPL") == 150.5
    client.get_stock_latest_trade.assert_not_called()


def test_falls_back_to_trade_price_when_ask_is_zero():
    # Regression test: a one-sided quote (ask=0, as Alpaca returns outside active
    # trading) must not silently average to a garbage price -- it previously
    # produced $150 for a stock actually trading near $300.
    client = MagicMock()
    client.get_stock_latest_quote.return_value = {"AAPL": _quote(300.93, 0.0)}
    client.get_stock_latest_trade.return_value = {"AAPL": _trade(319.92)}
    with patch.object(market_data, "get_stock_data_client", return_value=client):
        assert market_data.get_latest_quote("AAPL") == 319.92


def test_returns_none_when_no_data_available():
    client = MagicMock()
    client.get_stock_latest_quote.return_value = {}
    client.get_stock_latest_trade.return_value = {}
    with patch.object(market_data, "get_stock_data_client", return_value=client):
        assert market_data.get_latest_quote("AAPL") is None
