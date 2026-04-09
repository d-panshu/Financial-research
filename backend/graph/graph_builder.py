import logging
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver

from backend.graph.state import ResearchState
from backend.graph.conditions import should_review, route_after_human
from backend.agents.news_fetcher import news_fetcher_node
from backend.agents.sec_analyzer import sec_analyzer_node
from backend.agents.sentiment_scorer import sentiment_scorer_node
from backend.agents.portfolio_synthesizer import portfolio_synthesizer_node
from backend.config import settings

logger = logging.getLogger(__name__)


def aggregator_node(state: ResearchState) -> dict:
    news_text = "\n".join(
        f"- {a['title']}: {a['snippet']}" for a in state.get("news_articles", [])
    )
    context = (
        f"TICKER: {state['ticker']}\n\n"
        f"NEWS SUMMARY:\n{news_text}\n\n"
        f"SEC FILING SUMMARY:\n{state.get('sec_summary', 'N/A')}\n\n"
        f"SENTIMENT SCORE: {state.get('sentiment_score', 0.0)}\n"
        f"SENTIMENT RATIONALE: {state.get('sentiment_rationale', 'N/A')}"
    )
    return {
        "aggregated_context": context,
        "iteration_count": state.get("iteration_count", 0) + 1,
    }


def human_review_node(state: ResearchState) -> dict:
    # Graph pauses here via interrupt_before — this node only runs after resume
    logger.info("Human review node reached for ticker: %s", state["ticker"])
    return {}


def build_graph():
    builder = StateGraph(ResearchState)

    builder.add_node("news_fetcher", news_fetcher_node)
    builder.add_node("sec_analyzer", sec_analyzer_node)
    builder.add_node("sentiment_scorer", sentiment_scorer_node)
    builder.add_node("aggregator", aggregator_node)
    builder.add_node("human_review", human_review_node)
    builder.add_node("portfolio_synthesizer", portfolio_synthesizer_node)

    builder.set_entry_point("news_fetcher")
    builder.add_edge("news_fetcher", "sec_analyzer")
    builder.add_edge("sec_analyzer", "sentiment_scorer")
    builder.add_edge("sentiment_scorer", "aggregator")

    builder.add_conditional_edges(
        "aggregator",
        should_review,
        {
            "human_review": "human_review",
            "synthesizer": "portfolio_synthesizer",
            "end": END,
        },
    )

    builder.add_conditional_edges(
        "human_review",
        route_after_human,
        {
            "approved": "portfolio_synthesizer",
            "rejected": "news_fetcher",
            "end": END,
        },
    )

    builder.add_edge("portfolio_synthesizer", END)

    memory = SqliteSaver.from_conn_string(settings.CHECKPOINT_DB)
    return builder.compile(
        checkpointer=memory,
        interrupt_before=["human_review"],
    )
