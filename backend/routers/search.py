import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from backend.services.rag.search import answer_query
from backend.databases.mongo import get_db

router = APIRouter(prefix="/search", tags=["Search"])
logger = logging.getLogger(__name__)


class SearchRequest(BaseModel):
    query: str
    meeting_id: Optional[str] = None   # Optional — None means search all meetings


@router.post("/")
async def search_meetings(request: SearchRequest):
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

        result = answer_query(
            query=request.query,
            meeting_id=request.meeting_id,
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
):
    """
    Search within a single specific meeting.
    Convenience endpoint for the meeting detail page.
    """
    if not q.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    if len(q) > 500:
        raise HTTPException(status_code=400, detail="Query too long (max 500 chars)")

    db = get_db()

    meeting = await db.meetings.find_one({"_id": meeting_id})
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    try:

        result = answer_query(query=q, meeting_id=meeting_id)
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