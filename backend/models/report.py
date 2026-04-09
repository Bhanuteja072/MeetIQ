from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class ActionItem(BaseModel):
    task: str
    owner: Optional[str] = None       # Speaker name if mentioned
    deadline: Optional[str] = None    # e.g. "by Friday", "next week"
    priority: Optional[str] = None    # "high", "medium", "low"


class Decision(BaseModel):
    decision: str
    made_by: Optional[str] = None     # Speaker who drove the decision
    context: Optional[str] = None     # Why this decision was made


class Blocker(BaseModel):
    issue: str
    raised_by: Optional[str] = None
    severity: Optional[str] = None    # "critical", "moderate", "low"


class MeetingReport(BaseModel):
    meeting_id: str
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    tldr: str                          # 2-3 sentence overview
    summary: str                       # Full narrative summary
    action_items: List[ActionItem] = Field(default_factory=list)
    decisions: List[Decision] = Field(default_factory=list)
    blockers: List[Blocker] = Field(default_factory=list)
    topics_discussed: List[str] = Field(default_factory=list)        # High level topics