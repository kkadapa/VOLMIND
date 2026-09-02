from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from app.models.agent_score import AgentScore

DATA_DIR = Path(__file__).resolve().parents[3] / "data"
SCORES_PATH = DATA_DIR / "agent_scores.json"

# The belief-forming/gating agents whose track record we score against realized trade
# outcomes. Every executed trade passed through all five, so a trade's P&L is
# attributed to each of them equally.
PIPELINE_AGENTS = [
    "news_agent",
    "fundamental_agent",
    "probability_agent",
    "diligence_agent",
    "risk_agent",
]


class AgentReputation:
    def __init__(self, path: Path = SCORES_PATH):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def _load_all(self) -> dict[str, AgentScore]:
        if not self.path.exists():
            return {}
        raw = self.path.read_text()
        if not raw.strip():
            return {}
        scores = [AgentScore.model_validate(item) for item in json.loads(raw)]
        return {score.agent_name: score for score in scores}

    def _save_all(self, scores: dict[str, AgentScore]) -> None:
        payload = [json.loads(score.model_dump_json()) for score in scores.values()]
        self.path.write_text(json.dumps(payload, indent=2))

    def get(self, agent_name: str) -> AgentScore:
        scores = self._load_all()
        return scores.get(
            agent_name,
            AgentScore(agent_name=agent_name, updated_at=datetime.now(timezone.utc)),
        )

    def record_outcome(self, agent_name: str, correct: bool, brier_score: float) -> AgentScore:
        scores = self._load_all()
        score = scores.get(
            agent_name,
            AgentScore(agent_name=agent_name, updated_at=datetime.now(timezone.utc)),
        )
        score.trade_count += 1
        score.correct_count += int(correct)
        score.brier_score = brier_score
        score.reputation_weight = score.correct_count / score.trade_count
        score.updated_at = datetime.now(timezone.utc)
        scores[agent_name] = score
        self._save_all(scores)
        return score
