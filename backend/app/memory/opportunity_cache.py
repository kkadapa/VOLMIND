from __future__ import annotations

import json
from pathlib import Path
from typing import Any

DATA_DIR = Path(__file__).resolve().parents[3] / "data" / "predictions"


class OpportunityCache:
    """Persists the most recent serialized scan result per ticker.

    Backs the Market Radar / Opportunity Detail read endpoints so they don't
    need to re-run the (LLM-calling, several-second) pipeline on every page
    load -- a scan writes here, the API reads from here.
    """

    def __init__(self, data_dir: Path = DATA_DIR):
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def save(self, ticker: str, serialized: dict[str, Any]) -> None:
        path = self.data_dir / f"{ticker.upper()}.json"
        path.write_text(json.dumps(serialized, indent=2))

    def get(self, ticker: str) -> dict[str, Any] | None:
        path = self.data_dir / f"{ticker.upper()}.json"
        if not path.exists():
            return None
        return json.loads(path.read_text())

    def list_all(self) -> list[dict[str, Any]]:
        results = []
        for path in sorted(self.data_dir.glob("*.json")):
            results.append(json.loads(path.read_text()))
        return results
