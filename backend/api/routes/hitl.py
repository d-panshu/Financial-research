import logging
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.api.models import HITLApproveRequest, HITLRejectRequest
from backend.api.routes.research import graph
from backend.db.database import get_db
from backend.db.models import ResearchSession

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/approve")
async def approve_research(body: HITLApproveRequest, db: Session = Depends(get_db)):
    config = {"configurable": {"thread_id": f"{body.ticker.upper()}_{body.session_id}"}}

    try:
        graph.update_state(config, {
            "human_approved": True,
            "human_feedback": body.feedback,
        })

        async for _ in graph.astream(None, config=config):
            pass

        session = db.query(ResearchSession).filter_by(session_id=body.session_id).first()
        if session:
            session.human_approved = True
            session.human_feedback = body.feedback
            session.completed_at = datetime.utcnow()
            db.commit()

        logger.info("Research approved for session: %s", body.session_id)
        return {"status": "resumed", "session_id": body.session_id}

    except Exception as e:
        logger.error("Approve failed for session %s: %s", body.session_id, str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reject")
async def reject_research(body: HITLRejectRequest, db: Session = Depends(get_db)):
    config = {"configurable": {"thread_id": f"{body.ticker.upper()}_{body.session_id}"}}

    try:
        graph.update_state(config, {
            "human_approved": False,
            "human_feedback": body.feedback,
        })

        async for _ in graph.astream(None, config=config):
            pass

        session = db.query(ResearchSession).filter_by(session_id=body.session_id).first()
        if session:
            session.human_approved = False
            session.human_feedback = body.feedback
            db.commit()

        logger.info("Research rejected for session: %s", body.session_id)
        return {"status": "restarted", "session_id": body.session_id}

    except Exception as e:
        logger.error("Reject failed for session %s: %s", body.session_id, str(e))
        raise HTTPException(status_code=500, detail=str(e))
