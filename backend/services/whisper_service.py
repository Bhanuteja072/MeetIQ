import whisper
import torch
from pathlib import Path
# Load model once at startup (not on every request)
# Options: "tiny", "base", "small", "medium", "large"
# Start with "base" — good balance of speed and accuracy
MODEL_SIZE = "base"
model = None

# MODEL_SIZE   = "medium"
# COMPUTE_TYPE = "int8"   # GPU: "float16" | CPU or low VRAM: "int8"
# BEAM_SIZE    = 5

# _model  = None
# _device = None
# def _get_device() -> str:
#     try:
#         import torch
#         return "cuda" if torch.cuda.is_available() else "cpu"
#     except ImportError:
#         return "cpu"
    

def load_whisper_model():
    global model
    if model is None:
        try:
            print(f"🔄 Loading Whisper {MODEL_SIZE} model...")
            device = "cuda" if torch.cuda.is_available() else "cpu"
            model = whisper.load_model(MODEL_SIZE, device=device)
            print(f"✅ Whisper model loaded on {device}")
        except Exception as e:
            raise RuntimeError(f"Whisper model failed to load: {e}")
    return model


# def load_whisper_model():
#     """
#     Load faster-whisper model once and cache globally.
 
#     faster-whisper vs old openai-whisper:
#     - Same model weights (large-v2 etc.) — identical transcription quality
#     - Uses CTranslate2 C++ engine instead of PyTorch → 4x faster, less memory
#     - NO torch dependency conflict → zero clash with pyannote
#     - Word-level timestamps built-in via DTW on Whisper's own attention scores
#     """
#     global _model, _device
 
#     if _model is not None:
#         return _model
 
#     try:
#         from faster_whisper import WhisperModel
#     except ImportError:
#         raise ImportError(
#             "faster-whisper is not installed.\n"
#             "Run: pip install faster-whisper"
#         )
 
#     _device = _get_device()
 
#     # float16 only works on CUDA — fall back to int8 on CPU
#     compute_type = COMPUTE_TYPE if _device == "cuda" else "int8"
 
#     print(f"🔄 Loading faster-whisper '{MODEL_SIZE}' on {_device} ({compute_type})...")
 
#     _model = WhisperModel(
#         MODEL_SIZE,
#         device=_device,
#         compute_type=compute_type,
#     )
 
#     print(f"✅ faster-whisper loaded on {_device}")
#     return _model

def transcribe_audio(file_path: str) -> dict:
    """
    Takes audio file path, returns full transcription with timestamps.
    
    Returns:
    {
        "text": "full transcript text",
        "segments": [
            {"start": 0.0, "end": 3.5, "text": "Hello everyone"},
            ...
        ],
        "language": "en",
        "duration": 3600.0
    }
    """
    if not Path(file_path).exists():
        raise FileNotFoundError(f"Audio file not found: {file_path}")
    whisper_model = load_whisper_model()
    
    print(f"🎙️ Transcribing: {file_path}")
    
    try:

        result = whisper_model.transcribe(
            file_path,
            verbose=False,
            word_timestamps=True,   # Timestamps per word
            task="transcribe"       # Use "translate" to convert non-English to English
        )
    except Exception as e:
        raise RuntimeError(f"Transcription failed: {e}")
    
    # Clean up segments to only what we need
    cleaned_segments = []
    for seg in result["segments"]:
        cleaned_segments.append({
            "start": round(seg["start"], 2),
            "end": round(seg["end"], 2),
            "text": seg["text"].strip()
        })
    
    total_duration = cleaned_segments[-1]["end"] if cleaned_segments else 0
    
    print(f"✅ Transcription complete. Duration: {total_duration}s, Segments: {len(cleaned_segments)}")
    
    return {
        "text": result["text"].strip(),
        "segments": cleaned_segments,
        "language": result.get("language", "en"),
        "duration": total_duration
    }