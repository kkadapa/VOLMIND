from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from loguru import logger


def log_agent_decision(
    *,
    trace_id: str,
    agent: str,
    input_summary: Any,
    output_summary: Any,
    confidence: float | None,
    decision: str,
    reason: str,
) -> None:
    """Structured, traceable record of one agent's step in the pipeline.

    Every field the spec calls for (agent, timestamp, input, output, confidence,
    decision, reason) is emitted together, bound to the trace_id that follows a
    single opportunity from Scout through Execution. Never pass secrets in
    input_summary/output_summary -- these are logged verbatim.
    """
    logger.bind(trace_id=trace_id, agent=agent).info(
        "{agent} decision={decision} confidence={confidence} reason={reason}",
        agent=agent,
        decision=decision,
        confidence=confidence,
        reason=reason,
        timestamp=datetime.now(timezone.utc).isoformat(),
        input=input_summary,
        output=output_summary,
    )
