import os
import json
import logging
import numpy as np
from typing import Any, Dict, List
from sentence_transformers import SentenceTransformer
import faiss

logger = logging.getLogger(__name__)


# ── Constants ──────────────────────────────────────────────
FAISS_DIR = "faiss_store"
INDEX_FILE = os.path.join(FAISS_DIR, "meetings.index")
METADATA_FILE = os.path.join(FAISS_DIR, "metadata.json")
EMBED_MODEL = "all-MiniLM-L6-v2"
CHUNK_SIZE = 300       # words per chunk
CHUNK_OVERLAP = 50     # overlap between chunks

os.makedirs(FAISS_DIR, exist_ok=True)


# Load embedding model once
_embed_model = None

def get_embed_model() -> SentenceTransformer:
    global _embed_model
    if _embed_model is None:
        logger.info("Loading embedding model: %s", EMBED_MODEL)
        _embed_model = SentenceTransformer(EMBED_MODEL)
        logger.info("Embedding model loaded")
    return _embed_model


# ── Chunking ───────────────────────────────────────────────
def _chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    """
    Split text into overlapping word-based chunks.
    Overlap ensures context isn't lost at chunk boundaries.
    """
    words = text.split()
    chunks = []
    start = 0

    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        if end == len(words):
            break
        start += chunk_size - overlap

    return chunks


def _build_indexable_text(meeting_id: str, transcript: List[Dict], report: Dict) -> str:
    """
    Combine transcript + report into one rich text blob for embedding.
    This gives RAG both the raw conversation AND the structured insights.
    """
    parts = []

    # Add report summary if available
    if report:
        if report.get("tldr"):
            parts.append(f"SUMMARY: {report['tldr']}")
        if report.get("summary"):
            parts.append(f"DETAILED SUMMARY: {report['summary']}")
        if report.get("topics_discussed"):
            parts.append(f"TOPICS: {', '.join(report['topics_discussed'])}")

        # Add decisions as searchable text
        for d in report.get("decisions", []):
            parts.append(f"DECISION: {d.get('decision', '')} — Context: {d.get('context', '')}")

        # Add action items as searchable text
        for a in report.get("action_items", []):
            parts.append(f"ACTION ITEM: {a.get('task', '')} — Owner: {a.get('owner', '')} — Deadline: {a.get('deadline', '')}")

        # Add blockers
        for b in report.get("blockers", []):
            parts.append(f"BLOCKER: {b.get('issue', '')} — Severity: {b.get('severity', '')}")

    # Add full transcript
    for seg in transcript:
        speaker = seg.get("speaker_id", "Unknown")
        text = seg.get("text", "").strip()
        start = seg.get("start", 0)
        parts.append(f"[{int(start)}s] {speaker}: {text}")

    return "\n".join(parts)


# ── FAISS index management ─────────────────────────────────

def _load_index_and_metadata():
    """Load existing FAISS index and metadata from disk, or return empty ones."""
    if os.path.exists(INDEX_FILE) and os.path.exists(METADATA_FILE):
        index = faiss.read_index(INDEX_FILE)
        with open(METADATA_FILE, "r") as f:
            metadata = json.load(f)
        logger.info("Loaded FAISS index with %d vectors", index.ntotal)
        return index, metadata

    logger.info("No FAISS index found, initializing empty metadata")
    return None, []


def _save_index_and_metadata(index, metadata: list):
    """Persist FAISS index and metadata to disk."""
    faiss.write_index(index, INDEX_FILE)
    with open(METADATA_FILE, "w") as f:
        json.dump(metadata, f)
    logger.info("Saved FAISS index with %d vectors", index.ntotal)


def embed_meeting(
    meeting_id: str,
    transcript: List[Dict],
    report: Dict,
    meeting_title: str = "",
    user_id: str = "",
) -> int:
    """
    Embed a meeting's transcript + report into the FAISS index.
    Each chunk becomes one vector with metadata linking back to the meeting.

    Returns:
        Number of chunks embedded
    """
    logger.info("Embedding meeting %s into FAISS", meeting_id)

    try:
        # Build full text
        full_text = _build_indexable_text(meeting_id, transcript, report).strip()

        # Chunk it
        chunks = _chunk_text(full_text)
        if not chunks:
            logger.warning("No chunks generated for meeting %s", meeting_id)
            return 0

        # Embed all chunks
        model = get_embed_model()
        embeddings = model.encode(chunks, batch_size=32, show_progress_bar=False)
        embeddings = np.array(embeddings, dtype=np.float32)
        if embeddings.ndim != 2:
            raise ValueError("Unexpected embeddings shape")

        dimension = embeddings.shape[1]

        # Load existing index and metadata
        index, metadata = _load_index_and_metadata()

        # Remove old chunks for this meeting (re-embedding after re-analysis)
        remaining = [m for m in metadata if m.get("meeting_id") != meeting_id]

        # Rebuild index from remaining metadata
        new_index = faiss.IndexFlatL2(dimension)
        if remaining:
            texts = [m.get("text", "") for m in remaining]
            remaining_embeddings = model.encode(
                texts, batch_size=32, show_progress_bar=False
            )
            remaining_embeddings = np.array(remaining_embeddings, dtype=np.float32)
            if remaining_embeddings.ndim == 2 and remaining_embeddings.size > 0:
                new_index.add(remaining_embeddings)

        for i, m in enumerate(remaining):
            m["vector_id"] = i

        # Add new chunks
        start_idx = new_index.ntotal
        new_index.add(embeddings)

        for i, chunk in enumerate(chunks):
            remaining.append({
                "vector_id": start_idx + i,
                "meeting_id": meeting_id,
                "meeting_title": meeting_title,
                "chunk_index": i,
                "user_id": user_id,
                "text": chunk,
            })

        for i, m in enumerate(remaining):
            m["vector_id"] = i

        _save_index_and_metadata(new_index, remaining)

        logger.info("Embedded %d chunks for meeting %s", len(chunks), meeting_id)
        return len(chunks)
    except Exception:
        logger.error("Embedding failed for meeting %s", meeting_id, exc_info=True)
        return 0

def remove_meeting_from_index(meeting_id: str):
    """
    Remove all chunks for a deleted meeting from metadata.
    Note: FAISS FlatL2 doesn't support deletion, so we rebuild the index.
    """
    index, metadata = _load_index_and_metadata()
    if not metadata:
        return

    # Filter out this meeting's chunks
    remaining = [m for m in metadata if m["meeting_id"] != meeting_id]

    if len(remaining) == len(metadata):
        return  # Nothing to remove

    # Rebuild index from remaining chunks
    model = get_embed_model()

    if remaining:
        texts = [m.get("text", "") for m in remaining]
        embeddings = model.encode(texts, batch_size=32, show_progress_bar=False)
        embeddings = np.array(embeddings, dtype=np.float32)
        if embeddings.ndim != 2:
            logger.error("Unexpected embeddings shape while rebuilding index")
            return
        dimension = embeddings.shape[1]
    else:
        dimension = index.d if index is not None else 384  # default for MiniLM

    new_index = faiss.IndexFlatL2(dimension)

    if remaining:
        new_index.add(embeddings)

    for i, m in enumerate(remaining):
        m["vector_id"] = i

    _save_index_and_metadata(new_index, remaining)
    logger.info("Removed meeting %s from FAISS index", meeting_id)