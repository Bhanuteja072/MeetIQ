## Meeting Intelligence API

AI-powered meeting transcription and speaker diarization API built with FastAPI. Upload audio or video, get a structured transcript with speaker labels, and manage meeting records in MongoDB.

### Features
- Audio + video upload and background transcription
- Whisper-based speech-to-text with timestamps
- Pyannote-based speaker diarization
- Speaker summaries and transcript merging
- MongoDB persistence for meetings
- REST API with Swagger UI

### Tech Stack
- FastAPI + Uvicorn
- MongoDB (motor + pymongo)
- Whisper (OpenAI)
- Pyannote (speaker diarization)
- MoviePy (extract audio from MP4)

### Project Structure
```
main.py
config.py
backend/
	routers/
		meetings.py
		transcription.py
	services/
		whisper_service.py
		speaker_service.py
		file_service.py
	databases/
		mongo.py
uploads/
```

### Setup
1. Create and activate a virtual environment.
2. Install dependencies:
	 ```bash
	 pip install -r requirements.txt
	 ```
3. Create a `.env` file (optional, defaults shown below).

### Environment Variables
```env
MONGO_URL=mongodb://localhost:27017
DATABASE_NAME=Meeting_Partner
HUGGINGFACE_TOKEN=your_hf_token_here
UPLOAD_DIR=uploads
MAX_FILE_SIZE_MB=100
```

### Run the API
```bash
uvicorn main:app --reload --port 8000
```

Open Swagger UI:
```
http://127.0.0.1:8000/docs
```

### Core Flow
#### Upload Audio (MP3/WAV/M4A)
1. File is saved to `uploads/`.
2. Whisper transcribes the audio.
3. Pyannote diarizes speakers.
4. Results saved to MongoDB.

#### Upload Video (MP4)
1. File is saved to `uploads/`.
2. MoviePy extracts audio to WAV.
3. Whisper transcribes the extracted audio.
4. Pyannote diarizes speakers.
5. Results saved to MongoDB.

Note: MP4 files must include an audio track.

### API Endpoints
#### Transcription
- `POST /transcription/upload-audio`
	- Upload audio or MP4 video. Starts background processing.
- `POST /transcription/upload-transcript`
	- Upload TXT/PDF transcript. Parses and stores immediately.
- `GET /transcription/status/{meeting_id}`
	- Check processing status.

#### Meetings
- `GET /meetings/`
	- List all meetings.
- `GET /meetings/{meeting_id}`
	- Get full meeting details.
- `PATCH /meetings/{meeting_id}/rename-speaker`
	- Rename a speaker across transcript.
- `DELETE /meetings/{meeting_id}`
	- Delete a meeting.

### Example: Upload Audio
```bash
curl -X POST "http://127.0.0.1:8000/transcription/upload-audio?title=MyMeet" \
	-F "file=@sample.wav"
```

### Common Notes
- Whisper and Pyannote models load once per server process and are reused for later requests.
- First request may take longer due to model download and initialization.
- MP4 uploads trigger audio extraction via MoviePy.

### Troubleshooting
- If diarization fails, confirm `HUGGINGFACE_TOKEN` is set and has access.
- If MP4 upload fails, ensure the file has an audio track.
- If MongoDB is not running, the API will report a database error.
