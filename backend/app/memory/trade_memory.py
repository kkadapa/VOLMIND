from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from app.models.trade import Trade, TradeStatus

DATA_DIR = Path(__file__).resolve().parents[3] / "data" / "trades"


class TradeMemory:
    def __init__(self, data_dir: Path = DATA_DIR):
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def save(self, trade: Trade) -> None:
        path = self.data_dir / f"{trade.id}.json"
        path.write_text(trade.model_dump_json(indent=2))

    def load(self, trade_id: str) -> Trade | None:
        path = self.data_dir / f"{trade_id}.json"
        if not path.exists():
            return None
        return Trade.model_validate_json(path.read_text())

    def load_all(self) -> list[Trade]:
        return [
            Trade.model_validate_json(path.read_text())
            for path in sorted(self.data_dir.glob("*.json"))
        ]

    def load_open(self) -> list[Trade]:
        return [trade for trade in self.load_all() if trade.status == TradeStatus.OPEN]

    def load_closed_today(self) -> list[Trade]:
        today = datetime.now(timezone.utc).date()
        return [
            trade
            for trade in self.load_all()
            if trade.status == TradeStatus.CLOSED
            and trade.closed_at is not None
            and trade.closed_at.astimezone(timezone.utc).date() == today
        ]
