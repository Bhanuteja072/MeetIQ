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
            temperature=0.1,   # Low temp for factual extraction
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


ACTION_PROMPT = """You are an expert at extracting action items from meeting transcripts.
Find every task, to-do, or commitment made in this meeting.

TRANSCRIPT:
{transcript}

SPEAKERS IN THIS MEETING:
{speakers}

Rules:
- Only extract action items that were explicitly mentioned
- If an owner is mentioned or implied, include their name
- If a deadline is mentioned, include it exactly as said
- If no action items exist, return an empty list

Respond with ONLY a valid JSON object (no markdown, no extra text):
{{
    "action_items": [
        {{
            "task": "clear description of what needs to be done",
            "owner": "person responsible or null if unknown",
            "deadline": "deadline mentioned or null",
            "priority": "high/medium/low based on urgency in conversation"
        }}
    ]
}}"""


def action_item_agent(state: MeetingAnalysisState) -> MeetingAnalysisState:
    """
    Extracts all action items, owners, and deadlines from the transcript.
    """
    logger.info("Action item agent running")

    try:
        speaker_names = [
            s.get("speaker_id") or s.get("name") or "Unknown"
            for s in state.get("speakers", [])
        ]
        speakers_str = ", ".join(speaker_names) if speaker_names else "Unknown"

        llm = get_llm()
        prompt = ChatPromptTemplate.from_template(ACTION_PROMPT)
        chain = prompt | llm

        response = chain.invoke({
            "transcript": state["transcript_text"],
            "speakers": speakers_str
        })
        raw = response.content.strip()
        parsed = _parse_json(raw)

        return {
            **state,
            "action_items": parsed.get("action_items", []),
        }

    except Exception as e:
        print(f"❌ Action item agent error: {e}")
        return {
            **state,
            "action_items": [],
            "errors": state.get("errors", []) + [f"action_item_agent: {str(e)}"],
        }