from datetime import datetime, timezone
from unittest.mock import patch

from app.agents import scout_agent
from app.models.opportunity import Opportunity
from app.services.scanner import Scanner


def _opportunity(symbol: str) -> Opportunity:
    return Opportunity(
        id=symbol,
        underlying_symbol=symbol,
        underlying_price=100.0,
        discovered_at=datetime.now(timezone.utc),
        legs=[],
        source="test",
    )


def test_one_symbols_pipeline_failure_does_not_discard_the_rest():
    # Regression test: a real run hit an Alpaca "contract expired" error on one
    # symbol's execution step, which propagated out of Scanner.scan() entirely
    # and discarded every other symbol's already-completed pipeline work in the
    # same batch. This also runs unattended in the autonomous scheduler, where
    # losing a whole scan cycle over one bad symbol is worse than losing one.
    scanner = Scanner()
    opportunities = [_opportunity("BAD"), _opportunity("GOOD")]

    def fake_invoke(state):
        if state["opportunity"].underlying_symbol == "BAD":
            raise RuntimeError("contract expired")
        return state

    with (
        patch.object(scout_agent, "discover", return_value=opportunities),
        patch.object(scanner.graph, "invoke", side_effect=fake_invoke),
    ):
        results = scanner.scan(["BAD", "GOOD"])

    assert len(results) == 1
    assert results[0]["opportunity"].underlying_symbol == "GOOD"
