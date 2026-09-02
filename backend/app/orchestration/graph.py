from __future__ import annotations

from langgraph.graph import END, StateGraph

from app.agents.diligence_agent import run as diligence_run
from app.agents.divergence_agent import run as divergence_run
from app.agents.evaluator_agent import run as evaluator_run
from app.agents.execution_agent import run as execution_run
from app.agents.fundamental_agent import run as fundamental_run
from app.agents.market_probability_agent import run as market_probability_run
from app.agents.news_agent import run as news_run
from app.agents.options_architect_agent import run as options_architect_run
from app.agents.probability_agent import run as probability_run
from app.agents.risk_agent import run as risk_run
from app.orchestration.state import GraphState


def _route_after_diligence(state: GraphState) -> str:
    report = state.get("diligence_report")
    if report is not None and not report.passed:
        # The thesis didn't clear diligence review: never reaches Options Architect,
        # Risk, or execution. Only a reviewed, cleared thesis gets a strategy built.
        return "evaluator"
    return "options_architect"


def build_graph() -> StateGraph:
    graph = StateGraph(GraphState)

    graph.add_node("news", news_run)
    graph.add_node("fundamental", fundamental_run)
    graph.add_node("probability", probability_run)
    graph.add_node("market_probability", market_probability_run)
    graph.add_node("divergence", divergence_run)
    graph.add_node("diligence", diligence_run)
    graph.add_node("options_architect", options_architect_run)
    graph.add_node("risk", risk_run)
    graph.add_node("execution", execution_run)
    graph.add_node("evaluator", evaluator_run)

    graph.set_entry_point("news")
    graph.add_edge("news", "fundamental")
    graph.add_edge("fundamental", "probability")
    graph.add_edge("probability", "market_probability")
    graph.add_edge("market_probability", "divergence")
    graph.add_edge("divergence", "diligence")
    graph.add_conditional_edges(
        "diligence",
        _route_after_diligence,
        {"options_architect": "options_architect", "evaluator": "evaluator"},
    )
    graph.add_edge("options_architect", "risk")
    graph.add_edge("risk", "execution")
    graph.add_edge("execution", "evaluator")
    graph.add_edge("evaluator", END)

    return graph.compile()
