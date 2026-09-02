from __future__ import annotations

from alpaca.data.requests import StockLatestQuoteRequest, StockLatestTradeRequest

from app.alpaca.client import get_stock_data_client


def get_latest_quote(symbol: str) -> float | None:
    """Best-effort current price for `symbol`.

    Prefers the bid/ask midpoint, but only when BOTH sides are present and
    positive -- a one-sided or stale NBBO (e.g. `ask_price=0.0`, which Alpaca
    returns outside active trading) silently averages to a garbage price
    instead of raising, which would poison every downstream strike-selection
    and probability calculation. Falls back to the latest trade price, which is
    always one-sided-quote-proof.
    """
    client = get_stock_data_client()

    quote = client.get_stock_latest_quote(StockLatestQuoteRequest(symbol_or_symbols=symbol)).get(
        symbol
    )
    if quote is not None and quote.bid_price and quote.ask_price:
        return (quote.bid_price + quote.ask_price) / 2

    trade = client.get_stock_latest_trade(StockLatestTradeRequest(symbol_or_symbols=symbol)).get(
        symbol
    )
    if trade is not None and trade.price:
        return trade.price

    return None
