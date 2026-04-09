import json
import logging
import uuid
from datetime import datetime

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session

from backend.api.models import ResearchRequest, ResearchSessionResponse
from backend.graph import build_graph, default_state
from backend.db.database import get_db
from backend.db.models import ResearchSession

router = APIRouter()
logger = logging.getLogger(__name__)

graph = build_graph()


@router.post("/research", response_model=ResearchSessionResponse)
def start_research(body: ResearchRequest, db: Session = Depends(get_db)):
    session_id = str(uuid.uuid4())
    session = ResearchSession(
        session_id=session_id,
        ticker=body.ticker.upper(),
        query=body.query,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


@router.websocket("/ws/research")
async def research_stream(ws: WebSocket):
    await ws.accept()
    try:
        data = await ws.receive_json()
        ticker = data["ticker"].upper()
        query = data.get("query", f"Analyse {ticker} stock")
        session_id = data.get("session_id", str(uuid.uuid4()))

        config = {"configurable": {"thread_id": f"{ticker}_{session_id}"}}
        initial_state = default_state(query=query, ticker=ticker)

        async for event in graph.astream_events(initial_state, config=config, version="v2"):
            event_name = event.get("event", "")
            node_name = event.get("name", "")
            payload = {
                "event": event_name,
                "node": node_name,
                "session_id": session_id,
                "data": str(event.get("data", ""))[:300],
            }
            await ws.send_json(payload)

            # Notify frontend that HITL pause is reached
            if node_name == "human_review" and event_name == "on_chain_start":
                await ws.send_json({
                    "event": "hitl_required",
                    "node": "human_review",
                    "session_id": session_id,
                    "data": json.dumps({"message": "Human approval required"}),
                })

    except WebSocketDisconnect:
        logger.info("WebSocket disconnected for session: %s", session_id)
    except Exception as e:
        logger.error("WebSocket error: %s", str(e))
        await ws.send_json({"event": "error", "data": str(e)})
