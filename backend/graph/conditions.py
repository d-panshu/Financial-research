from backend.graph.state import ResearchState
from backend.config import settings


def should_review(state: ResearchState) -> str:
    if state.get("error"):
        return "end"
    if state["iteration_count"] >= settings.MAX_ITERATIONS:
        return "synthesizer"
    return "human_review"


def route_after_human(state: ResearchState) -> str:
    if state["human_approved"] is True:
        return "approved"
    if state["human_approved"] is False:
        return "rejected"
    return "end"
