from __future__ import annotations

from uuid import uuid4

from loguru import logger

from app.agents import scout_agent
from app.orchestration.graph import build_graph
from app.orchestration.state import GraphState


class Scanner:
    def __init__(self):
        self.graph = build_graph()

    def scan(self, symbols: list[str]) -> list[GraphState]:
        opportunities = scout_agent.discover(symbols)
        results: list[GraphState] = []
        for opportunity in opportunities:
            initial_state: GraphState = {
                "trace_id": str(uuid4()),
                "opportunity": opportunity,
                "predictions": [],
            }
            try:
                final_state = self.graph.invoke(initial_state)
            except Exception:  # noqa: BLE001 - one symbol's failure (e.g. an
                # execution error on an already-expired contract) must not
                # discard every other symbol's already-completed work in the
                # same batch -- this runs unattended in the autonomous
                # scheduler, where losing a whole cycle over one bad symbol
                # would be far worse than losing just that symbol.
                logger.exception(
                    "Scanner.scan: pipeline failed for {}", opportunity.underlying_symbol
                )
                continue
            results.append(final_state)
        return results
