from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from backend.databases.mongo import connect_db, close_db,get_db
from backend.routers import meetings, transcription, analysis
import logging
logging.basicConfig(level=logging.INFO)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await connect_db()
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
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(meetings.router)
app.include_router(transcription.router)
app.include_router(analysis.router)

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