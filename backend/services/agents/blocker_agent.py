from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from backend.services.graph.state import MeetingAnalysisState
from config import settings
import json
import re


_LLM = None


def get_llm():
    global _LLM
    if _LLM is None:
        _LLM = ChatGroq(
            api_key=settings.groq_api_key,
            model="llama-3.3-70b-versatile",
            temperature=0.1,
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


BLOCKER_PROMPT = """You are an expert at identifying risks, blockers, and unresolved issues in meetings.

TRANSCRIPT:
{transcript}

Find every:
- Problem or blocker that prevents progress
- Unresolved question or open issue
- Risk or concern raised
- Thing that needs clarification before work can proceed

Rules:
- Only extract genuine blockers or concerns, not general discussion
- Assign severity: "critical" (blocks everything), "moderate" (slows progress), "low" (minor concern)
- If no blockers exist, return an empty list

Respond with ONLY a valid JSON object (no markdown, no extra text):
{{
    "blockers": [
        {{
            "issue": "description of the blocker or risk",
            "raised_by": "person who raised it or null",
            "severity": "critical/moderate/low"
        }}
    ]
}}"""


def blocker_agent(state: MeetingAnalysisState) -> MeetingAnalysisState:
    """
    Identifies blockers, risks, and unresolved issues from the transcript.
    """
    print("🤖 Blocker agent running...")

    try:
        llm = get_llm()
        prompt = ChatPromptTemplate.from_template(BLOCKER_PROMPT)
        chain = prompt | llm

        response = chain.invoke({"transcript": state["transcript_text"]})
        raw = response.content.strip()
        parsed = _parse_json(raw)

        return {
            **state,
            "blockers": parsed.get("blockers", []),
        }

    except Exception as e:
        print(f"❌ Blocker agent error: {e}")
        return {
            **state,
            "blockers": [],
            "errors": state.get("errors", []) + [f"blocker_agent: {str(e)}"],
        }