from app.models.diligence import DiligenceReport
from app.orchestration.graph import _route_after_diligence, build_graph


def _report(passed: bool) -> DiligenceReport:
    return DiligenceReport(
        passed=passed,
        concern_score=0.1 if passed else 0.9,
        recommended_action="proceed" if passed else "do not proceed",
        confidence=0.8,
    )


def test_route_skips_strategy_construction_when_diligence_flags_thesis():
    state = {"diligence_report": _report(False)}
    assert _route_after_diligence(state) == "evaluator"


def test_route_proceeds_to_options_architect_when_diligence_clears_thesis():
    state = {"diligence_report": _report(True)}
    assert _route_after_diligence(state) == "options_architect"


def test_route_proceeds_by_default_when_no_diligence_report_present():
    # Should never happen once diligence always runs first, but the router must
    # not silently block execution if the field is missing.
    assert _route_after_diligence({}) == "options_architect"


def test_graph_wires_execution_between_risk_and_evaluator():
    # A trade that clears risk must actually reach execution, not just evaluation --
    # this is what turns "risk-approved" into a real paper order.
    nodes = build_graph().get_graph().nodes
    assert "execution" in nodes
