#!/usr/bin/env python
"""Run VOLMIND unattended for the duration of the competition.

Alternative to enabling VOLMIND_AUTONOMOUS_MODE inside the API process: a plain
long-running loop that scans the watchlist and monitors open positions on their
configured intervals, independent of whether `uvicorn` is running. Safe to leave
running for days -- every order it places still goes through the same fail-closed
paper-trading guard and risk checks as the API path.
"""
from __future__ import annotations

import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from dotenv import load_dotenv
from loguru import logger

load_dotenv()

from app.config import get_settings  # noqa: E402
from app.services.autonomous_runner import run_monitor_cycle, run_scan_cycle  # noqa: E402

HEARTBEAT_SECONDS = 60


def main() -> None:
    settings = get_settings()
    logger.info(
        "run_autonomous: starting -- scan every {}m, monitor every {}m, watchlist={}",
        settings.scan_interval_minutes,
        settings.monitor_interval_minutes,
        settings.watchlist,
    )

    last_scan = datetime.min.replace(tzinfo=timezone.utc)
    last_monitor = datetime.min.replace(tzinfo=timezone.utc)

    while True:
        now = datetime.now(timezone.utc)

        if (now - last_monitor).total_seconds() >= settings.monitor_interval_minutes * 60:
            run_monitor_cycle()
            last_monitor = now

        if (now - last_scan).total_seconds() >= settings.scan_interval_minutes * 60:
            run_scan_cycle()
            last_scan = now

        time.sleep(HEARTBEAT_SECONDS)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("run_autonomous: stopped")
