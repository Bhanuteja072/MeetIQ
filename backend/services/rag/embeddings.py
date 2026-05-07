import logging
import httpx
from typing import Dict, List
# import faiss
from backend.databases.mongo import get_db
from config import settings

logger = logging.getLogger(__name__)


# # # ── Constants ──────────────────────────────────────────────
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# FAISS_DIR = os.path.join(BASE_DIR, "..", "..", "faiss_store")
# FAISS_DIR = os.path.normpath(FAISS_DIR)
# INDEX_FILE = os.path.join(FAISS_DIR, "meetings.index")
# METADATA_FILE = os.path.join(FAISS_DIR, "metadata.json")

# NEW made only for hugging face
# FAISS_DIR = os.environ.get("FAISS_STORE_DIR", "/tmp/faiss_store")
# INDEX_FILE = os.path.join(FAISS_DIR, "meetings.index")
# METADATA_FILE = os.path.join(FAISS_DIR, "metadata.json")


# EMBED_MODEL = "all-MiniLM-L6-v2"
EMBEDDING_MODEL = "jina-embeddings-v3"
EMBEDDING_DIMENSION = 1024
CHUNK_SIZE = 400
CHUNK_OVERLAP = 50
# ── Embedding via Nomic Atlas API ────────────────────────

# def _nomic_headers() -> Dict[str, str]:
#     if not settings.nomic_api_key:
#         raise RuntimeError("NOMIC_API_KEY is not set")
#     return {
#         "Authorization": f"Bearer {settings.nomic_api_key}",
#         "X-API-Key": settings.nomic_api_key,
#         "Content-Type": "application/json",
#     }
async def get_embeddings(texts: List[str]) -> List[List[float]]:
    """Jina AI embeddings — free tier with API key."""
    if not texts:
        return []

    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(
            "https://api.jina.ai/v1/embeddings",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {settings.jina_api_key}"
            },
            json={
                "input": texts,
                "model": "jina-embeddings-v3"
            }
        )
        if response.status_code != 200:
            raise RuntimeError(
                f"Jina embedding API failed [{response.status_code}]: {response.text}"
            )
        data = response.json()
        return [item["embedding"] for item in data["data"]]

# async def get_query_embedding(query: str) -> List[float]:
#     """
#     Embed a single search query.
#     Uses task_type='search_query' for better retrieval quality.
#     """
#     url = settings.nomic_embeddings_url
 
#     payload = {
#         "model": EMBEDDING_MODEL,
#         "texts": [query],
#         "task_type": "search_query",
#     }
 
#     async with httpx.AsyncClient(timeout=60) as client:
#         response = await client.post(url, json=payload, headers=_nomic_headers())
 
#     if response.status_code != 200:
#         raise RuntimeError(
#             f"Nomic embedding API failed [{response.status_code}]: {response.text}"
#         )
 
#     data = response.json()
#     return data["embeddings"][0]
 
 

# os.makedirs(FAISS_DIR, exist_ok=True)


# Load embedding model once
# _embed_model = None

# def get_embed_model():
#     global _embed_model
#     if _embed_model is None:
#         logger.info("Loading embedding model: %s", EMBED_MODEL)
#         from sentence_transformers import SentenceTransformer
#         _embed_model = SentenceTransformer(EMBED_MODEL)
#         logger.info("Embedding model loaded")
#     return _embed_model
# def get_embed_model(texts: List[str]) -> List[List[float]]:
#     """
#     Call Nomic embedding API.
#     Returns list of embedding vectors.
#     """
#     if not settings.nomic_api_key:
#         raise RuntimeError("NOMIC_API_KEY is not set")
#     response = requests.post(
#         settings.nomic_embeddings_url,
#         headers={
#             "Authorization": f"Bearer {settings.nomic_api_key}",
#             "X-API-Key": settings.nomic_api_key,
#             "Content-Type": "application/json",
#         },
#         json={
#             "input": texts,
#             "model": EMBEDDING_MODEL
#         },
#         timeout=30
#     )
#     response.raise_for_status()
#     data = response.json()
#     return [item["embedding"] for item in data["data"]]


