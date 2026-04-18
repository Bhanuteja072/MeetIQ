# MeetIQ

MeetIQ is a full-stack meeting intelligence platform that helps you:

- Upload audio, video, or transcript files
- Transcribe and diarize speakers
- Generate AI meeting reports (summary, action items, decisions, blockers)
- Search globally across meetings or inside one specific meeting

The project includes:

- A FastAPI backend (MongoDB + Whisper + Pyannote + LangGraph + FAISS)
- A React frontend (Vite + React Router + Axios)

## What This Project Does

1. Upload meeting files
2. Process transcription in background
3. Detect speakers and merge transcript segments
4. Run AI analysis pipeline (on demand)
5. Embed analyzed content for semantic search
6. Answer user questions with RAG

## Features

- Audio/video upload with background processing
- Transcript file upload (TXT/PDF) with immediate parsing
- Whisper transcription with timestamps
- Pyannote speaker diarization
- Speaker rename support
- Multi-agent report generation via LangGraph
- Semantic search:
	- Global (all meetings)
	- Meeting-scoped (single meeting)
- FAISS vector index persistence
- Meeting archive with delete support
- Health endpoint and Swagger docs

## Tech Stack

### Backend

- FastAPI + Uvicorn
- MongoDB (motor/pymongo)
- Whisper
- Pyannote
- LangGraph + LangChain + Groq
- SentenceTransformers + FAISS
- MoviePy (MP4 audio extraction)

### Frontend

- React
- Vite
- React Router
- Axios
- React Hot Toast
- Lucide React icons

## Project Structure

```text
Meeting_Patner/
	backend/
		databases/
			mongo.py
		models/
			meeting.py
			report.py
		routers/
			transcription.py
			meetings.py
			analysis.py
			search.py
		services/
			whisper_service.py
			speaker_service.py
			file_service.py
			agents/
				summary_agent.py
				action_item_agent.py
				decision_agent.py
				blocker_agent.py
			graph/
				state.py
				pipeline.py
			rag/
				embeddings.py
				search.py
	frontend/
		src/
			api/client.js
			pages/
				Upload.jsx
				Archive.jsx
				MeetingDetail.jsx
				Search.jsx
	faiss_store/
		meetings.index
		metadata.json
	uploads/
	main.py
	config.py
	requirements.txt
```

## Prerequisites

- Python 3.10+
- Node.js 18+
- MongoDB running locally (or reachable via URI)

## Environment Variables

Create a .env file in the project root:

```env
MONGO_URL=mongodb://localhost:27017
DATABASE_NAME=Meeting_Partner
HUGGINGFACE_TOKEN=your_huggingface_token
GROQ_API_KEY=your_groq_api_key
UPLOAD_DIR=uploads
MAX_FILE_SIZE_MB=200
```

Notes:

- HUGGINGFACE_TOKEN is required for pyannote diarization (audio/video pipeline).
- GROQ_API_KEY is required for analysis and RAG search.

## Local Setup

### 1) Backend Setup

```bash
python -m venv myvenv
myvenv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Backend URLs:

- API root: http://127.0.0.1:8000/
- Swagger: http://127.0.0.1:8000/docs
- Health: http://127.0.0.1:8000/health

### 2) Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend URL:

- http://localhost:5173

Vite dev server proxies /api requests to http://localhost:8000.

## Frontend Routes

- / : Upload page (audio/video or transcript)
- /archive : Meeting archive list
- /meetings/:id : Meeting details (report/transcript/search tabs)
- /search : Global search page + specific search mode

## Backend API Endpoints

### Transcription

- POST /transcription/upload-audio
	- Accepts MP3, WAV, MP4, M4A
	- Creates meeting and starts background transcription
- POST /transcription/upload-transcript
	- Accepts TXT, PDF
	- Parses and stores immediately
- GET /transcription/status/{meeting_id}
	- Returns transcription status and segment counts

### Meetings

- GET /meetings/
- GET /meetings/{meeting_id}
- PATCH /meetings/{meeting_id}/rename-speaker
- DELETE /meetings/{meeting_id}

### Analysis

- POST /analysis/{meeting_id}/analyze
	- Requires meeting status = completed
	- Runs in background
- GET /analysis/{meeting_id}/report
	- Returns analyzing/failed/completed report state

### Search

- POST /search/
	- Global semantic search (optionally filtered by meeting_id)
- GET /search/meetings/{meeting_id}/search?q=...
	- Search within one meeting

## End-to-End Flow

1. User uploads file from frontend.
2. Backend stores file and creates meeting document.
3. Audio/video path:
	 - Whisper transcription
	 - Pyannote diarization
	 - Speaker extraction and segment merge
4. User triggers analysis.
5. LangGraph pipeline runs agents:
	 - Summary
	 - Action items
	 - Decisions
	 - Blockers
6. Backend saves report and embeds meeting content into FAISS.
7. Search queries retrieve relevant chunks and LLM returns grounded answer.

## Data Persistence

- MongoDB stores meetings, transcripts, speakers, statuses, reports.
- uploads stores raw uploaded files.
- faiss_store stores vector index and metadata for semantic retrieval.

## Commands Reference

### Backend

```bash
uvicorn main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm run dev
npm run build
npm run preview
npm run lint
```

## API Examples

### Upload Audio

```bash
curl -X POST "http://127.0.0.1:8000/transcription/upload-audio?title=MyMeeting" \
	-F "file=@sample.wav"
```

### Trigger Analysis

```bash
curl -X POST "http://127.0.0.1:8000/analysis/<meeting_id>/analyze"
```

### Search Within Meeting

```bash
curl "http://127.0.0.1:8000/search/meetings/<meeting_id>/search?q=What decisions were made"
```

## Troubleshooting

### 1) No relevant meeting data found

If search returns:

No relevant meeting data found. Make sure meetings have been analyzed first.

Check:

1. Analysis actually completed for that meeting.
2. Report exists in MongoDB meeting document.
3. Meeting chunks were embedded into faiss_store/metadata.json.
4. Query is targeting the correct meeting ID.

### 2) Meeting-specific search returns not found

Make sure meeting ID has no extra spaces. This project now trims meeting IDs in both frontend and backend search flow.

### 3) Diarization fails

Verify HUGGINGFACE_TOKEN is valid and has access to pyannote models.

### 4) Analysis/search fails

Verify GROQ_API_KEY is configured.

### 5) MP4 upload fails

Ensure the MP4 file has an audio track.

### 6) Frontend upload blocked at 50MB

Current frontend validation blocks files larger than 50MB in Upload page, while backend allows up to MAX_FILE_SIZE_MB (default 200).

## Notes for Development

- Models are loaded lazily and cached in process.
- First transcription/diarization request is typically slower.
- Analysis and transcription run in background tasks; frontend uses polling for status updates.
- CORS is enabled for localhost:3000 and localhost:5173.

## License

Add your license information here.
