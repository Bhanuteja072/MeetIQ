from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class MeetingStatus(str, Enum):
    UPLOADED = "uploaded"
    TRANSCRIBING = "transcribing"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class Speaker(BaseModel):
    id: str                        # "speaker_1", "speaker_2"
    name: Optional[str] = None     # User can rename later
    total_speaking_time: float = 0 # In seconds

class TranscriptSegment(BaseModel):
    speaker_id: str
    text: str
    start_time: float
    end_time: float

class MeetingCreate(BaseModel):
    title: Optional[str] = None
    attendees: Optional[List[str]] = []

class MeetingResponse(BaseModel):
    id: str
    title: str
    status: MeetingStatus
    created_at: datetime
    duration: Optional[float] = None
    speakers: Optional[List[Speaker]] = []
    transcript: Optional[List[TranscriptSegment]] = []
    raw_transcript: Optional[str] = None
    file_name: Optional[str] = None
    file_type: Optional[str] = None