# # ── Chunking ───────────────────────────────────────────────
# def _chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
#     """
#     Split text into overlapping word-based chunks.
#     Overlap ensures context isn't lost at chunk boundaries.
#     """
#     words = text.split()
#     chunks = []
#     start = 0

#     while start < len(words):
#         end = min(start + chunk_size, len(words))
#         chunk = " ".join(words[start:end])
#         chunks.append(chunk)
#         if end == len(words):
#             break
#         start += chunk_size - overlap

#     return chunks
def _chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    """Split text into overlapping chunks."""
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)
        i += chunk_size - overlap
    return chunks

def _build_chunks(meeting_id: str, transcript: List[Dict], report: Dict,meeting_title: str, user_id: str) -> List[str]:
    """
    Build text chunks from transcript + report.
    Same chunking logic as before.
    """
    chunks = []
    full_transcript = " ".join(
        seg.get("text", "") for seg in transcript if seg.get("text")
    )
    if full_transcript:
        for chunk in _chunk_text(full_transcript):
            if chunk.strip():
                chunks.append({
                    "meeting_id": meeting_id,
                    "meeting_title": meeting_title,
                    "user_id": user_id,
                    "type": "transcript",
                    "text": chunk,
                })
    if report:
        if report.get("tldr"):
            chunks.append({
                "meeting_id": meeting_id,
                "meeting_title": meeting_title,
                "user_id": user_id,
                "type": "tldr",
                "text": f"TL;DR: {report['tldr']}"
            })
        if report.get("summary"):
            chunks.append({
                "meeting_id": meeting_id,
                "meeting_title": meeting_title,
                "user_id": user_id,
                "type": "summary",
                "text": f"SUMMARY: {report['summary']}"
            })
        for item in report.get("action_items", []):
            task = item.get("task", "")
            owner = item.get("owner", "")
            deadline = item.get("deadline", "")
            chunks.append({
                "meeting_id": meeting_id,
                "meeting_title": meeting_title,
                "user_id": user_id,
                "type": "action_item",
                "text": f"ACTION ITEM: {task} — Owner: {owner} — Deadline: {deadline}"
            })
        for item in report.get("decisions", []):
            decision = item.get("decision", "")
            context = item.get("context", "")
            chunks.append({
                "meeting_id": meeting_id,
                "meeting_title": meeting_title,
                "user_id": user_id,
                "type": "decision",
                "text": f"DECISION: {decision} — Context: {context}"
            })
        for item in report.get("blockers", []):
            issue = item.get("issue", "")
            severity = item.get("severity", "")
            chunks.append({
                "meeting_id": meeting_id,
                "meeting_title": meeting_title,
                "user_id": user_id,
                "type": "blocker",
                "text": f"BLOCKER: {issue} — Severity: {severity}"
            })
    return chunks


async def embed_meeting(meeting_id: str, transcript: list, report: dict, meeting_title: str, user_id: str = ""):
    db = get_db()
    await db.chunks.delete_many({"meeting_id": meeting_id})

    chunks = _build_chunks(meeting_id, transcript, report, meeting_title, user_id)
    if not chunks:
        logger.warning("No chunks to embed for meeting %s", meeting_id)
        return

    texts = [c["text"] for c in chunks]
    all_embeddings = []
    for i in range(0, len(texts), 20):
        batch = texts[i:i + 20]
        embeddings = await get_embeddings(batch)
        all_embeddings.extend(embeddings)

    for chunk, embedding in zip(chunks, all_embeddings):
        chunk["embedding"] = embedding

    await db.chunks.insert_many(chunks)
    await db.chunks.create_index("meeting_id")
    await db.chunks.create_index("user_id")

    logger.info("Embedded %d chunks for meeting %s into MongoDB", len(chunks), meeting_id)


# def _build_indexable_text(meeting_id: str, transcript: List[Dict], report: Dict) -> str:
#     """
#     Combine transcript + report into one rich text blob for embedding.
#     This gives RAG both the raw conversation AND the structured insights.
#     """
#     parts = []

#     # Add report summary if available
#     if report:
#         if report.get("tldr"):
#             parts.append(f"SUMMARY: {report['tldr']}")
#         if report.get("summary"):
#             parts.append(f"DETAILED SUMMARY: {report['summary']}")
#         if report.get("topics_discussed"):
#             parts.append(f"TOPICS: {', '.join(report['topics_discussed'])}")

