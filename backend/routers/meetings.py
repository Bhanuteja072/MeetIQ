from fastapi import APIRouter, HTTPException
from backend.databases.mongo import get_db
from backend.services.rag.embeddings import remove_meeting_from_index


router = APIRouter(prefix="/meetings", tags=["Meetings"])


def _get_db_or_raise():
    db = get_db()
    if db is None:
        raise HTTPException(status_code=500, detail="Database is not initialized")
    return db


@router.get("/")
async def get_all_meetings():
    """Get all meetings — for the archive page."""
    db = _get_db_or_raise()
    cursor = db.meetings.find({}, {
        "_id": 1, "title": 1, "status": 1,
        "created_at": 1, "duration": 1,
        "speakers": 1, "file_type": 1
    }).sort("created_at", -1)
    
    meetings = []
    async for meeting in cursor:
        meeting["id"] = str(meeting.pop("_id"))
        meetings.append(meeting)
    
    return {"meetings": meetings, "total": len(meetings)}


@router.get("/{meeting_id}")
async def get_meeting(meeting_id: str):
    """Get full meeting details including transcript."""
    db = _get_db_or_raise()
    meeting = await db.meetings.find_one({"_id": meeting_id})
    
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    meeting["id"] = str(meeting.pop("_id"))
    return meeting


@router.patch("/{meeting_id}/rename-speaker")
async def rename_speaker(meeting_id: str, speaker_id: str, new_name: str):
    """
    Let the user rename 'speaker_1' to 'Rahul' etc.
    Updates both speakers array and all transcript segments.
    """
    if not new_name.strip():
        raise HTTPException(status_code=400, detail="New name cannot be empty")

    db = _get_db_or_raise()
    meeting = await db.meetings.find_one({"_id": meeting_id})
    
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    # Update speaker name in speakers array
    speakers = meeting.get("speakers", [])
    for speaker in speakers:
        if speaker["id"] == speaker_id:
            speaker["name"] = new_name
    
    # Update speaker name in transcript segments
    transcript = meeting.get("transcript", [])
    for segment in transcript:
        if segment["speaker_id"] == speaker_id:
            segment["speaker_name"] = new_name
    
    await db.meetings.update_one(
        {"_id": meeting_id},
        {"$set": {"speakers": speakers, "transcript": transcript}}
    )
    
    return {"message": f"Speaker renamed to '{new_name}' successfully"}


@router.delete("/{meeting_id}")
async def delete_meeting(meeting_id: str):
    """Delete a meeting record."""
    db = _get_db_or_raise()
    result = await db.meetings.delete_one({"_id": meeting_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Meeting not found")
    # Remove from FAISS index too
    remove_meeting_from_index(meeting_id)
    return {"message": "Meeting deleted successfully"}