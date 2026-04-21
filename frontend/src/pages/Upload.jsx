import { useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import { uploadAudio, uploadTranscript } from '../api/client'
import { Upload as UploadIcon, FileAudio, FileText } from 'lucide-react'

export default function Upload() {
  const [title, setTitle] = useState('')
  const [file, setFile] = useState(null)
  const [mode, setMode] = useState('audio')  // 'audio' | 'transcript'
  const [progress, setProgress] = useState(0)
  const [loading, setLoading] = useState(false)
  const [dragOver, setDragOver] = useState(false)
  const fileRef = useRef()
  const navigate = useNavigate()

  const handleFile = (f) => {
    if (!f) return
    setFile(f)
    if (!title) setTitle(f.name.replace(/\.[^.]+$/, ''))
  }

  const handleDrop = (e) => {
    e.preventDefault()
    setDragOver(false)
    handleFile(e.dataTransfer.files[0])
  }

  const handleSubmit = async () => {
    if (!file) return toast.error('Please select a file')
    if (!title.trim()) return toast.error('Please enter a title')
    if (file.size > 100 * 1024 * 1024) {
    return toast.error('File too large (max 50MB)')
    }

    setLoading(true)
    setProgress(0)

    try {
      let result
      if (mode === 'audio') {
        result = await uploadAudio(file, title, setProgress)
        toast.success('Upload successful! Transcription started.')
      } else {
        result = await uploadTranscript(file, title)
        toast.success('Transcript uploaded and processed!')
      }
      navigate(`/meetings/${result.meeting_id}`)
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Upload failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ maxWidth: 560, margin: '0 auto' }}>
      <h1 style={{ color: '#f1f5f9', fontSize: 28, fontWeight: 700, marginBottom: 8 }}>
        New Meeting
      </h1>
      <p style={{ color: '#64748b', marginBottom: 32 }}>
        Upload a recording or transcript to get AI-powered insights
      </p>

      {/* Mode toggle */}
      <div style={{ display: 'flex', gap: 8, marginBottom: 24 }}>
        {[['audio', 'Audio / Video', FileAudio], ['transcript', 'Transcript', FileText]].map(
          ([val, label, Icon]) => (
            <button key={val} onClick={() => setMode(val)} style={{
              flex: 1, padding: '10px 0', borderRadius: 10, border: 'none',
              cursor: 'pointer', display: 'flex', alignItems: 'center',
              justifyContent: 'center', gap: 6, fontWeight: 600, fontSize: 14,
              background: mode === val ? '#6366f1' : '#1e293b',
              color: mode === val ? '#fff' : '#64748b',
            }}>
              <Icon size={15} /> {label}
            </button>
          )
        )}
      </div>

      {/* Title input */}
      <input
        value={title}
        onChange={e => setTitle(e.target.value)}
        placeholder="Meeting title"
        style={{
          width: '100%', padding: '10px 14px', borderRadius: 10,
          background: '#1e293b', border: '1px solid #334155',
          color: '#f1f5f9', fontSize: 15, marginBottom: 16,
          outline: 'none', boxSizing: 'border-box'
        }}
      />

      {/* Drop zone */}
      <div
        onClick={() => fileRef.current.click()}
        onDragOver={e => { e.preventDefault(); setDragOver(true) }}
        onDragLeave={() => setDragOver(false)}
        onDrop={handleDrop}
        style={{
          border: `2px dashed ${dragOver ? '#6366f1' : '#334155'}`,
          borderRadius: 14, padding: '48px 24px', textAlign: 'center',
          cursor: 'pointer', marginBottom: 20,
          background: dragOver ? '#1e1b4b' : '#0f172a',
          transition: 'all 0.15s'
        }}
      >
        <UploadIcon size={32} color="#6366f1" style={{ marginBottom: 12 }} />
        {file ? (
          <p style={{ color: '#86efac', fontWeight: 600 }}>{file.name}</p>
        ) : (
          <>
            <p style={{ color: '#94a3b8', marginBottom: 4 }}>
              Drag & drop or click to browse
            </p>
            <p style={{ color: '#475569', fontSize: 13 }}>
              {mode === 'audio' ? 'MP3, WAV, MP4, M4A' : 'TXT, PDF'}
            </p>
          </>
        )}
        <input
          ref={fileRef}
          type="file"
          hidden
          accept={mode === 'audio' ? '.mp3,.wav,.mp4,.m4a' : '.txt,.pdf'}
          onChange={e => handleFile(e.target.files[0])}
        />
      </div>

      {/* Progress bar */}
      {loading && progress > 0 && (
        <div style={{
          background: '#1e293b', borderRadius: 999, height: 6, marginBottom: 16
        }}>
          <div style={{
            background: '#6366f1', height: 6, borderRadius: 999,
            width: `${progress}%`, transition: 'width 0.3s'
          }} />
        </div>
      )}

      <button
        onClick={handleSubmit}
        disabled={loading || !file}
        style={{
          width: '100%', padding: '12px 0', borderRadius: 10,
          background: loading || !file ? '#334155' : '#6366f1',
          color: '#fff', border: 'none', cursor: loading || !file ? 'not-allowed' : 'pointer',
          fontWeight: 700, fontSize: 16
        }}
      >
        {loading ? 'Uploading...' : 'Upload & Process'}
      </button>
    </div>
  )
}