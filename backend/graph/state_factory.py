from graph.state import ResearchState


def create_initial_state(query: str, ticker: str) -> ResearchState:
    return {
        "query": query,
        "ticker": ticker,

        "news_articles": [],
        "news_status": "pending",

        "sec_chunks": [],
        "sec_summary": "",
        "sec_status": "pending",

        "sentiment_score": 0.0,
        "sentiment_rationale": "",
        "sentiment_status": "pending",

        "aggregated_context": "",

        "human_approved": None,
        "human_feedback": None,

        "final_report": None,

        "error": None,
        "iteration_count": 0,
    }