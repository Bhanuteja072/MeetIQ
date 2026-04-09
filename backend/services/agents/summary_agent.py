from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from backend.services.graph.state import MeetingAnalysisState
from config import settings
import json
import re
import logging
logger = logging.getLogger(__name__)


_LLM = None


def get_llm():
    global _LLM
    if _LLM is None:
        _LLM = ChatGroq(
            api_key=settings.groq_api_key,
            model="llama-3.3-70b-versatile",
            temperature=0.3,
        )
    return _LLM


def _parse_json(raw: str) -> dict:
    cleaned = re.sub(r"^```(?:json)?\s*", "", raw)
    cleaned = re.sub(r"\s*```$", "", cleaned)

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", cleaned, flags=re.S)
        if match:
            return json.loads(match.group(0))
        raise


SUMMARY_PROMPT = """You are an expert meeting analyst. 
Analyze this meeting transcript and produce a structured summary.

TRANSCRIPT:
{transcript}

Respond with ONLY a valid JSON object in this exact format (no markdown, no extra text):
{{
    "tldr": "2-3 sentence overview of the entire meeting",
    "summary": "Detailed narrative paragraph covering what was discussed, the flow of conversation, and key outcomes. Be specific and professional.",
    "topics_discussed": ["topic 1", "topic 2", "topic 3"]
}}"""


def summary_agent(state: MeetingAnalysisState) -> MeetingAnalysisState:
    """
    Reads the transcript and produces:
    - tldr: 2-3 sentence overview
    - summary: full narrative
    - topics_discussed: list of main topics
    """
    logger.info("Summary agent running")

    try:
        llm = get_llm()
        prompt = ChatPromptTemplate.from_template(SUMMARY_PROMPT)
        chain = prompt | llm

        response = chain.invoke({"transcript": state["transcript_text"]})
        raw = response.content.strip()

        parsed = _parse_json(raw)

        return {
            **state,
            "tldr": parsed.get("tldr", ""),
            "summary": parsed.get("summary", ""),
            "topics_discussed": parsed.get("topics_discussed", []),
        }

    except Exception as e:
        print(f"❌ Summary agent error: {e}")
        return {
            **state,
            "tldr": "",
            "summary": "",
            "topics_discussed": [],
            "errors": state.get("errors", []) + [f"summary_agent: {str(e)}"],
        }