#         # Add decisions as searchable text
#         for d in report.get("decisions", []):
#             parts.append(f"DECISION: {d.get('decision', '')} — Context: {d.get('context', '')}")

#         # Add action items as searchable text
#         for a in report.get("action_items", []):
#             parts.append(f"ACTION ITEM: {a.get('task', '')} — Owner: {a.get('owner', '')} — Deadline: {a.get('deadline', '')}")

#         # Add blockers
#         for b in report.get("blockers", []):
#             parts.append(f"BLOCKER: {b.get('issue', '')} — Severity: {b.get('severity', '')}")

#     # Add full transcript
#     for seg in transcript:
#         speaker = seg.get("speaker_id", "Unknown")
#         text = seg.get("text", "").strip()
#         start = seg.get("start", 0)
#         parts.append(f"[{int(start)}s] {speaker}: {text}")

#     return "\n".join(parts)


# # ── FAISS index management ─────────────────────────────────

# def _load_index_and_metadata():
#     """Load existing FAISS index and metadata from disk, or return empty ones."""
#     if os.path.exists(INDEX_FILE) and os.path.exists(METADATA_FILE):
#         index = faiss.read_index(INDEX_FILE)
#         with open(METADATA_FILE, "r") as f:
#             metadata = json.load(f)
#         logger.info("Loaded FAISS index with %d vectors", index.ntotal)
#         return index, metadata

#     logger.info("No FAISS index found, initializing empty metadata")
#     return None, []


# def _save_index_and_metadata(index, metadata: list):
#     """Persist FAISS index and metadata to disk."""
#     faiss.write_index(index, INDEX_FILE)
#     with open(METADATA_FILE, "w") as f:
#         json.dump(metadata, f)
#     logger.info("Saved FAISS index with %d vectors", index.ntotal)


# def embed_meeting(
#     meeting_id: str,
#     transcript: List[Dict],
#     report: Dict,
#     meeting_title: str = "",
#     user_id: str = "",
# ) -> int:
#     """
#     Embed a meeting's transcript + report into the FAISS index.
#     Each chunk becomes one vector with metadata linking back to the meeting.

#     Returns:
#         Number of chunks embedded
#     """
#     logger.info("Embedding meeting %s into FAISS", meeting_id)

#     try:
#         # Build full text
#         full_text = _build_indexable_text(meeting_id, transcript, report).strip()

#         # Chunk it
#         chunks = _chunk_text(full_text)
#         if not chunks:
#             logger.warning("No chunks generated for meeting %s", meeting_id)
#             return 0

#         # Embed all chunks
#         model = get_embed_model()
#         embeddings = model.encode(chunks, batch_size=32, show_progress_bar=False)
#         embeddings = np.array(embeddings, dtype=np.float32)
#         if embeddings.ndim != 2:
#             raise ValueError("Unexpected embeddings shape")

#         dimension = embeddings.shape[1]

#         # Load existing index and metadata
#         index, metadata = _load_index_and_metadata()

#         # Remove old chunks for this meeting (re-embedding after re-analysis)
#         remaining = [m for m in metadata if m.get("meeting_id") != meeting_id]

#         # Rebuild index from remaining metadata
#         new_index = faiss.IndexFlatL2(dimension)
#         if remaining:
#             texts = [m.get("text", "") for m in remaining]
#             remaining_embeddings = model.encode(
#                 texts, batch_size=32, show_progress_bar=False
#             )
#             remaining_embeddings = np.array(remaining_embeddings, dtype=np.float32)
#             if remaining_embeddings.ndim == 2 and remaining_embeddings.size > 0:
#                 new_index.add(remaining_embeddings)

#         for i, m in enumerate(remaining):
#             m["vector_id"] = i

#         # Add new chunks
#         start_idx = new_index.ntotal
#         new_index.add(embeddings)

#         for i, chunk in enumerate(chunks):
#             remaining.append({
#                 "vector_id": start_idx + i,
#                 "meeting_id": meeting_id,
#                 "meeting_title": meeting_title,
#                 "chunk_index": i,
#                 "user_id": user_id,
#                 "text": chunk,
#             })

