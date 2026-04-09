import logging
import asyncio
from datetime import datetime
from typing import Any, Dict, List

from langgraph.graph import END, StateGraph


from backend.services.graph.state import MeetingAnalysisState
from backend.services.agents.summary_agent import summary_agent
from backend.services.agents.action_item_agent import action_item_agent
from backend.services.agents.decision_agent import decision_agent
from backend.services.agents.blocker_agent import blocker_agent

logger = logging.getLogger(__name__)


def build_transcript_text(transcript: List[Dict], speakers: List[Dict]) -> str:
    """
    Convert raw transcript segments into readable text for LLM consumption.
    
    Format:
    [00:00:09] Speaker 1 (Mayor Terrien): Thank you. The meeting agenda...
    [00:00:42] Speaker 2: The Armistrand School of Knowledge...
    """
    # Build speaker name lookup
    speaker_lookup = {}
    for s in speakers:
        sid = s.get("speaker_id") or s.get("id") or ""
        name = s.get("name") or sid or "Unknown"
        speaker_lookup[sid] = name

    lines = []
    for seg in transcript:
        start = seg.get("start", 0)
        hours = int(start // 3600)
        minutes = int((start % 3600) // 60)
        seconds = int(start % 60)
        timestamp = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

        speaker_id = seg.get("speaker_id", "unknown")
        speaker_name = speaker_lookup.get(speaker_id, speaker_id)
        text = str(seg.get("text") or "").strip()

        lines.append(f"[{timestamp}] {speaker_name}: {text}")

    return "\n".join(lines)


def report_builder(state: MeetingAnalysisState) -> MeetingAnalysisState:
    """
    Final node — merges all agent outputs into one structured report dict.
    This gets saved to MongoDB by the router.
    """
    logger.info("Building final report")

    def _as_str(value: Any) -> str:
        return value if isinstance(value, str) else ""

    def _as_list(value: Any) -> list:
        return value if isinstance(value, list) else []

    report = {
        "meeting_id": state["meeting_id"],
        "generated_at": datetime.utcnow(),
        "tldr": _as_str(state.get("tldr")),
        "summary": _as_str(state.get("summary")),
        "action_items": _as_list(state.get("action_items")),
        "decisions": _as_list(state.get("decisions")),
        "blockers": _as_list(state.get("blockers")),
        "topics_discussed": _as_list(state.get("topics_discussed")),
        "agent_errors": _as_list(state.get("errors")),
    }

    return {**state, "final_report": report}


def build_analysis_pipeline() -> StateGraph:
    """
    Builds the LangGraph pipeline.

    Graph structure:
    
    START
      ↓
    summary_agent ──────────────────────────────┐
    action_item_agent (runs in parallel) ───────┤
    decision_agent (runs in parallel) ──────────┤
    blocker_agent (runs in parallel) ───────────┘
                                                ↓
                                        report_builder
                                                ↓
                                              END

    Note: LangGraph runs nodes sequentially by default.
    For true parallelism you'd need async branches.
    We run them sequentially here — still fast with Groq (~2s per agent).
    """
    graph = StateGraph(MeetingAnalysisState)

    # Add all nodes
    graph.add_node("summary_agent", summary_agent)
    graph.add_node("action_item_agent", action_item_agent)
    graph.add_node("decision_agent", decision_agent)
    graph.add_node("blocker_agent", blocker_agent)
    graph.add_node("report_builder", report_builder)

    # Wire the edges — sequential flow
    graph.set_entry_point("summary_agent")
    graph.add_edge("summary_agent", "action_item_agent")
    graph.add_edge("action_item_agent", "decision_agent")
    graph.add_edge("decision_agent", "blocker_agent")
    graph.add_edge("blocker_agent", "report_builder")
    graph.add_edge("report_builder", END)

    return graph.compile()


async def run_analysis_pipeline(
    meeting_id: str,
    transcript: list,
    speakers: list,
) -> Dict[str, Any]:
    """
    Entry point called by the router.
    Builds initial state, runs the graph, returns the final report.
    """
    transcript_text = build_transcript_text(transcript, speakers)

    initial_state: MeetingAnalysisState = {
        "meeting_id": meeting_id,
        "transcript_text": transcript_text,
        "speakers": speakers,
        "summary": None,
        "tldr": None,
        "action_items": None,
        "decisions": None,
        "blockers": None,
        "topics_discussed": None,
        "final_report": None,
        "errors": [],
    }
    
    pipeline = build_analysis_pipeline()

    logger.info("Starting analysis pipeline for meeting %s", meeting_id)
    final_state = await asyncio.to_thread(pipeline.invoke, initial_state)
    logger.info("Analysis pipeline complete for meeting %s", meeting_id)

    return final_state["final_report"]