from typing import Any, Dict, List, Optional
from typing_extensions import TypedDict

# ── Typed sub-schemas ──────────────────────────────────────

class Speaker(TypedDict, total=False):
    id: str
    name: Optional[str]
    total_speaking_time: float


class ActionItem(TypedDict, total=False):
    task: str
    owner: Optional[str]
    deadline: Optional[str]
    priority: Optional[str]


class Decision(TypedDict, total=False):
    decision: str
    made_by: Optional[str]
    context: Optional[str]


class Blocker(TypedDict, total=False):
    issue: str
    raised_by: Optional[str]
    severity: Optional[str]


class FinalReport(TypedDict, total=False):
    meeting_id: str
    generated_at: str
    tldr: str
    summary: str
    action_items: List[ActionItem]
    decisions: List[Decision]
    blockers: List[Blocker]
    topics_discussed: List[str]
    agent_errors: List[str]





# ── Main state ─────────────────────────────────────────────

class MeetingAnalysisState(TypedDict):
    """
    Shared state passed between all nodes in the LangGraph pipeline.
    Each agent reads the transcript and writes its own output field.
    The report_builder node reads all output fields and merges them.
    """
    meeting_id: str
    transcript_text: str
    speakers: List[Speaker]

    summary: Optional[str]
    tldr: Optional[str]
    action_items: Optional[List[ActionItem]]
    decisions: Optional[List[Decision]]
    blockers: Optional[List[Blocker]]
    topics_discussed: Optional[List[str]]

    final_report: Optional[FinalReport]
    errors: List[str]