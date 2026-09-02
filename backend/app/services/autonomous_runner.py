from __future__ import annotations

from loguru import logger

from app.alpaca.trading import get_clock
from app.config import get_settings
from app.memory.opportunity_cache import OpportunityCache
from app.services.position_monitor import PositionMonitor
from app.services.scanner import Scanner
from app.services.serialization import serialize_state


def _market_is_open() -> bool:
    try:
        return bool(get_clock().is_open)
    except Exception:
        logger.exception("autonomous_runner: failed to fetch Alpaca clock; skipping cycle")
        return False


def run_scan_cycle() -> int:
    """Scan the configured watchlist. Returns the number of opportunities scanned."""
    if not _market_is_open():
        logger.info("autonomous_runner: market closed, skipping scan cycle")
        return 0

    settings = get_settings()
    scanner = Scanner()
    cache = OpportunityCache()
    results = scanner.scan(settings.watchlist)
    for state in results:
        payload = serialize_state(state)
        cache.save(payload["ticker"], payload)
    logger.info("autonomous_runner: scan cycle completed for {} symbols", len(results))
    return len(results)


def run_monitor_cycle() -> int:
    """Mark open positions to market and close anything that hit an exit rule.

    Runs regardless of market-open state for options near/at expiry so a position
    isn't left open into a holiday close, but bails out early if the clock lookup
    itself fails.
    """
    try:
        get_clock()
    except Exception:
        logger.exception("autonomous_runner: failed to fetch Alpaca clock; skipping monitor cycle")
        return 0

    closed = PositionMonitor().run_cycle()
    logger.info("autonomous_runner: monitor cycle closed {} position(s)", len(closed))
    return len(closed)
