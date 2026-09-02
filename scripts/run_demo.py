#!/usr/bin/env python
from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from dotenv import load_dotenv

from app.models.opportunity import Opportunity
from app.orchestration.graph import build_graph


def main() -> None:
    load_dotenv()
    opportunity = Opportunity(
        id=str(uuid4()),
        underlying_symbol="DEMO",
        underlying_price=100.0,
        discovered_at=datetime.now(timezone.utc),
        legs=[],
        source="run_demo",
        notes="Synthetic opportunity for end-to-end pipeline demo.",
    )

    graph = build_graph()
    final_state = graph.invoke({"opportunity": opportunity, "predictions": []})

    for key, value in final_state.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
