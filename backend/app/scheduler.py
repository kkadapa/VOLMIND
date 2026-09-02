from __future__ import annotations

from apscheduler.schedulers.background import BackgroundScheduler
from loguru import logger

from app.config import get_settings
from app.services.autonomous_runner import run_monitor_cycle, run_scan_cycle

_scheduler: BackgroundScheduler | None = None


def start_scheduler() -> BackgroundScheduler | None:
    """Starts background scan/monitor jobs if VOLMIND_AUTONOMOUS_MODE=true.

    No-op (returns None) otherwise -- autonomous trading is opt-in, mirroring the
    app's fail-closed default everywhere else (ALPACA_PAPER_TRADE, risk limits).
    """
    global _scheduler
    settings = get_settings()
    if not settings.autonomous_mode:
        logger.info("scheduler: VOLMIND_AUTONOMOUS_MODE is not 'true', autonomous loop disabled")
        return None

    scheduler = BackgroundScheduler()
    scheduler.add_job(
        run_scan_cycle,
        "interval",
        minutes=settings.scan_interval_minutes,
        id="scan_cycle",
    )
    scheduler.add_job(
        run_monitor_cycle,
        "interval",
        minutes=settings.monitor_interval_minutes,
        id="monitor_cycle",
    )
    scheduler.start()
    logger.info(
        "scheduler: autonomous mode enabled -- scan every {}m, monitor every {}m, watchlist={}",
        settings.scan_interval_minutes,
        settings.monitor_interval_minutes,
        settings.watchlist,
    )
    _scheduler = scheduler
    return scheduler


def stop_scheduler() -> None:
    global _scheduler
    if _scheduler is not None:
        _scheduler.shutdown(wait=False)
        _scheduler = None
