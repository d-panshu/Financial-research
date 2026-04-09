from datetime import datetime
from sqlalchemy import String, Float, Boolean, Text, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from backend.db.database import Base


class ResearchSession(Base):
    __tablename__ = "research_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    session_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    ticker: Mapped[str] = mapped_column(String(10), index=True)
    query: Mapped[str] = mapped_column(Text)

    # Agent outputs
    news_status: Mapped[str] = mapped_column(String(20), default="pending")
    sec_status: Mapped[str] = mapped_column(String(20), default="pending")
    sentiment_status: Mapped[str] = mapped_column(String(20), default="pending")
    sentiment_score: Mapped[float] = mapped_column(Float, nullable=True)
    aggregated_context: Mapped[str] = mapped_column(Text, nullable=True)

    # HITL
    human_approved: Mapped[bool] = mapped_column(Boolean, nullable=True)
    human_feedback: Mapped[str] = mapped_column(Text, nullable=True)

    # Output
    final_report: Mapped[str] = mapped_column(Text, nullable=True)
    pdf_path: Mapped[str] = mapped_column(String(256), nullable=True)
    error: Mapped[str] = mapped_column(Text, nullable=True)

    # Meta
    iteration_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
