from typing import Any, Dict, List, Optional, TypedDict
from config import settings

import os


class Segment(TypedDict, total=False):
    start: float
    end: float
    text: str
    speaker_id: str


class SpeakerSummary(TypedDict):
    id: str
    name: None
    total_speaking_time: float


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _safe_str(value: Any) -> str:
    return "" if value is None else str(value)


def _patch_speechbrain_lazy_imports() -> None:
    try:
        import inspect
        import os
        import sys
        import warnings
        from speechbrain.utils import importutils as sb_importutils

        current = sb_importutils.LazyModule.ensure_module
        if getattr(current, "_patched_for_windows", False):
            return

        def _ensure_module(self, stacklevel: int):
            importer_frame = None
            try:
                importer_frame = inspect.getframeinfo(sys._getframe(stacklevel + 1))
            except AttributeError:
                warnings.warn(
                    "Failed to inspect frame for SpeechBrain lazy import patch."
                )

            if importer_frame is not None:
                if os.path.basename(importer_frame.filename) == "inspect.py":
                    raise AttributeError()

            return current(self, stacklevel)

        _ensure_module._patched_for_windows = True
        sb_importutils.LazyModule.ensure_module = _ensure_module
    except Exception:
        return

# ─────────────────────────────────────────────
# pyannote pipeline (loaded once, reused)
# ─────────────────────────────────────────────
 
_pyannote_pipeline = None

def _load_pyannote_pipeline():
    """
    Loads the pyannote speaker diarization pipeline.
    Cached globally so it's only loaded once per server start.
    Requires HUGGINGFACE_TOKEN in environment.
    """
    global _pyannote_pipeline
 
    if _pyannote_pipeline is not None:
        return _pyannote_pipeline
 
    _patch_speechbrain_lazy_imports()

    try:
        from pyannote.audio import Pipeline
        import torch
    except ImportError as exc:
        raise ImportError(
            "pyannote.audio is not installed. Run: pip install pyannote.audio"
        ) from exc

    token = settings.huggingface_token.strip()
    if not token:
        raise ValueError(
            "HUGGINGFACE_TOKEN not set in environment. "
            "Get your token from huggingface.co/settings/tokens"
        )

    print("🔄 Loading pyannote speaker diarization pipeline...")

    try:
        from huggingface_hub import login

        try:
            login(token=token)
        except TypeError:
            login(use_auth_token=token)
    except ImportError:
        pass

    pipeline = Pipeline.from_pretrained(
        "pyannote/speaker-diarization-3.1",
    )

    # Use GPU if available, otherwise CPU
    device = "cuda" if torch.cuda.is_available() else "cpu"
    pipeline = pipeline.to(torch.device(device))

    print(f"✅ pyannote pipeline loaded on {device}")
    _pyannote_pipeline = pipeline
    return pipeline
 
 
# ─────────────────────────────────────────────
# Core: pyannote diarization
# ─────────────────────────────────────────────


