import os
from huggingface_hub import HfApi

api = HfApi()
token = os.getenv("HUGGINGFACE_TOKENN")

if not token:
    raise ValueError("Set HUGGINGFACE_TOKEN in your environment before running this script.")

models = [
    "pyannote/speaker-diarization-3.1",
    "pyannote/speaker-diarization-community-1", 
    "pyannote/segmentation-3.0",
    "pyannote/wespeaker-voxceleb-resnet34-LM",
]

for m in models:
    try:
        api.model_info(m, token=token)
        print(f"✅ {m}")
    except Exception as e:
        print(f"❌ {m} → {e}")