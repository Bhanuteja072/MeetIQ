import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
})

// ── Meetings ──────────────────────────────────────────────
export const getAllMeetings = () =>
  api.get('/meetings/').then(r => r.data)

export const getMeeting = (id) =>
  api.get(`/meetings/${id}`).then(r => r.data)

export const deleteMeeting = (id) =>
  api.delete(`/meetings/${id}`).then(r => r.data)

export const renameSpeaker = (meetingId, speakerId, newName) =>
  api.patch(`/meetings/${meetingId}/rename-speaker`, null, {
    params: { speaker_id: speakerId, new_name: newName }
  }).then(r => r.data)

// ── Transcription ─────────────────────────────────────────
export const uploadAudio = (file, title, onProgress) => {
  const form = new FormData()
  form.append('file', file)
  form.append('title', title)
  return api.post('/transcription/upload-audio', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: e => onProgress && onProgress(
      Math.round((e.loaded * 100) / e.total)
    )
  }).then(r => r.data)
}

export const uploadTranscript = (file, title) => {
  const form = new FormData()
  form.append('file', file)
  form.append('title', title)
  return api.post('/transcription/upload-transcript', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }).then(r => r.data)
}

export const getTranscriptionStatus = (id) =>
  api.get(`/transcription/status/${id}`).then(r => r.data)

// ── Analysis ──────────────────────────────────────────────
export const triggerAnalysis = (id) =>
  api.post(`/analysis/${id}/analyze`).then(r => r.data)

export const getReport = (id) =>
  api.get(`/analysis/${id}/report`).then(r => r.data)

// ── Search ────────────────────────────────────────────────
export const searchMeetings = (query, meetingId = null) =>
  api.post('/search/', { query, meeting_id: meetingId }).then(r => r.data)

export const searchWithinMeeting = (meetingId, query) =>
  api.get(`/search/meetings/${meetingId}/search`, { params: { q: query } }).then(r => r.data)