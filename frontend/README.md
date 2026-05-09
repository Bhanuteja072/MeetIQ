# MeetIQ Frontend

This folder contains the frontend application for MeetIQ, built with React and Vite.

It provides the user interface for:

- Uploading meeting audio, video, or transcript files
- Monitoring transcription and analysis progress
- Reading generated AI meeting reports
- Searching insights across all meetings or within one specific meeting

## Tech Stack

- React 19
- Vite 8
- React Router 7
- Axios
- React Hot Toast
- Lucide React

## Features

- Drag-and-drop upload for audio/video and transcript files
- Upload progress indicator for audio/video uploads
- Meeting archive with live status refresh
- Meeting detail with three tabs:
	- Report
	- Transcript
	- Meeting-scoped Search
- Inline speaker rename support
- Global search page with two modes:
	- Global (all meetings)
	- Specific meeting

## Routes

| Route | Page | Purpose |
| --- | --- | --- |
| / | Upload | Upload and start processing a new meeting |
| /archive | Archive | View all meetings and current status |
| /meetings/:id | Meeting Detail | View transcript, report, and scoped search |
| /search | Search | Global or meeting-specific semantic search |
| * | NotFound | Fallback route for invalid paths |

## Project Structure

```text
frontend/
	src/
		api/
			client.js
		components/
			Navbar.jsx
			StatusBadge.jsx
		pages/
			Upload.jsx
			Archive.jsx
			MeetingDetail.jsx
			Search.jsx
			NotFound.jsx
		App.jsx
		main.jsx
		index.css
```

## API Integration

The frontend uses a single Axios client in src/api/client.js with:

- baseURL: /api
- timeout: 30000

Vite proxy in vite.config.js rewrites /api requests to the backend:

- /api/* -> http://localhost:8000/*

### API Calls Used by the UI

- Meetings
	- GET /meetings/
	- GET /meetings/{id}
	- DELETE /meetings/{id}
	- PATCH /meetings/{id}/rename-speaker
- Transcription
	- POST /transcription/upload-audio
	- POST /transcription/upload-transcript
	- GET /transcription/status/{id}
- Analysis
	- POST /analysis/{id}/analyze
	- GET /analysis/{id}/report
- Search
	- POST /search/
	- GET /search/meetings/{meeting_id}/search?q=...

## Local Development

From this frontend directory:

```bash
npm install
npm run dev
```

App URL:

- http://localhost:5173

Required backend URL (for dev proxy target):

- http://localhost:8000

## Available Scripts

```bash
npm run dev      # Start dev server
npm run build    # Create production build
npm run preview  # Preview production build
npm run lint     # Run ESLint
```

## Important Notes

- Frontend currently blocks files larger than 100 MB on upload.
- Backend default max file size can be higher (configured separately).
- Meeting IDs are normalized for scoped search to avoid whitespace issues.
- Archive auto-refreshes periodically to show processing updates.

## Backend Dependency

This frontend depends on the FastAPI backend in the project root.

For full backend setup, environment variables, and architecture details, see:

- ../README.md
