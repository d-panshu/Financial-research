import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes import research, hitl, report
from backend.db.database import init_db
from backend.config import settings

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    os.makedirs("./data/reports", exist_ok=True)
    os.makedirs("./data/chroma_db", exist_ok=True)
    init_db()
    logger.info("Database initialised")
    logger.info("Financial Research System ready")
    yield
    logger.info("Shutting down")


app = FastAPI(
    title="Financial Research System API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(research.router, tags=["Research"])
app.include_router(hitl.router, prefix="/api", tags=["HITL"])
app.include_router(report.router, prefix="/api", tags=["Reports"])


@app.get("/health")
def health():
    return {"status": "ok", "environment": settings.ENVIRONMENT}
