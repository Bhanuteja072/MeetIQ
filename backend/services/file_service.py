import os
import re
from typing import Dict, List

import PyPDF2


def parse_transcript_file(file_path: str, file_type: str) -> str:
    """
    Reads an uploaded transcript file and returns raw text.
    Supports: .txt, .pdf
    """
    
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"Transcript file not found: {file_path}")

    normalized_type = (file_type or "").strip().lower()

    if normalized_type in ["text/plain", ".txt"]:
        return _parse_txt(file_path)
    elif normalized_type in ["application/pdf", ".pdf"]:
        return _parse_pdf(file_path)
    else:
        raise ValueError(f"Unsupported file type: {file_type}")


def _parse_txt(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read().strip()
    
    if not content:
        raise ValueError("Transcript file is empty")
    
    return content


def _parse_pdf(file_path: str) -> str:
    text = ""
    
    with open(file_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        
        for page_num, page in enumerate(reader.pages):
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    
    text = text.strip()
    
    if not text:
        raise ValueError("Could not extract text from PDF. It may be a scanned image.")
    
    return text


def text_to_segments(raw_text: str) -> List[Dict[str, object]]:
    """
    Converts raw transcript text into fake segments with speaker detection.
    
    Handles common transcript formats like:
    - "John: Hello everyone"
    - "Speaker 1: Good morning"
    - "[00:01:30] John: Let's start"
    
    If no speaker format detected, treats as single speaker.
    """
    
    segments: List[Dict[str, object]] = []
    lines = [line.strip() for line in raw_text.split("\n") if line.strip()]
    
    # Detect speaker pattern: "Name: text" or "[timestamp] Name: text"
    speaker_pattern = re.compile(
        r'^(?:\[[\d:]+\]\s*)?([A-Za-z][A-Za-z\s]{0,30}):\s*(.+)$'
    )
    
    speaker_index: Dict[str, str] = {}
    fake_time = 0.0
    
    for line in lines:
        match = speaker_pattern.match(line)
        
        if match:
            speaker_name = match.group(1).strip()
            text = match.group(2).strip()
            
            # Assign consistent speaker IDs
            if speaker_name not in speaker_index:
                speaker_index[speaker_name] = f"speaker_{len(speaker_index) + 1}"
            
            estimated_duration = len(text.split()) * 0.4  # ~0.4s per word
            
            segments.append({
                "speaker_id": speaker_index[speaker_name],
                "speaker_name": speaker_name,
                "text": text,
                "start": round(fake_time, 2),
                "end": round(fake_time + estimated_duration, 2)
            })
            
            fake_time += estimated_duration + 0.5
        
        else:
            # No speaker detected — single speaker
            estimated_duration = len(line.split()) * 0.4
            
            segments.append({
                "speaker_id": "speaker_1",
                "speaker_name": None,
                "text": line,
                "start": round(fake_time, 2),
                "end": round(fake_time + estimated_duration, 2)
            })
            
            fake_time += estimated_duration + 0.5
    
    return segments