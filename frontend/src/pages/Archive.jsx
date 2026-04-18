import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { getAllMeetings, deleteMeeting } from '../api/client'
import StatusBadge from '../components/StatusBadge'
import toast from 'react-hot-toast'
import { Trash2, ChevronRight, Clock } from 'lucide-react'

export default function Archive() {
  const [meetings, setMeetings] = useState([])
  const [loading, setLoading] = useState(true)

  const load = async () => {
    try {
      const data = await getAllMeetings()

      // Sort latest first (optional but recommended)
      const sorted = (data.meetings || []).sort(
        (a, b) => new Date(b.created_at) - new Date(a.created_at)
      )

      setMeetings(sorted)
    } catch {
      toast.error('Failed to load meetings')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()

    // Auto-refresh every 5s (important for processing status)
    const interval = setInterval(load, 5000)
    return () => clearInterval(interval)
  }, [])

  const handleDelete = async (e, id) => {
    e.preventDefault()

    if (!confirm('Delete this meeting?')) return

    try {
      await deleteMeeting(id)

      // FIX: use _id instead of id
      setMeetings(m => m.filter(x => x.id !== id))

      toast.success('Meeting deleted')
    } catch {
      toast.error('Delete failed')
    }
  }

  const fmtDuration = (secs) => {
    if (!secs) return '—'
    const m = Math.floor(secs / 60)
    const s = Math.floor(secs % 60)
    return `${m}m ${s}s`
  }

  if (loading) {
    return <p style={{ color: '#64748b' }}>Loading meetings...</p>
  }

  return (
    <div>
      <h1 style={{ color: '#f1f5f9', fontSize: 28, fontWeight: 700, marginBottom: 24 }}>
        Meeting Archive
      </h1>

      {meetings.length === 0 ? (
        <div style={{
          textAlign: 'center',
          padding: '64px 0',
          color: '#475569'
        }}>
          <p style={{ fontSize: 18, marginBottom: 8 }}>No meetings yet</p>
          <Link to="/" style={{ color: '#6366f1' }}>
            Upload your first meeting →
          </Link>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          {meetings.map(m => (
            <Link
              key={m.id}   // FIXED
              to={`/meetings/${m.id}`}   // FIXED
              style={{
                display: 'flex',
                alignItems: 'center',
                background: '#1e293b',
                borderRadius: 12,
                padding: '16px 20px',
                textDecoration: 'none',
                border: '1px solid #334155',
                transition: 'border-color 0.15s'
              }}
            >
              <div style={{ flex: 1 }}>
                <p style={{
                  color: '#f1f5f9',
                  fontWeight: 600,
                  marginBottom: 4
                }}>
                  {m.title}
                </p>

                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 12
                }}>
                  <StatusBadge status={m.status} />

                  <span style={{
                    color: '#475569',
                    fontSize: 13,
                    display: 'flex',
                    alignItems: 'center',
                    gap: 4
                  }}>
                    <Clock size={12} />
                    {fmtDuration(m.duration || 0)}
                  </span>

                  <span style={{ color: '#475569', fontSize: 13 }}>
                    {m.speakers?.length || 0} speakers
                  </span>
                </div>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                <button
                  onClick={(e) => handleDelete(e, m.id)} // FIXED
                  style={{
                    background: 'none',
                    border: 'none',
                    cursor: 'pointer',
                    color: '#ef4444',
                    padding: 4
                  }}
                >
                  <Trash2 size={16} />
                </button>

                <ChevronRight size={18} color="#475569" />
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}