#         for i, m in enumerate(remaining):
#             m["vector_id"] = i

#         _save_index_and_metadata(new_index, remaining)

#         logger.info("Embedded %d chunks for meeting %s", len(chunks), meeting_id)
#         return len(chunks)
#     except Exception:
#         logger.error("Embedding failed for meeting %s", meeting_id, exc_info=True)
#         return 0


async def remove_meeting_from_index(meeting_id: str):
    """Delete all chunks for a meeting — called on meeting delete."""
    db = get_db()
    await db.chunks.delete_many({"meeting_id": meeting_id})
    logger.info("Removed chunks for meeting %s", meeting_id)

# def remove_meeting_from_index(meeting_id: str):
#     """
#     Remove all chunks for a deleted meeting from metadata.
#     Note: FAISS FlatL2 doesn't support deletion, so we rebuild the index.
#     """
#     index, metadata = _load_index_and_metadata()
#     if not metadata:
#         return

#     # Filter out this meeting's chunks
#     remaining = [m for m in metadata if m["meeting_id"] != meeting_id]

#     if len(remaining) == len(metadata):
#         return  # Nothing to remove

#     # Rebuild index from remaining chunks
#     model = get_embed_model()

#     if remaining:
#         texts = [m.get("text", "") for m in remaining]
#         embeddings = model.encode(texts, batch_size=32, show_progress_bar=False)
#         embeddings = np.array(embeddings, dtype=np.float32)
#         if embeddings.ndim != 2:
#             logger.error("Unexpected embeddings shape while rebuilding index")
#             return
#         dimension = embeddings.shape[1]
#     else:
#         dimension = index.d if index is not None else 384  # default for MiniLM

#     new_index = faiss.IndexFlatL2(dimension)

#     if remaining:
#         new_index.add(embeddings)

#     for i, m in enumerate(remaining):
#         m["vector_id"] = i

#     _save_index_and_metadata(new_index, remaining)
#     logger.info("Removed meeting %s from FAISS index", meeting_id)

# import logging
# import numpy as np
# from typing import Dict, List
# from sentence_transformers import SentenceTransformer
# from backend.databases.mongo import get_db

# logger = logging.getLogger(__name__)

# # ── Constants ──────────────────────────────────────────────
# EMBED_MODEL   = "all-MiniLM-L6-v2"
# CHUNK_SIZE    = 300   # words per chunk
# CHUNK_OVERLAP = 50    # overlap between chunks

# # ── Embedding model (loaded once, cached) ──────────────────
# _embed_model = None

# def get_embed_model() -> SentenceTransformer:
#     global _embed_model
#     if _embed_model is None:
#         logger.info("Loading embedding model: %s", EMBED_MODEL)
#         _embed_model = SentenceTransformer(EMBED_MODEL)
#         logger.info("Embedding model loaded")
#     return _embed_model


# # ── Chunking (unchanged) ───────────────────────────────────

# def _chunk_text(
#     text: str,
#     chunk_size: int = CHUNK_SIZE,
#     overlap: int = CHUNK_OVERLAP,
# ) -> List[str]:
#     """Split text into overlapping word-based chunks."""
#     words  = text.split()
#     chunks = []
#     start  = 0

#     while start < len(words):
#         end   = min(start + chunk_size, len(words))
#         chunk = " ".join(words[start:end])
#         chunks.append(chunk)
#         if end == len(words):
#             break
#         start += chunk_size - overlap

#     return chunks


# def _build_indexable_text(
#     meeting_id: str,
#     transcript: List[Dict],
#     report: Dict,
# ) -> str:
#     """
#     Combine transcript + report into one rich text blob for embedding.
#     Unchanged from original — gives RAG both raw conversation + structured insights.
#     """
#     parts = []

