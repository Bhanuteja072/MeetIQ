from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from backend.databases.mongo import connect_db, close_db,get_db
from backend.routers import meetings, transcription, analysis, search, auth
import logging
import os
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
logging.basicConfig(level=logging.INFO)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await connect_db()
    # ── Recover stuck meetings from previous crash ──
    try:
        db = get_db()
        if db is not None:
            result = await db.meetings.update_many(
                {"status": "transcribing"},
                {"$set": {
                    "status": "failed",
                    "error": "Server restarted during processing — please re-upload"
                }}
            )
            if result.modified_count > 0:
                logging.warning(
                    "Recovered %d stuck meetings on startup",
                    result.modified_count
                )
    except Exception as e:
        logging.error("Startup recovery failed: %s", e)
    
    yield
    # Shutdown
    await close_db()

app = FastAPI(
    title="Meeting Intelligence API",
    description="AI-powered meeting analysis platform",
    version="1.0.0",
    lifespan=lifespan
)

# Allow React frontend to call this API later
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:8000","http://localhost:5173","*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth.router,prefix="/api")
app.include_router(meetings.router,prefix="/api")
app.include_router(transcription.router,prefix="/api")
app.include_router(analysis.router,prefix="/api")
app.include_router(search.router,prefix="/api")
# Register routers
# app.include_router(auth.router,)
# app.include_router(meetings.router)
# app.include_router(transcription.router)
# app.include_router(analysis.router)
# app.include_router(search.router)
@app.get("/")
async def root():
    return {
        "message": "Meeting Intelligence API is running",
        "docs": "/docs"
    }

@app.get("/health")
async def health():
        
        db = get_db()
        if db is None:
            return {"status": "unhealthy", "db": "disconnected"}
        return {"status": "healthy", "db": "connected"}


# ── Serve React frontend ──────────────────────────────────
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "frontend", "dist")

if os.path.exists(FRONTEND_DIR):
    app.mount("/assets", StaticFiles(directory=f"{FRONTEND_DIR}/assets"), name="assets")

    @app.get("/")
    async def serve_root():
        return FileResponse(f"{FRONTEND_DIR}/index.html")

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        file_path = os.path.join(FRONTEND_DIR, full_path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(f"{FRONTEND_DIR}/index.html")
