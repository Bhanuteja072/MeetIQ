def seconds_to_timestamp(seconds: float) -> str:
    """Convert 3661.5 → '01:01:01'"""
    seconds = int(seconds)
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"

def format_transcript_for_display(segments: list) -> str:
    """
    Convert transcript segments into readable text format.
    
    Output:
    [00:00:05] Speaker 1: Hello everyone, welcome to the meeting.
    [00:00:12] Speaker 2: Thanks for joining.
    """
    lines = []
    for seg in segments:
        timestamp = seconds_to_timestamp(seg.get("start", 0))
        speaker = seg.get("speaker_name") or seg.get("speaker_id", "Unknown")
        text = seg.get("text", "")
        lines.append(f"[{timestamp}] {speaker}: {text}")
    
    return "\n".join(lines)