#     if report:
#         if report.get("tldr"):
#             parts.append(f"SUMMARY: {report['tldr']}")
#         if report.get("summary"):
#             parts.append(f"DETAILED SUMMARY: {report['summary']}")
#         if report.get("topics_discussed"):
#             parts.append(f"TOPICS: {', '.join(report['topics_discussed'])}")
#         for d in report.get("decisions", []):
#             parts.append(f"DECISION: {d.get('decision', '')} — Context: {d.get('context', '')}")
#         for a in report.get("action_items", []):
#             parts.append(f"ACTION ITEM: {a.get('task', '')} — Owner: {a.get('owner', '')} — Deadline: {a.get('deadline', '')}")
#         for b in report.get("blockers", []):
#             parts.append(f"BLOCKER: {b.get('issue', '')} — Severity: {b.get('severity', '')}")

#     for seg in transcript:
#         speaker = seg.get("speaker_id", "Unknown")
#         text    = seg.get("text", "").strip()
#         start   = seg.get("start", 0)
#         parts.append(f"[{int(start)}s] {speaker}: {text}")

#     return "\n".join(parts)


# # ── MongoDB storage (replaces FAISS file I/O) ──────────────

# def embed_meeting(
#     meeting_id: str,
#     transcript: List[Dict],
#     report: Dict,
#     meeting_title: str = "",
#     user_id: str = "",
# ) -> int:
#     """
#     Embed a meeting's transcript + report and store chunks in MongoDB.

#     WHAT CHANGED vs old version:
#     ────────────────────────────
#     Old: saved vectors to faiss_store/meetings.index + metadata.json on disk
#          → files wiped on HuggingFace restart → search breaks

#     New: saves each chunk as a MongoDB document in `meeting_chunks` collection
#          → MongoDB Atlas is external → survives restarts forever
#          → no FAISS files needed at all

#     MongoDB document structure per chunk:
#     {
#         "meeting_id":    "abc123",
#         "meeting_title": "Q3 Planning",
#         "user_id":       "user456",
#         "chunk_index":   0,
#         "text":          "SUMMARY: We discussed budget...",
#         "embedding":     [0.123, -0.456, ...]   ← 384-dim float list
#     }

#     Same function signature as before — analysis.py needs zero changes.

#     Returns:
#         Number of chunks embedded
#     """
#     logger.info("Embedding meeting %s into MongoDB", meeting_id)

#     try:
#         full_text = _build_indexable_text(meeting_id, transcript, report).strip()
#         chunks    = _chunk_text(full_text)

#         if not chunks:
#             logger.warning("No chunks generated for meeting %s", meeting_id)
#             return 0

#         # Generate embeddings
#         model      = get_embed_model()
#         embeddings = model.encode(chunks, batch_size=32, show_progress_bar=False)
#         embeddings = np.array(embeddings, dtype=np.float32)

#         if embeddings.ndim != 2:
#             raise ValueError("Unexpected embeddings shape")

#         db = get_db()

#         # ── Delete old chunks for this meeting (handles re-analysis) ──
#         db.meeting_chunks.delete_many({"meeting_id": meeting_id})

#         # ── Insert new chunks ──────────────────────────────────────────
#         docs = []
#         for i, (chunk, vector) in enumerate(zip(chunks, embeddings)):
#             docs.append({
#                 "meeting_id":    meeting_id,
#                 "meeting_title": meeting_title,
#                 "user_id":       user_id,
#                 "chunk_index":   i,
#                 "text":          chunk,
#                 "embedding":     vector.tolist(),   # store as plain list in MongoDB
#             })

#         if docs:
#             db.meeting_chunks.insert_many(docs)

#         logger.info("Embedded %d chunks for meeting %s into MongoDB", len(chunks), meeting_id)
#         return len(chunks)

#     except Exception:
#         logger.error("Embedding failed for meeting %s", meeting_id, exc_info=True)
#         return 0


# def remove_meeting_from_index(meeting_id: str) -> None:
#     """
#     Remove all chunks for a deleted meeting from MongoDB.

#     WHAT CHANGED vs old version:
#     ────────────────────────────
#     Old: had to rebuild entire FAISS index from scratch (slow, expensive)
#     New: single MongoDB delete_many — instant, no rebuilding needed
#     """
#     db = get_db()
#     result = db.meeting_chunks.delete_many({"meeting_id": meeting_id})
#     logger.info(
#         "Removed %d chunks for meeting %s from MongoDB",
#         result.deleted_count,
#         meeting_id,
#     )