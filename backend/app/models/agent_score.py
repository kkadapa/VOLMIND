from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class AgentScore(BaseModel):
    agent_name: str
    trade_count: int = 0
    correct_count: int = 0
    brier_score: float = 0.0
    reputation_weight: float = 1.0
    updated_at: datetime
