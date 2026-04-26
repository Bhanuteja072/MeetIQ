# ── Stage 1: Build React frontend ─────────────────────────
FROM node:18-slim AS frontend-builder

WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# ── Stage 2: Python backend ────────────────────────────────
FROM python:3.11-slim

# System packages needed by whisper, pyannote, moviepy
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsndfile1 \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python deps first (cached layer)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all backend code
COPY . .

# Copy built frontend into backend
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Create directories
RUN mkdir -p /tmp/uploads /tmp/faiss_store

# Railway sets PORT automatically
ENV PORT=8000

CMD uvicorn main:app --host 0.0.0.0 --port ${PORT}