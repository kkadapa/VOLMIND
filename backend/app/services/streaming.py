from __future__ import annotations

import json
from collections.abc import Iterator
from uuid import uuid4

from loguru import logger

from app.agents import scout_agent
from app.memory.opportunity_cache import OpportunityCache
from app.orchestration.graph import build_graph
from app.services.serialization import serialize_state

# Display labels for each graph node, in the order the frontend should render
# them as pipeline steps. Nodes not reached for a given run (e.g. Options
# Architect/Risk when diligence review flags the thesis) simply never get a
# "done" event, so the client marks them skipped once evaluator fires.
NODE_LABELS: dict[str, str] = {
    "news": "News Agent",
    "fundamental": "Fundamental Agent",
    "probability": "Probability Agent",
    "market_probability": "Market-Implied Probability",
    "divergence": "Divergence Engine",
    "diligence": "Diligence Agent",
    "options_architect": "Options Architect",
    "risk": "Risk Agent",
    "execution": "Execution",
    "evaluator": "Evaluator",
}


def _sse(event: dict) -> str:
    return f"data: {json.dumps(event)}\n\n"


def stream_scan(symbols: list[str]) -> Iterator[str]:
    """Server-sent-events generator: one event per pipeline stage as it actually
    completes, for each symbol in turn, so the UI can show genuine live progress
    instead of a generic spinner.
    """
    graph = build_graph()
    cache = OpportunityCache()

    for symbol in symbols:
        symbol = symbol.strip().upper()
        if not symbol:
            continue

        yield _sse({"type": "symbol_start", "ticker": symbol})

        try:
            opportunities = scout_agent.discover([symbol])
        except Exception as exc:  # noqa: BLE001 - a bad symbol must not kill the stream
            logger.warning("stream_scan: discovery failed for {}: {}", symbol, exc)
            yield _sse({"type": "symbol_error", "ticker": symbol, "message": str(exc)})
            continue

        if not opportunities:
            yield _sse(
                {
                    "type": "symbol_error",
                    "ticker": symbol,
                    "message": f"No market/option data available for {symbol}.",
                }
            )
            continue

        opportunity = opportunities[0]
        trace_id = str(uuid4())
        accumulated: dict = {"trace_id": trace_id, "opportunity": opportunity, "predictions": []}

        try:
            for chunk in graph.stream(dict(accumulated)):
                for node_name, update in chunk.items():
                    for key, value in update.items():
                        if key == "predictions":
                            accumulated["predictions"] = accumulated.get("predictions", []) + value
                        else:
                            accumulated[key] = value
                    yield _sse(
                        {
                            "type": "agent_done",
                            "ticker": symbol,
                            "node": node_name,
                            "label": NODE_LABELS.get(node_name, node_name),
                        }
                    )
        except Exception as exc:  # noqa: BLE001 - one symbol's failure must not kill the stream
            logger.exception("stream_scan: pipeline failed for {}", symbol)
            yield _sse({"type": "symbol_error", "ticker": symbol, "message": str(exc)})
            continue

        payload = serialize_state(accumulated)
        cache.save(symbol, payload)
        yield _sse({"type": "opportunity_complete", "ticker": symbol, "data": payload})

    yield _sse({"type": "scan_complete"})
