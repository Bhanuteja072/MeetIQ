# ── Stage 1: Build React frontend ─────────────────────────
FROM node:22-slim AS frontend-builder

WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# ── Stage 2: Python backend ────────────────────────────────
FROM python:3.11-slim

# ffmpeg needed for moviepy (MP4 extraction)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Copy built frontend
COPY --from=frontend-builder /app/frontend/dist /app/frontend/dist

# Create temp directories
RUN mkdir -p /tmp/uploads /tmp/faiss_store

ENV PORT=8000

CMD uvicorn main:app --host 0.0.0.0 --port ${PORT}