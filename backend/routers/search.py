import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Query, Depends
from backend.dependencies.auth import get_current_user
from pydantic import BaseModel
from backend.services.rag.search import answer_query
from backend.services.rag.embeddings import embed_meeting
from backend.databases.mongo import get_db

router = APIRouter(prefix="/search", tags=["Search"])
logger = logging.getLogger(__name__)


class SearchRequest(BaseModel):
    query: str
    meeting_id: Optional[str] = None   # Optional — None means search all meetings


@router.post("/")
async def search_meetings(request: SearchRequest, current_user: dict = Depends(get_current_user)):
    """
    Natural language search across all meeting records.

    Example queries:
    - "What did we decide about the drain?"
    - "What are all unresolved blockers?"
    - "What tasks were assigned to Councillor Fuel?"
    - "What happened in the tax cancellation discussion?"
    """
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    if len(request.query) > 500:
        raise HTTPException(status_code=400, detail="Query too long (max 500 chars)")

    logger.info("Search query: '%s' | meeting_id: %s", request.query, request.meeting_id)
    try:

        result = await answer_query(
            query=request.query,
            meeting_id=request.meeting_id,
            user_id=current_user["_id"]
        )
    except Exception as e:
        logger.error("Search failed", exc_info=True)
        raise HTTPException(status_code=500, detail="Search failed due to an internal error")

    return {
        "query": request.query,
        "meeting_id": request.meeting_id,
        "answer": result["answer"],
        "sources": result["sources"],
        "chunks_used": result["chunks_used"],
    }


@router.get("/meetings/{meeting_id}/search")
async def search_within_meeting(
    meeting_id: str,
    q: str = Query(..., description="Your question about this meeting"),
    current_user: dict = Depends(get_current_user)
):
    """
    Search within a single specific meeting.
    Convenience endpoint for the meeting detail page.
    """
    q = q.strip()
    meeting_id = meeting_id.strip()

    if not q:
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    if len(q) > 500:
        raise HTTPException(status_code=400, detail="Query too long (max 500 chars)")
    if not meeting_id:
        raise HTTPException(status_code=400, detail="Meeting ID cannot be empty")

    db = get_db()

    meeting = await db.meetings.find_one({"_id": meeting_id, "user_id": current_user["_id"]})
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    # Auto-embed if embedding hasn't completed yet
    embedding_status = meeting.get("embedding_status")
    # If currently embedding from a previous request, wait briefly and recheck
    if embedding_status == "embedding":
        raise HTTPException(
            status_code=503,
            detail="Meeting is being prepared for search, please try again in a moment."
        )
    if embedding_status in (None, "pending", "failed"):
        report=meeting.get("report")
        if not report:
            raise HTTPException(status_code=503, detail="Meeting analysis not completed yet, please try again later")
        try:
            await db.meetings.update_one(
                {"_id": meeting_id},
                {"$set": {"embedding_status": "embedding"}}
            )
            await embed_meeting(
                meeting_id=meeting_id,
                transcript=meeting.get("transcript", []),
                report=report,
                meeting_title=meeting.get("title", ""),
                user_id=current_user["_id"],
            )
            await db.meetings.update_one(
                {"_id": meeting_id},
                {"$set": {"embedding_status": "completed"}}
                )
        except Exception as e:
            await db.meetings.update_one(
                {"_id": meeting_id},
                {"$set": {"embedding_status": "failed"}}
            )
            logger.error("Embedding failed for meeting %s: %s", meeting_id, e)
            raise HTTPException(status_code=500, detail="Failed to prepare meeting for search, please try again later")

    try:

        result = await answer_query(query=q, meeting_id=meeting_id, user_id=current_user["_id"])
    except Exception as e:
        logger.error("Search failed", exc_info=True)
        raise HTTPException(status_code=500, detail="Search failed due to an internal error")
    return {
        "query": q,
        "meeting_id": meeting_id,
        "meeting_title": meeting.get("title", ""),
        "answer": result["answer"],
        "sources": result["sources"],
        "chunks_used": result["chunks_used"],
    }