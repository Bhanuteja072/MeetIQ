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


DECISION_PROMPT = """You are an expert at identifying decisions made in meetings.
Extract every concrete decision, resolution, or agreement from this transcript.

TRANSCRIPT:
{transcript}

Rules:
- Only extract decisions that were clearly made or agreed upon
- Include who drove the decision if mentioned
- Include the reasoning or context if discussed
- Votes, resolutions, and unanimous agreements all count as decisions
- If no decisions were made, return an empty list

Respond with ONLY a valid JSON object (no markdown, no extra text):
{{
    "decisions": [
        {{
            "decision": "what was decided",
            "made_by": "person or group who made it, or null",
            "context": "brief reason or context for the decision, or null"
        }}
    ]
}}"""


def decision_agent(state: MeetingAnalysisState) -> MeetingAnalysisState:
    """
    Extracts all decisions, resolutions, and agreements from the transcript.
    """
    print("🤖 Decision agent running...")

    try:
        llm = get_llm()
        prompt = ChatPromptTemplate.from_template(DECISION_PROMPT)
        chain = prompt | llm

        response = chain.invoke({"transcript": state["transcript_text"]})
        raw = response.content.strip()
        parsed = _parse_json(raw)

        return {
            **state,
            "decisions": parsed.get("decisions", []),
        }

    except Exception as e:
        print(f"❌ Decision agent error: {e}")
        return {
            **state,
            "decisions": [],
            "errors": state.get("errors", []) + [f"decision_agent: {str(e)}"],
        }