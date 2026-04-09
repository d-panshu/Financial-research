import os
import logging

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from backend.db.database import get_db
from backend.db.models import ResearchSession

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/report/{session_id}")
def download_report(session_id: str, db: Session = Depends(get_db)):
    session = db.query(ResearchSession).filter_by(session_id=session_id).first()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if not session.pdf_path or not os.path.exists(session.pdf_path):
        raise HTTPException(status_code=404, detail="Report PDF not yet generated")

    return FileResponse(
        path=session.pdf_path,
        media_type="application/pdf",
        filename=f"{session.ticker}_report_{session_id[:8]}.pdf",
    )


@router.get("/sessions")
def list_sessions(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    sessions = db.query(ResearchSession).order_by(ResearchSession.created_at.desc()).offset(skip).limit(limit).all()
    return sessions


@router.get("/sessions/{session_id}")
def get_session(session_id: str, db: Session = Depends(get_db)):
    session = db.query(ResearchSession).filter_by(session_id=session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session
