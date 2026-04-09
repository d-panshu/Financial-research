from typing import TypedDict, Optional


class ResearchState(TypedDict):
    # Input
    query: str
    ticker: str

    # Agent 1 — News Fetcher
    news_articles: list[dict]
    news_status: str  # "pending" | "done" | "error"

    # Agent 2 — SEC Analyzer
    sec_chunks: list[str]
    sec_summary: str
    sec_status: str

    # Agent 3 — Sentiment Scorer
    sentiment_score: float  # -1.0 to +1.0
    sentiment_rationale: str
    sentiment_status: str

    # Aggregator
    aggregated_context: str

    # Human-in-the-Loop
    human_approved: Optional[bool]  # None = waiting
    human_feedback: Optional[str]

    # Agent 4 — Portfolio Synthesizer
    final_report: Optional[str]

    # System
    error: Optional[str]
    iteration_count: int


def default_state(query: str, ticker: str) -> ResearchState:
    return ResearchState(
        query=query,
        ticker=ticker,
        news_articles=[],
        news_status="pending",
        sec_chunks=[],
        sec_summary="",
        sec_status="pending",
        sentiment_score=0.0,
        sentiment_rationale="",
        sentiment_status="pending",
        aggregated_context="",
        human_approved=None,
        human_feedback=None,
        final_report=None,
        error=None,
        iteration_count=0,
    )
