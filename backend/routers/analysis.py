import logging, asyncio
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from backend.dependencies.auth import get_current_user
from backend.databases.mongo import get_db
from backend.models.report import MeetingReport
from backend.services.graph.pipeline import run_analysis_pipeline
from backend.services.rag.embeddings import embed_meeting
from datetime import datetime

router = APIRouter(prefix="/analysis", tags=["Analysis"])
logger = logging.getLogger(__name__)


def _get_db_or_raise():
    db = get_db()
    if db is None:
        raise HTTPException(status_code=500, detail="Database not initialized")
    return db


@router.post("/{meeting_id}/analyze")
async def trigger_analysis(meeting_id: str, background_tasks: BackgroundTasks, current_user: dict = Depends(get_current_user)):
    """
    Trigger the 4-agent LangGraph analysis pipeline for a meeting.
    Meeting must already be transcribed (status = completed).
    Runs in background — use GET /analysis/{meeting_id}/report to fetch results.
    """
    db = _get_db_or_raise()
    meeting = await db.meetings.find_one({"_id": meeting_id, "user_id": current_user["_id"]})

    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    if meeting["status"] != "completed":
        raise HTTPException(
            status_code=400,
            detail=f"Meeting is not ready for analysis. Current status: {meeting['status']}"
        )

    if not meeting.get("transcript"):
        raise HTTPException(
            status_code=400,
            detail="Meeting has no transcript to analyze"
        )

    # Mark as analyzing
    await db.meetings.update_one(
        {"_id": meeting_id},
        {"$set": {"analysis_status": "analyzing"}}
    )

    background_tasks.add_task(
        _run_analysis_background,
        meeting_id,
        meeting["transcript"],
        meeting.get("speakers", []),
        current_user["_id"]
    )

    return {
        "meeting_id": meeting_id,
        "message": "Analysis started. Check status at GET /analysis/{meeting_id}/report",
        "analysis_status": "analyzing"
    }


@router.get("/{meeting_id}/report")
async def get_report(meeting_id: str, current_user: dict = Depends(get_current_user)):
    """
    Fetch the analysis report for a meeting.
    Returns the report if ready, or current status if still processing.
    """
    db = _get_db_or_raise()
    meeting = await db.meetings.find_one({"_id": meeting_id, "user_id": current_user["_id"]})

    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    analysis_status = meeting.get("analysis_status", "not_started")

    if analysis_status == "not_started":
        raise HTTPException(
            status_code=404,
            detail="Analysis has not been triggered. POST /analysis/{meeting_id}/analyze first"
        )

    if analysis_status == "analyzing":
        return {
            "meeting_id": meeting_id,
            "analysis_status": "analyzing",
            "message": "Analysis in progress, check back in a few seconds"
        }

    if analysis_status == "failed":
        return {
            "meeting_id": meeting_id,
            "analysis_status": "failed",
            "error": meeting.get("analysis_error", "Unknown error")
        }

    # Return the full report
    raw_report = meeting.get("report", {})
    # Strip fields not in MeetingReport before validating
    return{
        "meeting_id": meeting_id,
        "analysis_status": "completed",
        "report": raw_report
    }


async def _run_analysis_background(
    meeting_id: str,
    transcript: list,
    speakers: list,
    user_id: str = "", 
):
    """Background task that runs the LangGraph pipeline and saves report to MongoDB."""
    db = _get_db_or_raise()

    try:
        report = await run_analysis_pipeline(meeting_id, transcript, speakers)

        await db.meetings.update_one(
            {"_id": meeting_id},
            {"$set": {
                "report": report,
                "analysis_status": "completed",
                "embedding_status": "pending",
                "analyzed_at": datetime.utcnow()
            }}
        )
        logger.info("Analysis complete for meeting %s", meeting_id)
    except Exception as e:
        await db.meetings.update_one(
            {"_id": meeting_id},
            {"$set": {
                "analysis_status": "failed",
                "analysis_error": str(e)
            }}
        )
        logger.exception("Analysis failed for meeting %s", meeting_id)
        return
    # try:
    #     await db.meetings.update_one(
    #                     {"_id": meeting_id},
    #         {"$set": {"embedding_status": "embedding"}}
    #     )
    #     await asyncio.sleep(0) 
    #     meeting_doc = await db.meetings.find_one({"_id": meeting_id})
    #     await asyncio.to_thread(
    #             embed_meeting,
    #             meeting_id=meeting_id,
    #             transcript=transcript,
    #             report=report,
    #             meeting_title=meeting_doc.get("title", ""),
    #             user_id=user_id, 
    #     )
    #     await db.meetings.update_one(
    #         {"_id": meeting_id},
    #         {"$set": {"embedding_status": "completed"}}
    #     )
    # except Exception as embed_err:
    #     await db.meetings.update_one(
    #         {"_id": meeting_id},
    #         {"$set": {
    #             "embedding_status": "failed",
    #         }}
    #     )
    #     logger.warning("Embedding failed for meeting %s: %s", meeting_id, embed_err)