def pyannote_diarization(
    audio_file_path: str,
    whisper_segments: List[Dict[str, Any]],
    num_speakers: Optional[int] = None,
    min_speakers: Optional[int] = None,
    max_speakers: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """
    Real speaker diarization using pyannote.audio.
 
    How it works:
    1. pyannote analyzes the audio file and returns speaker turns with timestamps
       e.g. "SPEAKER_00 spoke from 0s to 4.2s, SPEAKER_01 spoke from 4.5s to 9.1s"
    2. We align each Whisper text segment to whichever pyannote speaker
       was speaking at the midpoint of that segment
    3. Return the Whisper segments with correct speaker_ids attached
 
    Args:
        audio_file_path: Path to the original audio/video file
        whisper_segments:  List of Whisper output segments with start/end/text
        num_speakers: Exact number of speakers (if you know it, helps accuracy)
        min_speakers: Minimum expected speakers
        max_speakers: Maximum expected speakers
 
    Returns:
        Same segments list but each dict now has a correct speaker_id
    """
    if not whisper_segments:
        return []
 
    if not os.path.exists(audio_file_path):
        raise FileNotFoundError(f"Audio file not found: {audio_file_path}")
 
    pipeline = _load_pyannote_pipeline()
 
    print(f"🎙️ Running pyannote diarization on: {audio_file_path}")
 
    # Build kwargs — only pass speaker counts if provided
    diarize_kwargs: Dict[str, Any] = {}
    if num_speakers is not None:
        diarize_kwargs["num_speakers"] = num_speakers
    elif min_speakers is not None or max_speakers is not None:
        if min_speakers:
            diarize_kwargs["min_speakers"] = min_speakers
        if max_speakers:
            diarize_kwargs["max_speakers"] = max_speakers
 
    # Run pyannote on the audio file
    diarization_result = pipeline(audio_file_path, **diarize_kwargs)
 
    # Convert pyannote output into a flat list of speaker turns
    # Each turn: {"start": float, "end": float, "speaker": "SPEAKER_00"}
    speaker_turns: List[Dict[str, Any]] = []
    for turn, _, speaker_label in diarization_result.itertracks(yield_label=True):
        speaker_turns.append({
            "start": turn.start,
            "end": turn.end,
            "speaker": speaker_label,  # e.g. "SPEAKER_00"
        })
 
    print(f"✅ pyannote detected {len(set(t['speaker'] for t in speaker_turns))} unique speakers "
          f"across {len(speaker_turns)} turns")
 
    # Build a clean speaker label → speaker_N mapping
    # so output is "speaker_1", "speaker_2" etc. (consistent with rest of app)
    raw_labels = sorted(set(t["speaker"] for t in speaker_turns))
    label_to_id = {
        label: f"speaker_{i + 1}"
        for i, label in enumerate(raw_labels)
    }
 
    # Assign each Whisper segment to a speaker
    # Strategy: use the midpoint of the Whisper segment to find which
    # pyannote speaker turn covers that moment
    result_segments: List[Dict[str, Any]] = []
 
    for seg in whisper_segments:
        seg_copy = seg.copy()
        start = _safe_float(seg_copy.get("start"))
        end = _safe_float(seg_copy.get("end"), start)
        midpoint = (start + end) / 2
 
        # Find the speaker turn that contains this midpoint
        matched_speaker = _find_speaker_at_time(speaker_turns, midpoint)
 
        if matched_speaker:
            seg_copy["speaker_id"] = label_to_id[matched_speaker]
        else:
            # Fallback: find nearest turn by start time
            nearest = _find_nearest_speaker(speaker_turns, midpoint)
            seg_copy["speaker_id"] = label_to_id.get(nearest, "speaker_1")
 
        seg_copy["start"] = start
        seg_copy["end"] = end
        seg_copy["text"] = _safe_str(seg_copy.get("text")).strip()
        result_segments.append(seg_copy)
 
    return result_segments
 

def _find_speaker_at_time(
    speaker_turns: List[Dict[str, Any]],
    timestamp: float
) -> Optional[str]:
    """
    Returns the speaker label whose turn contains the given timestamp.
    Returns None if no turn covers that exact moment.
    """
    for turn in speaker_turns:
        if turn["start"] <= timestamp <= turn["end"]:
            return turn["speaker"]
    return None


def _find_nearest_speaker(
    speaker_turns: List[Dict[str, Any]],
    timestamp: float
) -> str:
    """
    Fallback: returns the speaker whose turn START is closest to the timestamp.
    Used when a Whisper segment falls in a gap between pyannote turns.
    """
    if not speaker_turns:
        return "SPEAKER_00"
 
    closest = min(speaker_turns, key=lambda t: abs(t["start"] - timestamp))
    return closest["speaker"]


 
# ─────────────────────────────────────────────
# Fallback: simple rule-based diarization
# (kept for offline/no-token use)
# ─────────────────────────────────────────────

def simple_speaker_diarization(
    segments: List[Dict[str, Any]],
    gap_threshold: float = 1.5,
) -> List[Dict[str, Any]]:
    """
    Simple rule-based speaker diarization.

    Logic:
    - Sort by start time
    - If gap between segments > gap_threshold, switch to a new speaker
    - First segment is speaker_1
    - Never mutate the input list or its items
    """
    if not segments:
        return []

    sorted_segments: List[Segment] = sorted(
        (seg.copy() for seg in segments),
        key=lambda s: _safe_float(s.get("start")),
    )

    diarized: List[Segment] = []
    current_speaker = 1
    last_end: Optional[float] = None

    for segment in sorted_segments:
        start = _safe_float(segment.get("start"))
        end = _safe_float(segment.get("end"), start)

        if last_end is None:
            current_speaker = 1
        else:
            gap = start - last_end
            if gap > gap_threshold:
                current_speaker += 1

        segment["speaker_id"] = f"speaker_{current_speaker}"
        segment["start"] = start
        segment["end"] = end
        segment["text"] = _safe_str(segment.get("text")).strip()

        diarized.append(segment)
        last_end = end

    return [dict(seg) for seg in diarized]

# ─────────────────────────────────────────────
# Shared utilities (used after diarization)
# ─────────────────────────────────────────────

def extract_speakers(diarized_segments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Extract unique speakers and calculate total speaking time.
    """
    if not diarized_segments:
        return []

    totals: Dict[str, float] = {}

    for seg in diarized_segments:
        sid = _safe_str(seg.get("speaker_id")).strip()
        if not sid:
            continue

        start = _safe_float(seg.get("start"))
        end = _safe_float(seg.get("end"), start)
        duration = max(0.0, end - start)

        totals[sid] = totals.get(sid, 0.0) + duration

    speakers: List[SpeakerSummary] = []
    for sid, total in totals.items():
        speakers.append(
            {
                "id": sid,
                "name": None,
                "total_speaking_time": round(total, 2),
            }
        )
    speakers.sort(key=lambda s: int(s["id"].split("_")[-1]))

    return [dict(s) for s in speakers]


def merge_consecutive_same_speaker(segments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Merge consecutive segments that share the same speaker_id.
    """
    if not segments:
        return []

    merged: List[Segment] = []

    for seg in segments:
        seg_copy: Segment = seg.copy()
        seg_copy["text"] = _safe_str(seg_copy.get("text")).strip()
        seg_copy["start"] = _safe_float(seg_copy.get("start"))
        seg_copy["end"] = _safe_float(seg_copy.get("end"), seg_copy["start"])
        speaker_id = _safe_str(seg_copy.get("speaker_id")).strip()

        if not merged:
            seg_copy["speaker_id"] = speaker_id
            merged.append(seg_copy)
            continue

        last = merged[-1]
        last_speaker = _safe_str(last.get("speaker_id")).strip()

        if speaker_id and speaker_id == last_speaker:
            last_text = _safe_str(last.get("text")).strip()
            new_text = seg_copy["text"]
            if last_text and new_text:
                last["text"] = f"{last_text} {new_text}".strip()
            else:
                last["text"] = (last_text or new_text).strip()
            last["end"] = max(_safe_float(last.get("end")), seg_copy["end"])
        else:
            seg_copy["speaker_id"] = speaker_id
            merged.append(seg_copy)

    return [dict(seg) for seg in merged]



def diarize(
    segments: List[Dict[str, Any]],
    method: str = "pyannote",
    audio_file_path: Optional[str] = None,
    num_speakers: Optional[int] = None,
    min_speakers: Optional[int] = None,
    max_speakers: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """
    Main diarization entry point.
 
    Args:
        segments: Whisper output segments
        method: "pyannote" (accurate, needs HF token) or "simple" (fallback)
        audio_file_path: Required for pyannote method
        num_speakers: Hint to pyannote (optional but improves accuracy)
        min_speakers: Min expected speakers (optional)
        max_speakers: Max expected speakers (optional)
 
    Returns:
        Segments with speaker_id assigned
    """
    if method == "pyannote":
        if not audio_file_path:
            raise ValueError(
                "audio_file_path is required for pyannote diarization. "
                "Pass the path to the uploaded audio file."
            )
        return pyannote_diarization(
            audio_file_path=audio_file_path,
            whisper_segments=segments,
            num_speakers=num_speakers,
            min_speakers=min_speakers,
            max_speakers=max_speakers,
        )
 
    elif method == "simple":
        return simple_speaker_diarization(segments)
 
    else:
        raise NotImplementedError(f"Unknown diarization method: {method}")