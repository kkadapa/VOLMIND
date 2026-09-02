from __future__ import annotations

from functools import lru_cache

from alpaca.data.historical.news import NewsClient
from alpaca.data.historical.option import OptionHistoricalDataClient
from alpaca.data.historical.stock import StockHistoricalDataClient
from alpaca.trading.client import TradingClient

from app.config import get_settings


@lru_cache(maxsize=1)
def get_trading_client() -> TradingClient:
    settings = get_settings()
    # alpaca-py's own `paper` flag governs which Alpaca endpoint is used. VOLMIND's
    # ALPACA_PAPER_TRADE guard (see app.config.Settings.require_paper_trading) is the
    # authoritative, fail-closed check applied before any order is ever submitted.
    return TradingClient(
        api_key=settings.alpaca_api_key,
        secret_key=settings.alpaca_secret_key,
        paper=True,
    )


@lru_cache(maxsize=1)
def get_stock_data_client() -> StockHistoricalDataClient:
    settings = get_settings()
    return StockHistoricalDataClient(
        api_key=settings.alpaca_api_key,
        secret_key=settings.alpaca_secret_key,
    )


@lru_cache(maxsize=1)
def get_option_data_client() -> OptionHistoricalDataClient:
    settings = get_settings()
    return OptionHistoricalDataClient(
        api_key=settings.alpaca_api_key,
        secret_key=settings.alpaca_secret_key,
    )


@lru_cache(maxsize=1)
def get_news_client() -> NewsClient:
    settings = get_settings()
    return NewsClient(
        api_key=settings.alpaca_api_key,
        secret_key=settings.alpaca_secret_key,
    )
