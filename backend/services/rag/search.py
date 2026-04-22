import json
import logging
import os
import numpy as np
import faiss
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from config import settings
from backend.services.rag.embeddings import (
    get_embed_model,
    INDEX_FILE,
    METADATA_FILE,
)

logger = logging.getLogger(__name__)

TOP_K = 5  # Number of chunks to retrieve per query


# ── Retrieval ──────────────────────────────────────────────

def retrieve_relevant_chunks(query: str, meeting_id: str = None, user_id: str = None, top_k: int = TOP_K):
    """
    Embed the query and find the top_k most similar chunks in FAISS.

    Args:
        query: Natural language question from user
        meeting_id: If provided, restrict search to one meeting.
                    If None, search across ALL meetings (global RAG).
        top_k: Number of chunks to return

    Returns:
        List of metadata dicts for the top matching chunks
    """
    if not os.path.exists(INDEX_FILE) or not os.path.exists(METADATA_FILE):
        return []

    # Load index and metadata
    index = faiss.read_index(INDEX_FILE)
    with open(METADATA_FILE, "r") as f:
        try:
            metadata = json.load(f)
        except:
            logger.error("Metadata load failed", exc_info=True)
            return []

    if index.ntotal == 0:
        return []

    # Embed the query
    model = get_embed_model()
    query_embedding = model.encode([query], show_progress_bar=False)
    query_embedding = np.array(query_embedding, dtype=np.float32)

    # Search FAISS
    distances, indices = index.search(query_embedding, min(top_k * 10, index.ntotal))

    # Filter by meeting_id if specified, then take top_k
    results = []
    for dist, idx in zip(distances[0], indices[0]):
        if idx < 0 or idx >= len(metadata):
            continue
        chunk_meta = metadata[idx].copy()
        chunk_meta["score"] = float(dist)
        if user_id and chunk_meta.get("user_id") and chunk_meta["user_id"] != user_id:
            continue


        if meeting_id and chunk_meta["meeting_id"] != meeting_id:
            continue

        results.append(chunk_meta)

        if len(results) >= top_k:
            break

    return results


# ── Answer generation ──────────────────────────────────────

RAG_PROMPT = """You are an intelligent meeting assistant with access to past meeting records.
Answer the user's question based ONLY on the meeting context provided below.

If the answer is not found in the context, say "I couldn't find that in the meeting records."
Be specific and cite which meeting the information came from when possible.

MEETING CONTEXT:
{context}

USER QUESTION:
{question}

Answer clearly and concisely:"""


def answer_query(query: str, meeting_id: str = None, user_id: str = None) -> dict:
    """
    Full RAG pipeline:
    1. Retrieve relevant chunks from FAISS
    2. Build context from chunks
    3. Generate answer with LLM

    Args:
        query: User's natural language question
        meeting_id: Restrict to specific meeting or None for all meetings

    Returns:
        {
            "answer": str,
            "sources": [{"meeting_id", "meeting_title", "chunk_text"}],
            "chunks_used": int
        }
    """
    # Step 1: Retrieve
    if not query.strip():
        return {
        "answer": "Please provide a valid question.",
        "sources": [],
        "chunks_used": 0
        }
    chunks = retrieve_relevant_chunks(query, meeting_id=meeting_id,user_id=user_id)

    if not chunks:
        return {
            "answer": "No relevant meeting data found. Make sure meetings have been analyzed first.",
            "sources": [],
            "chunks_used": 0,
        }


    # Step 2: Build context
    context_parts = []
    sources = []

    for chunk in chunks:
        meeting_title = chunk.get("meeting_title", chunk["meeting_id"])
        context_parts.append(
            f"--- From meeting: '{meeting_title}' ---\n{chunk['text']}"
        )
        sources.append({
            "meeting_id": chunk["meeting_id"],
            "meeting_title": meeting_title,
            "chunk_text": chunk["text"][:200] + "..."  # preview only
        })

    context = "\n\n".join(context_parts)

    # Step 3: Generate answer
    llm = ChatGroq(
        api_key=settings.groq_api_key,
        model="llama-3.3-70b-versatile",
        temperature=0.2,
    )

    prompt = ChatPromptTemplate.from_template(RAG_PROMPT)
    chain = prompt | llm
    try:

        response = chain.invoke({"context": context, "question": query})
    except Exception as e:
        logger.error("LLM generation failed", exc_info=True)
        return {
            "answer": "Sorry, I had trouble generating an answer.",
            "sources": sources,
            "chunks_used": len(chunks),
        }

    return {
        "answer": response.content.strip(),
        "sources": sources,
        "chunks_used": len(chunks),
    }