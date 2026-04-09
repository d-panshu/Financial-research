import logging
import os
from datetime import datetime
from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib import colors

from backend.graph.state import ResearchState
from backend.config import settings

logger = logging.getLogger(__name__)

SYNTHESIS_PROMPT = PromptTemplate.from_template(
    "You are a senior portfolio analyst writing a professional investment research report.\n\n"
    "Research Context:\n{context}\n\n"
    "Human Reviewer Feedback: {feedback}\n\n"
    "Write a structured investment research report with these sections:\n"
    "1. Executive Summary\n"
    "2. Market Sentiment Analysis\n"
    "3. Key Financial Findings from SEC Filing\n"
    "4. Risk Factors\n"
    "5. Investment Recommendation (Buy / Hold / Sell with rationale)\n\n"
    "Be precise, cite specific figures, and maintain a professional tone."
)


def _generate_pdf(ticker: str, report_text: str, session_id: str) -> str:
    os.makedirs("./data/reports", exist_ok=True)
    path = f"./data/reports/{ticker}_{session_id}.pdf"

    doc = SimpleDocTemplate(path, pagesize=A4, topMargin=inch, bottomMargin=inch)
    styles = getSampleStyleSheet()
    heading_style = ParagraphStyle("Heading", parent=styles["Heading1"], textColor=colors.HexColor("#1a365d"))
    body_style = styles["BodyText"]
    body_style.leading = 16

    story = [
        Paragraph(f"Investment Research Report: {ticker}", heading_style),
        Paragraph(f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}", styles["Normal"]),
        HRFlowable(width="100%", thickness=1, color=colors.grey),
        Spacer(1, 0.2 * inch),
    ]

    for line in report_text.split("\n"):
        stripped = line.strip()
        if not stripped:
            story.append(Spacer(1, 0.1 * inch))
        elif stripped.startswith(("1.", "2.", "3.", "4.", "5.")):
            story.append(Paragraph(stripped, heading_style))
        else:
            story.append(Paragraph(stripped, body_style))

    doc.build(story)
    return path


def portfolio_synthesizer_node(state: ResearchState) -> dict:
    ticker = state["ticker"]
    logger.info("Synthesizing final report for ticker: %s", ticker)

    try:
        llm = OllamaLLM(model=settings.LLM_MODEL)

        report_text = llm.invoke(SYNTHESIS_PROMPT.format(
            context=state.get("aggregated_context", ""),
            feedback=state.get("human_feedback") or "None provided.",
        ))

        session_id = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        pdf_path = _generate_pdf(ticker, report_text, session_id)

        logger.info("Report generated at: %s", pdf_path)
        return {"final_report": report_text, "pdf_path": pdf_path}

    except Exception as e:
        logger.error("Synthesis failed for %s: %s", ticker, str(e))
        return {"error": f"Portfolio synthesizer: {str(e)}"}
