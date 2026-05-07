import logging
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from typing import List, Dict, Any, Optional
from config import settings
from backend.databases.mongo import get_db
from backend.services.rag.embeddings import (
    get_embeddings
)

logger = logging.getLogger(__name__)

TOP_K = 5  # Number of chunks to retrieve per query


# ── Retrieval ──────────────────────────────────────────────

async def retrieve_relevant_chunks(query: str, meeting_id: str = None, user_id: str = None, top_k: int = TOP_K) -> List[Dict[str, Any]]:
    """
    Embed query with Nomic and search MongoDB Atlas Vector Search.
    """
    db = get_db()
    # Use search_query task type for better retrieval quality
    embeddings = await get_embeddings([query])
    query_vector = embeddings[0]
    vector_search: Dict[str, Any] = {
        "index": "vector_index",
        "path": "embedding",
        "queryVector": query_vector,
        "numCandidates": 200,
        "limit": top_k * 5,
    }
        # Add filters if needed
    filters = {}
    if meeting_id:
        filters["meeting_id"] = meeting_id
    if user_id:
        filters["user_id"] = user_id
    if filters:
        vector_search["filter"] = filters


    pipeline = [
        {"$vectorSearch": vector_search},
        {"$project": {
            "_id": 0,
            "score": {"$meta": "vectorSearchScore"},
            "text": 1,
            "meeting_id": 1,
            "meeting_title": 1,
            "user_id": 1,
            "type": 1,
        }},
        {"$limit": top_k}
    ]
    try:
        cursor = db.chunks.aggregate(pipeline)
        results = await cursor.to_list(length=top_k)
        logger.info("Vector search returned %d chunks for meeting_id=%s", len(results), meeting_id)
        return results
    except Exception:
        logger.error("Vector search failed", exc_info=True)
    # ── Fallback: if vector search returned nothing (small meeting / few chunks)
    # just fetch ALL chunks for this meeting directly — no similarity needed
    logger.warning(
        "Vector search returned 0 results for meeting_id=%s — "
        "falling back to direct chunk fetch", meeting_id
    )
    return await _fallback_fetch_chunks(meeting_id=meeting_id, user_id=user_id, top_k=top_k)


async def _fallback_fetch_chunks(
    meeting_id: str = None,
    user_id: str = None,
    top_k: int = TOP_K,
) -> List[Dict[str, Any]]:
    """
    Direct MongoDB fetch — no vector similarity.
    Used when the meeting is too small to score well in Atlas Vector Search.
    Fetches all chunks for the meeting and returns them — the LLM will
    figure out the answer from the full context.
    """
    db = get_db()
    query_filter = {}
    if meeting_id:
        query_filter["meeting_id"] = meeting_id
    if user_id:
        query_filter["user_id"] = user_id

    try:
        # For small meetings, just return ALL chunks (not limited to top_k)
        # so the LLM has the full context to work with
        cursor = db.chunks.find(
            query_filter,
            {
                "_id": 0,
                "text": 1,
                "meeting_id": 1,
                "meeting_title": 1,
                "user_id": 1,
                "type": 1,
            }
        ).limit(50)  # safety cap — 50 chunks is plenty even for large meetings
        results = await cursor.to_list(length=50)
        logger.info(
            "Fallback fetch returned %d chunks for meeting_id=%s",
            len(results), meeting_id
        )
        return results
    except Exception:
        logger.error("Fallback chunk fetch failed", exc_info=True)
        return []



RAG_PROMPT = """You are an intelligent meeting assistant with access to past meeting records.
Answer the user's question based ONLY on the meeting context provided below.

If the answer is not found in the context, say "I couldn't find that in the meeting records."
Be specific and cite which meeting the information came from when possible.

MEETING CONTEXT:
{context}

USER QUESTION:
{question}

Answer clearly and concisely:"""


async def answer_query(query: str, meeting_id: str = None, user_id: str = None) -> dict:
    """
    Full RAG pipeline using Atlas Vector Search.
    Same interface as before — routers need zero changes.
    """
    # Step 1: Retrieve
    if not query.strip():
        return {
        "answer": "Please provide a valid question.",
        "sources": [],
        "chunks_used": 0
        }
    chunks = await retrieve_relevant_chunks(query, meeting_id=meeting_id,user_id=user_id)

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

        response = await chain.ainvoke({"context": context, "question": query})
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