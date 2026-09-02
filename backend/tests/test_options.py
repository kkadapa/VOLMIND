from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

from app.alpaca import options

_FUTURE = (datetime.now(timezone.utc) + timedelta(days=30)).strftime("%y%m%d")


def _snapshot(bid: float, ask: float, delta: float | None = 0.5):
    snapshot = MagicMock()
    snapshot.latest_quote = MagicMock(bid_price=bid, ask_price=ask)
    snapshot.implied_volatility = 0.3
    snapshot.greeks = MagicMock(delta=delta, gamma=0.01, theta=-0.02, vega=0.1)
    return snapshot


def test_skips_unparseable_contract_without_failing_whole_chain():
    # Regression test: a post-corporate-action "adjusted" contract (e.g. root
    # "BA1" after a split/spinoff) doesn't match the standard OCC symbol format.
    # One bad contract previously crashed get_option_chain entirely, which took
    # down a whole multi-symbol /scan request over one unrelated ticker's data.
    client = MagicMock()
    client.get_option_chain.return_value = {
        "BA1260918C00035000": _snapshot(1.0, 1.2),
        f"AAPL{_FUTURE}C00150000": _snapshot(2.0, 2.2),
    }
    with patch.object(options, "get_option_data_client", return_value=client):
        legs = options.get_option_chain("AAPL")

    assert len(legs) == 1
    assert legs[0].symbol == f"AAPL{_FUTURE}C00150000"


def test_skips_expired_and_0dte_contracts():
    # Regression test: Alpaca can reject a same-day (0DTE) or already-expired
    # contract as "expired" at order-submission time even though the chain
    # snapshot still returns a live quote for it -- this crashed a real paper
    # order mid-scan. Exclude anything expiring today or earlier at the source.
    today = datetime.now(timezone.utc)
    expired = (today - timedelta(days=1)).strftime("%y%m%d")
    zero_dte = today.strftime("%y%m%d")

    client = MagicMock()
    client.get_option_chain.return_value = {
        f"AAPL{expired}C00150000": _snapshot(1.0, 1.2),
        f"AAPL{zero_dte}C00150000": _snapshot(1.0, 1.2),
        f"AAPL{_FUTURE}C00150000": _snapshot(2.0, 2.2),
    }
    with patch.object(options, "get_option_data_client", return_value=client):
        legs = options.get_option_chain("AAPL")

    assert len(legs) == 1
    assert legs[0].symbol == f"AAPL{_FUTURE}C00150000"


def test_skips_contract_with_no_quote():
    client = MagicMock()
    no_quote = _snapshot(0, 0)
    no_quote.latest_quote = None
    client.get_option_chain.return_value = {f"AAPL{_FUTURE}C00150000": no_quote}
    with patch.object(options, "get_option_data_client", return_value=client):
        assert options.get_option_chain("AAPL") == []
