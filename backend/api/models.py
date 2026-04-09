from pydantic import BaseModel, Field
from typing import Optional


class ResearchRequest(BaseModel):
    query: str = Field(..., min_length=3, max_length=500)
    ticker: str = Field(..., min_length=1, max_length=10)


class HITLApproveRequest(BaseModel):
    ticker: str
    session_id: str
    feedback: Optional[str] = None


class HITLRejectRequest(BaseModel):
    ticker: str
    session_id: str
    feedback: Optional[str] = None


class ResearchSessionResponse(BaseModel):
    session_id: str
    ticker: str
    query: str
    news_status: str
    sec_status: str
    sentiment_status: str
    sentiment_score: Optional[float]
    human_approved: Optional[bool]
    final_report: Optional[str]
    error: Optional[str]
    iteration_count: int

    class Config:
        from_attributes = True


class AgentEvent(BaseModel):
    event: str
    node: Optional[str]
    data: Optional[str]
    session_id: str
