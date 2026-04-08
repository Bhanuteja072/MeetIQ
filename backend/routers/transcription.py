import asyncio
import logging
import os
import uuid

import aiofiles
from fastapi import APIRouter, BackgroundTasks, File, HTTPException, UploadFile
from pathlib import Path
from config import settings
from backend.services.whisper_service import transcribe_audio
from backend.services.speaker_service import (
    diarize,
    extract_speakers,
    merge_consecutive_same_speaker
)
from backend.services.file_service import parse_transcript_file, text_to_segments
# Diarize with pyannote (real voice fingerprinting)
# from backend.services.speaker_service import diarize
from backend.databases.mongo import get_db
from datetime import datetime
from moviepy import VideoFileClip

router = APIRouter(prefix="/transcription", tags=["Transcription"])

logger = logging.getLogger(__name__)

ALLOWED_AUDIO_TYPES = {
    "audio/mpeg", "audio/mp3", "audio/wav", "audio/x-wav",
    "audio/mp4", "video/mp4", "audio/m4a"
}

ALLOWED_TRANSCRIPT_TYPES = {
    "text/plain", "application/pdf"
}

MAX_FILE_SIZE_BYTES = settings.max_file_size_mb * 1024 * 1024


def _get_db_or_raise():
    db = get_db()
    if db is None:
        raise HTTPException(status_code=500, detail="Database is not initialized")
    return db


async def _save_upload_file(
    file: UploadFile,
    file_path: str,
    max_size_bytes: int,
) -> None:
    total = 0
    chunk_size = 1024 * 1024

    async with aiofiles.open(file_path, "wb") as out_file:
        while True:
            chunk = await file.read(chunk_size)
            if not chunk:
                break
            total += len(chunk)
            if total > max_size_bytes:
                raise HTTPException(
                    status_code=413,
                    detail=f"File too large. Max size is {settings.max_file_size_mb}MB",
                )
            await out_file.write(chunk)


async def _extract_audio_from_mp4(video_path: str, output_path: str) -> None:
    def _extract() -> None:
        with VideoFileClip(video_path) as clip:
            if clip.audio is None:
                raise ValueError("Video has no audio track")
            clip.audio.write_audiofile(
                output_path,
                codec="pcm_s16le",
                fps=16000,
            )

    await asyncio.to_thread(_extract)


@router.post("/upload-audio")
async def upload_and_transcribe(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    title: str = "Untitled Meeting"
):
    """
    Upload an audio/video file.
    Saves it, creates a meeting record, then transcribes in background.
    """
    
    content_type = (file.content_type or "").lower()

    # Validate file type
    if content_type not in ALLOWED_AUDIO_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type: {file.content_type}. Allowed: MP3, WAV, MP4, M4A"
        )
    
    # Save file to disk
    file_id = str(uuid.uuid4())
    file_extension = Path(file.filename or "upload").suffix
    file_name = f"{file_id}{file_extension}"
    file_path = os.path.join(settings.upload_dir, file_name)

    try:
        await _save_upload_file(file, file_path, MAX_FILE_SIZE_BYTES)
    except HTTPException:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise
    
    # Create meeting record in MongoDB
    db = _get_db_or_raise()
    is_video = content_type == "video/mp4" or file_extension.lower() == ".mp4"
    meeting = {
        "_id": file_id,
        "title": title or file.filename,
        "file_name": file.filename,
        "file_path": file_path,
        "file_type": "video" if is_video else "audio",
        "content_type": content_type,
        "status": "uploaded",
        "created_at": datetime.utcnow(),
        "speakers": [],
        "transcript": [],
        "raw_transcript": None,
        "duration": None
    }
    
    await db.meetings.insert_one(meeting)
    
    # Transcribe in background (don't make user wait)
    background_tasks.add_task(process_audio_transcription, file_id, file_path, content_type)
    
    return {
        "meeting_id": file_id,
        "message": "File uploaded. Transcription started in background.",
        "status": "transcribing"
    }


