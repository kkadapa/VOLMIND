#!/usr/bin/env python
"""Read-only performance report: realized P&L and agent reputation as they stand.

Recording of outcomes now happens live in app.services.position_monitor.PositionMonitor
every time a trade actually closes, so this script no longer writes anything -- it just
summarizes what's in data/trades and data/agent_scores.json.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from dotenv import load_dotenv

from app.memory.agent_reputation import PIPELINE_AGENTS, AgentReputation
from app.memory.trade_memory import TradeMemory
from app.models.trade import TradeStatus


def main() -> None:
    load_dotenv()
    trades = TradeMemory().load_all()
    closed_trades = [t for t in trades if t.status == TradeStatus.CLOSED and t.realized_pnl is not None]
    open_trades = [t for t in trades if t.status == TradeStatus.OPEN]

    if not closed_trades:
        print("No closed trades yet.")
    else:
        total_pnl = sum(t.realized_pnl for t in closed_trades)
        wins = sum(1 for t in closed_trades if t.realized_pnl > 0)
        print(f"Closed trades: {len(closed_trades)}  (open: {len(open_trades)})")
        print(f"Win rate: {wins}/{len(closed_trades)} ({wins / len(closed_trades):.0%})")
        print(f"Total realized P&L: ${total_pnl:,.2f}")
        print()
        for trade in closed_trades:
            print(
                f"  {trade.closed_at} {trade.underlying_symbol:6s} {trade.strategy_name:12s} "
                f"pnl=${trade.realized_pnl:,.2f}"
            )

    print("\nAgent reputation:")
    reputation = AgentReputation()
    for name in PIPELINE_AGENTS:
        score = reputation.get(name)
        print(f"  {name}: {score.correct_count}/{score.trade_count} correct, weight={score.reputation_weight:.2f}")


if __name__ == "__main__":
    main()
