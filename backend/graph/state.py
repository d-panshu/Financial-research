from typing import TypedDict, Optional, List


class ResearchState(TypedDict):
 
    query: str
    ticker: str

    news_articles: List[dict]
    news_status: str  # "pending" | "done" | "error"

    sec_chunks: List[str]
    sec_summary: str
    sec_status: str


    sentiment_score: float 
    sentiment_rationale: str
    sentiment_status: str

    aggregated_context: str

    human_approved: Optional[bool]
    human_feedback: Optional[str]


    final_report: Optional[str]

    error: Optional[str]
    iteration_count: int