@router.post("/upload-transcript")
async def upload_transcript_file(
    file: UploadFile = File(...),
    title: str = "Untitled Meeting"
):
    """
    Upload a TXT or PDF transcript directly.
    No Whisper needed — parses and diarizes immediately.
    """
    
    content_type = (file.content_type or "").lower()
    if content_type not in ALLOWED_TRANSCRIPT_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Only TXT and PDF transcripts are supported"
        )
    
    # Save file
    file_id = str(uuid.uuid4())
    file_extension = Path(file.filename or "upload").suffix
    file_path = os.path.join(settings.upload_dir, f"{file_id}{file_extension}")

    try:
        await _save_upload_file(file, file_path, MAX_FILE_SIZE_BYTES)
    except HTTPException:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise
    
    # Parse the transcript
    raw_text = parse_transcript_file(file_path, content_type)
    segments = text_to_segments(raw_text)
    merged_segments = merge_consecutive_same_speaker(segments)

    speakers = extract_speakers(segments)
    
    # Save to MongoDB
    db = _get_db_or_raise()
    meeting = {
        "_id": file_id,
        "title": title or file.filename,
        "file_name": file.filename,
        "file_path": file_path,
        "file_type": "transcript",
        "content_type": content_type,
        "status": "completed",
        "created_at": datetime.utcnow(),
        "speakers": speakers,
        "transcript": merged_segments,
        "raw_transcript": raw_text,
        "duration": merged_segments[-1]["end"] if merged_segments else 0
    }
    
    await db.meetings.insert_one(meeting)
    
    return {
        "meeting_id": file_id,
        "message": "Transcript uploaded and processed successfully",
        "status": "completed",
        "speakers_detected": len(speakers),
        "segments_count": len(merged_segments)
    }


@router.get("/status/{meeting_id}")
async def get_transcription_status(meeting_id: str):
    """Check the processing status of a meeting."""
    db = _get_db_or_raise()
    meeting = await db.meetings.find_one({"_id": meeting_id})
    
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    return {
        "meeting_id": meeting_id,
        "status": meeting["status"],
        "speakers_detected": len(meeting.get("speakers", [])),
        "segments_count": len(meeting.get("transcript", []))
    }


# Background task — runs after upload returns response
async def process_audio_transcription(meeting_id: str, file_path: str, content_type: str):
    """Background task: transcribe audio and update MongoDB."""
    db = _get_db_or_raise()
    audio_path = file_path
    temp_audio_path = None
    
    try:
        # Update status to transcribing
        await db.meetings.update_one(
            {"_id": meeting_id},
            {"$set": {"status": "transcribing"}}
        )

        if content_type == "video/mp4" or file_path.lower().endswith(".mp4"):
            temp_audio_path = os.path.join(settings.upload_dir, f"{meeting_id}.wav")
            await _extract_audio_from_mp4(file_path, temp_audio_path)
            audio_path = temp_audio_path

        # Transcribe with Whisper (run in thread to avoid blocking)
        result = await asyncio.to_thread(transcribe_audio, audio_path)
        
        # Diarize
        diarized = diarize(
            segments=result["segments"],
            method="pyannote",
            audio_file_path=audio_path,
        )
        merged = merge_consecutive_same_speaker(diarized)
        speakers = extract_speakers(diarized)
        
        # Update MongoDB with results
        await db.meetings.update_one(
            {"_id": meeting_id},
            {"$set": {
                "status": "completed",
                "raw_transcript": result["text"],
                "transcript": merged,
                "speakers": speakers,
                "duration": result["duration"],
                "language": result.get("language", "en")
            }}
        )

        logger.info("Meeting %s transcription complete", meeting_id)
        
    except Exception as e:
        await db.meetings.update_one(
            {"_id": meeting_id},
            {"$set": {"status": "failed", "error": str(e)}}
        )
        logger.exception("Transcription failed for %s", meeting_id)
    finally:
        if temp_audio_path and os.path.exists(temp_audio_path):
            try:
                os.remove(temp_audio_path)
            except OSError:
                logger.warning("Failed to remove temp audio file: %s", temp_audio_path)