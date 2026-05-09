import { useState } from 'react'
import { Link } from 'react-router-dom'
import { searchMeetings, searchWithinMeeting } from '../api/client'
import toast from 'react-hot-toast'
import { Search as SearchIcon } from 'lucide-react'

const EXAMPLES = [
  'What decisions were made about the drain?',
  'What are all unresolved blockers?',
  'What action items were assigned?',
  'What bylaws were approved?',
]

export default function Search() {
  const [query, setQuery] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)

  // 🔥 NEW
  const [mode, setMode] = useState('global') // 'global' | 'meeting'
  const [meetingId, setMeetingId] = useState('')

  const normalizeMeetingId = (value = '') =>
    value.trim().replace(/^id:\s*/i, '')

  const handleSearch = async (q = query) => {
    const normalizedQuery = q.trim()
    if (!normalizedQuery) return

    const normalizedMeetingId = normalizeMeetingId(meetingId)

    setQuery(normalizedQuery)
    setLoading(true)
    setResult(null)

    try {
      let data

      if (mode === 'meeting') {
        if (!normalizedMeetingId) {
          toast.error('Please enter a meeting ID')
          setLoading(false)
          return
        }
        data = await searchWithinMeeting(normalizedMeetingId, normalizedQuery)
      } else {
        data = await searchMeetings(normalizedQuery)
      }

      setResult(data)
    } catch {
      toast.error('Search failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ maxWidth: 680, margin: '0 auto' }}>
      <h1 style={{ color: '#f1f5f9', fontSize: 28, fontWeight: 700, marginBottom: 8 }}>
        Search Meetings
      </h1>

      {/* 🔥 Mode Toggle */}
      <div style={{ display: 'flex', gap: 8, marginBottom: 12 }}>
        <button onClick={() => setMode('global')} style={{
          background: mode === 'global' ? '#6366f1' : '#1e293b',
          color: '#fff', padding: '10px 16px', minHeight: 44, borderRadius: 8, border: 'none'
        }}>
          Global
        </button>

        <button onClick={() => setMode('meeting')} style={{
          background: mode === 'meeting' ? '#6366f1' : '#1e293b',
          color: '#fff', padding: '10px 16px', minHeight: 44, borderRadius: 8, border: 'none'
        }}>
          Specific Meeting
        </button>
      </div>

      {/* 🔥 Meeting ID input */}
      {mode === 'meeting' && (
        <input
          value={meetingId}
          onChange={e => setMeetingId(e.target.value)}
          onBlur={e => setMeetingId(normalizeMeetingId(e.target.value))}
          placeholder="Enter Meeting ID..."
          style={{
            width: '100%',
            marginBottom: 12,
            padding: '8px 12px',
            borderRadius: 8,
            background: '#1e293b',
            border: '1px solid #334155',
            color: '#f1f5f9'
          }}
        />
      )}

      {/* Search input */}
      <div style={{ display: 'flex', gap: 8, marginBottom: 20 }}>
        <input
          value={query}
          onChange={e => setQuery(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && handleSearch()}
          placeholder="What did we decide about...?"
          style={{
            flex: 1, padding: '12px 16px', borderRadius: 12,
            background: '#1e293b', border: '1px solid #334155',
            color: '#f1f5f9', fontSize: 15, outline: 'none'
          }}
        />
        <button onClick={() => handleSearch()} disabled={loading} style={{
          background: loading ? '#334155' : '#6366f1',
          color: '#fff', border: 'none', padding: '12px 20px',
          borderRadius: 12, cursor: loading ? 'not-allowed' : 'pointer',
          fontWeight: 600
        }}>
          <SearchIcon size={18} />
        </button>
      </div>

      {!result && (
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, marginBottom: 32 }}>
          {EXAMPLES.map(ex => (
            <button key={ex} onClick={() => handleSearch(ex)} style={{
              background: '#1e293b', border: '1px solid #334155',
              color: '#64748b', borderRadius: 999, padding: '6px 14px',
              fontSize: 13, maxWidth: '100%',cursor: 'pointer'
            }}>
              {ex}
            </button>
          ))}
        </div>
      )}

      {loading && <p style={{ color: '#6366f1' }}>Searching...</p>}

      {result && (
        <div>
          <div style={{
            background: '#1e293b', borderRadius: 12, padding: 20,
            marginBottom: 16, border: '1px solid #334155'
          }}>
            <p style={{ color: '#94a3b8', fontSize: 12, fontWeight: 700,
              textTransform: 'uppercase', marginBottom: 12 }}>
              Answer
            </p>
            <p style={{ color: '#f1f5f9' }}>{result.answer}</p>
          </div>

          {result.sources?.length > 0 && (
            <div>
              <p style={{ color: '#475569', fontSize: 13, marginBottom: 10 }}>
                Sources ({result.chunks_used})
              </p>
              {[...new Map(result.sources.map(s => [s.meeting_id, s])).values()].map(s => (
                <Link key={s.meeting_id} to={`/meetings/${s.meeting_id}`} style={{
                  display: 'block', background: '#1e293b', borderRadius: 8,
                  padding: '10px 14px', marginBottom: 8,
                  textDecoration: 'none', border: '1px solid #334155',
                  color: '#6366f1'
                }}>
                  📄 {s.meeting_title || s.meeting_id} →
                </Link>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}