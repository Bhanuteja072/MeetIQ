import { useState, useEffect, useCallback } from 'react'
import { useParams } from 'react-router-dom'
import {
  getMeeting, getReport, triggerAnalysis,
  getTranscriptionStatus, renameSpeaker
} from '../api/client'
import { searchWithinMeeting } from '../api/client'
import StatusBadge from '../components/StatusBadge'
import toast from 'react-hot-toast'
import { Zap, Search, RefreshCw, Edit2, Check, X } from 'lucide-react'

// ── Small sub-components ──────────────────────────────────

function Section({ title, children }) {
  return (
    <div style={{
      background: '#1e293b', borderRadius: 12, padding: 20,
      marginBottom: 16, border: '1px solid #334155'
    }}>
      <h3 style={{ color: '#94a3b8', fontSize: 12, fontWeight: 700,
        textTransform: 'uppercase', letterSpacing: 1, marginBottom: 14 }}>
        {title}
      </h3>
      {children}
    </div>
  )
}

function ActionItemCard({ item }) {
  const priorityColor = { high: '#ef4444', medium: '#f59e0b', low: '#22c55e' }
  return (
    <div style={{
      background: '#0f172a', borderRadius: 8, padding: '12px 14px',
      marginBottom: 8, borderLeft: `3px solid ${priorityColor[item.priority] || '#6366f1'}`
    }}>
      <p style={{ color: '#f1f5f9', marginBottom: 4 }}>{item.task}</p>
      <div style={{ display: 'flex', gap: 16, fontSize: 13, color: '#64748b' }}>
        {item.owner && <span>👤 {item.owner}</span>}
        {item.deadline && <span>📅 {item.deadline}</span>}
        {item.priority && <span style={{ color: priorityColor[item.priority] }}>
          ● {item.priority}
        </span>}
      </div>
    </div>
  )
}

function DecisionCard({ item }) {
  return (
    <div style={{
      background: '#0f172a', borderRadius: 8, padding: '12px 14px', marginBottom: 8
    }}>
      <p style={{ color: '#f1f5f9', marginBottom: 4 }}>✅ {item.decision}</p>
      {item.context && <p style={{ color: '#64748b', fontSize: 13 }}>{item.context}</p>}
      {item.made_by && <p style={{ color: '#6366f1', fontSize: 13 }}>— {item.made_by}</p>}
    </div>
  )
}

function BlockerCard({ item }) {
  const sevColor = { critical: '#ef4444', moderate: '#f59e0b', low: '#22c55e' }
  return (
    <div style={{
      background: '#0f172a', borderRadius: 8, padding: '12px 14px',
      marginBottom: 8, borderLeft: `3px solid ${sevColor[item.severity] || '#f59e0b'}`
    }}>
      <p style={{ color: '#f1f5f9', marginBottom: 4 }}>⚠️ {item.issue}</p>
      {item.raised_by && <p style={{ color: '#64748b', fontSize: 13 }}>
        Raised by: {item.raised_by}
      </p>}
    </div>
  )
}
function TranscriptionProgress({ seconds }) {
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  const timerStr = `${mins}:${String(secs).padStart(2, '0')}`

  const msgs = [
    'Sending audio to AssemblyAI...',
    'Transcription in progress...',
    'Detecting speaker voices...',
    'Finalizing...',
  ]
  const msgIdx = Math.min(Math.floor(seconds / 18), msgs.length - 1)

  return (
    <div style={{
      background: '#1e293b', border: '1px solid #334155',
      borderRadius: 12, padding: '28px 24px', maxWidth: 480
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 20 }}>
        <div style={{
          width: 10, height: 10, borderRadius: '50%', background: '#6366f1', flexShrink: 0,
          animation: 'meetiq-pulse 1.4s ease-in-out infinite'
        }} />
        <div>
          <p style={{ color: '#f1f5f9', fontWeight: 600, fontSize: 15, margin: 0 }}>
            Processing your meeting
          </p>
          <p style={{ color: '#64748b', fontSize: 13, margin: 0 }}>
            {msgs[msgIdx]}
          </p>
        </div>
      </div>

      <div style={{ display: 'flex', alignItems: 'baseline', gap: 6, marginBottom: 20 }}>
        <span style={{
          color: '#a78bfa', fontSize: 28, fontWeight: 700, fontVariantNumeric: 'tabular-nums'
        }}>
          {timerStr}
        </span>
        <span style={{ color: '#475569', fontSize: 13 }}>elapsed</span>
      </div>

      {/* Steps */}
      {[
        { label: 'Upload received', desc: 'File saved to server', state: 'done' },
        { label: 'Transcribing & identifying speakers', desc: msgs[msgIdx], state: 'active' },
        { label: 'Ready for AI analysis', desc: 'Run once transcription completes', state: 'waiting' },
      ].map((step, i) => (
        <div key={i} style={{
          display: 'flex', alignItems: 'flex-start', gap: 12,
          padding: '8px 0',
          borderBottom: i < 2 ? '1px solid #1a2438' : 'none'
        }}>
          <div style={{
            width: 22, height: 22, borderRadius: '50%', flexShrink: 0, marginTop: 1,
            display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 11,
            background: step.state === 'done' ? '#6366f1' : step.state === 'active' ? '#1e1b4b' : '#0f172a',
            border: step.state === 'done' ? 'none' : `2px solid ${step.state === 'active' ? '#6366f1' : '#334155'}`,
            color: '#fff'
          }}>
            {step.state === 'done' ? '✓' : step.state === 'active' ? (
              <div style={{ width: 6, height: 6, borderRadius: '50%', background: '#6366f1' }} />
            ) : null}
          </div>
          <div>
            <p style={{
              margin: 0, fontSize: 13, fontWeight: 500,
              color: step.state === 'done' ? '#64748b' : step.state === 'active' ? '#f1f5f9' : '#334155'
            }}>{step.label}</p>
            {step.state === 'active' && (
              <p style={{ margin: 0, fontSize: 12, color: '#6366f1' }}>{step.desc}</p>
            )}
          </div>
        </div>
      ))}

      {/* Progress bar */}
      <div style={{ background: '#0f172a', borderRadius: 99, height: 3, margin: '18px 0 16px', overflow: 'hidden' }}>
        <div style={{
          height: 3, borderRadius: 99, background: '#6366f1',
          width: `${Math.min((seconds / 180) * 100, 95)}%`,
          transition: 'width 1s linear'
        }} />
      </div>

      <p style={{ color: '#475569', fontSize: 12, margin: 0, lineHeight: 1.6 }}>
        Typical processing time is 1–3 min. You can leave this page and return anytime.
      </p>

      <style>{`
        @keyframes meetiq-pulse {
          0%, 100% { opacity: 1; transform: scale(1); }
          50% { opacity: 0.4; transform: scale(0.8); }
        }
      `}</style>
    </div>
  )
}

// ── Main page ─────────────────────────────────────────────

export default function MeetingDetail() {
  const { id } = useParams()
  const [meeting, setMeeting] = useState(null)
  const [report, setReport] = useState(null)
  const [analysisStatus, setAnalysisStatus] = useState(null)
  const [polling, setPolling] = useState(false)
  const [tab, setTab] = useState('report')  // 'report' | 'transcript' | 'search'
  const [searchQuery, setSearchQuery] = useState('')
  const [searchResult, setSearchResult] = useState(null)
  const [searching, setSearching] = useState(false)
  const [editingSpeaker, setEditingSpeaker] = useState(null)
  const [speakerName, setSpeakerName] = useState('')
  const [transcribeSeconds, setTranscribeSeconds] = useState(0)

  const loadMeeting = useCallback(async () => {
    try {
      const data = await getMeeting(id)
      setMeeting(data)
    } catch {
      toast.error('Meeting not found')
    }
  }, [id])

  const loadReport = useCallback(async () => {
    try {
        const data = await getReport(id)
        setAnalysisStatus(data.analysis_status)
        if (data.analysis_status === 'completed') {
            setReport(data.report)
            setPolling(false)
        } else if (data.analysis_status === 'failed') {
            setPolling(false)
            toast.error('Analysis failed: ' + (data.error || 'Unknown error'))
        }
    } catch (err) {
        // Only ignore 404 (not triggered yet), log everything else
        if (err?.response?.status !== 404) {
            console.error('getReport error:', err)
        }
    }
  }, [id])

  useEffect(() => {
    loadMeeting()
    loadReport()
  }, [loadMeeting, loadReport])

  // Poll transcription status until completed
  useEffect(() => {
    if (!meeting) return
    if (meeting.status === 'completed') return
    // Start elapsed timer
    const timer = setInterval(() => setTranscribeSeconds(s => s + 1), 1000)

    const interval = setInterval(async () => {
      const s = await getTranscriptionStatus(id)
      if (s.status === 'completed') {
        clearInterval(interval)
        clearInterval(timer)       // ← stop timer
        setTranscribeSeconds(0)
        loadMeeting()
        toast.success('Transcription complete!')
      }
      if (s.status === 'failed') {
        clearInterval(interval)
        clearInterval(timer)
        toast.error('Transcription failed')
      }
    }, 15000)

    return () => { clearInterval(interval); clearInterval(timer) }
  }, [meeting?.status, id])

  // Poll analysis status while analyzing
  useEffect(() => {
    if (!polling) return
    
    const interval = setInterval(async () => {
        try {
            const data = await getReport(id)
            setAnalysisStatus(data.analysis_status)
            if (data.analysis_status === 'completed') {
                setReport(data.report)
                setPolling(false)
                clearInterval(interval)  // ← explicitly clear
                toast.success('Analysis complete!')
            } else if (data.analysis_status === 'failed') {
                setPolling(false)
                clearInterval(interval)
                toast.error('Analysis failed')
            }
        } catch (err) {
            console.error('Polling error:', err)
        }
    }, 3000)
    
    return () => clearInterval(interval)
  }, [polling, id])

  const handleAnalyze = async () => {
    try {
      await triggerAnalysis(id)
      setAnalysisStatus('analyzing')
      setPolling(true)
      toast.success('Analysis started!')
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to start analysis')
    }
  }

  const handleSearch = async (q = searchQuery) => {
    const normalizedQuery = q.trim()
    if (!normalizedQuery) {
      toast.error('Please enter a question')
      return
    }

    setSearchQuery(normalizedQuery)
    setSearching(true)
    setSearchResult(null)

    try {
      const result = await searchWithinMeeting(id, normalizedQuery)
      setSearchResult(result)
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Search failed')
    } finally {
      setSearching(false)
    }
  }

  const handleRenameSpeaker = async (speakerId) => {
    if (!speakerName.trim()) return
    try {
      await renameSpeaker(id, speakerId, speakerName)
      setEditingSpeaker(null)
      setSpeakerName('')
      loadMeeting()
      toast.success('Speaker renamed')
    } catch {
      toast.error('Rename failed')
    }
  }

  if (!meeting) return <p style={{ color: '#64748b' }}>Loading...</p>

  const tabs = ['report', 'transcript', 'search']
  const visibleMeetingId = meeting.id || id
  const quickQuestions = [
    'What decisions were made?',
    'What are the action items?',
    'What blockers were discussed?',
    'Summarize this meeting in 5 points',
  ]


  return (
    <div>
      {/* Header */}
      <div style={{ marginBottom: 24 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 8 }}>
          <h1 style={{ color: '#f1f5f9', fontSize: 26, fontWeight: 700 }}>
            {meeting.title}
          </h1>
          <StatusBadge status={meeting.status} />
        </div>
        <div style={{
          display: 'flex', alignItems: 'center', flexWrap: 'wrap',
          gap: 16, color: '#475569', fontSize: 14
        }}>
          {meeting.duration && <span>⏱ {Math.floor(meeting.duration / 60)}m</span>}
          <span>👥 {meeting.speakers?.length || 0} speakers</span>
          <span>📅 {new Date(meeting.created_at).toLocaleDateString()}</span>
          <span style={{
            display: 'inline-flex', alignItems: 'center', gap: 6,
            background: '#1e293b', border: '1px solid #334155',
            borderRadius: 999, padding: '2px 10px',
            color: '#94a3b8', fontSize: 12
          }}>
            ID: {visibleMeetingId}
          </span>
        </div>
      </div>

      {/* Analyze button */}
      {meeting.status === 'completed' && !report && analysisStatus !== 'analyzing' && (
        <button onClick={handleAnalyze} style={{
          display: 'flex', alignItems: 'center', gap: 8,
          background: '#6366f1', color: '#fff', border: 'none',
          padding: '10px 20px', borderRadius: 10, cursor: 'pointer',
          fontWeight: 600, marginBottom: 24
        }}>
          <Zap size={16} /> Run AI Analysis
        </button>
      )}

      {analysisStatus === 'analyzing' && (
        <div style={{
          display: 'flex', alignItems: 'center', gap: 8,
          color: '#a78bfa', marginBottom: 24
        }}>
          <RefreshCw size={16} className="spin" /> Analyzing meeting...
        </div>
      )}

      {/* Tabs */}
      <div style={{ display: 'flex', gap: 4, marginBottom: 20 }}>
        {tabs.map(t => (
          <button key={t} onClick={() => setTab(t)} style={{
            padding: '8px 18px', borderRadius: 8, border: 'none',
            cursor: 'pointer', fontWeight: 600, fontSize: 14, textTransform: 'capitalize',
            background: tab === t ? '#6366f1' : '#1e293b',
            color: tab === t ? '#fff' : '#64748b',
          }}>
            {t}
          </button>
        ))}
      </div>

      {/* ── REPORT TAB ── */}
      {tab === 'report' && report && (
        <div>
          <Section title="TL;DR">
            <p style={{ color: '#cbd5e1', lineHeight: 1.7 }}>{report.tldr}</p>
          </Section>

          <Section title="Summary">
            <p style={{ color: '#cbd5e1', lineHeight: 1.7 }}>{report.summary}</p>
          </Section>

          {report.topics_discussed?.length > 0 && (
            <Section title="Topics Discussed">
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
                {report.topics_discussed.map((t, i) => (
                  <span key={i} style={{
                    background: '#1e1b4b', color: '#a5b4fc',
                    padding: '4px 12px', borderRadius: 999, fontSize: 13
                  }}>{t}</span>
                ))}
              </div>
            </Section>
          )}

          {report.action_items?.length > 0 && (
            <Section title={`Action Items (${report.action_items.length})`}>
              {report.action_items.map((a, i) => <ActionItemCard key={i} item={a} />)}
            </Section>
          )}

          {report.decisions?.length > 0 && (
            <Section title={`Decisions (${report.decisions.length})`}>
              {report.decisions.map((d, i) => <DecisionCard key={i} item={d} />)}
            </Section>
          )}

          {report.blockers?.length > 0 && (
            <Section title={`Blockers (${report.blockers.length})`}>
              {report.blockers.map((b, i) => <BlockerCard key={i} item={b} />)}
            </Section>
          )}
        </div>
      )}

      {tab === 'report' && !report && (
        <div style={{ color: '#475569', textAlign: 'center', padding: '48px 0' }}>
          {meeting.status !== 'completed'
            ? <TranscriptionProgress seconds={transcribeSeconds} />
            : 'Click "Run AI Analysis" to generate the report'}
        </div>
      )}

      {/* ── TRANSCRIPT TAB ── */}
      {tab === 'transcript' && (
        <div>
          {/* Speaker rename */}
          {meeting.speakers?.length > 0 && (
            <Section title="Speakers">
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
                {meeting.speakers.map(s => (
                  <div key={s.id} style={{
                    display: 'flex', alignItems: 'center', gap: 6,
                    background: '#0f172a', borderRadius: 8, padding: '6px 10px'
                  }}>
                    {editingSpeaker === s.id ? (
                      <>
                        <input
                          value={speakerName}
                          onChange={e => setSpeakerName(e.target.value)}
                          onKeyDown={e => e.key === 'Enter' && handleRenameSpeaker(s.id)}
                          autoFocus
                          style={{
                            background: '#1e293b', border: '1px solid #6366f1',
                            color: '#f1f5f9', borderRadius: 6, padding: '2px 8px',
                            fontSize: 13, width: 100
                          }}
                        />
                        <button onClick={() => handleRenameSpeaker(s.id)}
                          style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#22c55e' }}>
                          <Check size={14} />
                        </button>
                        <button onClick={() => setEditingSpeaker(null)}
                          style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#ef4444' }}>
                          <X size={14} />
                        </button>
                      </>
                    ) : (
                      <>
                        <span style={{ color: '#94a3b8', fontSize: 13 }}>
                          {s.name || s.id}
                        </span>
                        <span style={{ color: '#475569', fontSize: 12 }}>
                          {Math.round(s.total_speaking_time)}s
                        </span>
                        <button
                          onClick={() => { setEditingSpeaker(s.id); setSpeakerName(s.name || '') }}
                          style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#64748b' }}>
                          <Edit2 size={12} />
                        </button>
                      </>
                    )}
                  </div>
                ))}
              </div>
            </Section>
          )}
          {analysisStatus === 'completed' && !report && (
            <button onClick={loadReport} style={{
                background: '#1e293b', border: '1px solid #334155',
                color: '#94a3b8', padding: '6px 12px', borderRadius: 8,
                cursor: 'pointer', marginBottom: 16
            }}>
                <RefreshCw size={14} /> Refresh Report
            </button>
        )}

          {/* Transcript segments */}
          <div style={{ maxHeight: 520, overflowY: 'auto' }}>
            {meeting.transcript?.map((seg, i) => {
              const speaker = meeting.speakers?.find(s => s.id === seg.speaker_id)
              const name = speaker?.name || seg.speaker_id
              const mins = Math.floor(seg.start / 60)
              const secs = Math.floor(seg.start % 60)

              return (
                <div key={i} style={{
                  display: 'flex', gap: 12, marginBottom: 14,
                  paddingBottom: 14, borderBottom: '1px solid #1e293b'
                }}>
                  <span style={{ color: '#475569', fontSize: 12, minWidth: 44, paddingTop: 2 }}>
                    {String(mins).padStart(2,'0')}:{String(secs).padStart(2,'0')}
                  </span>
                  <div>
                    <span style={{
                      color: '#6366f1', fontWeight: 600, fontSize: 13, marginBottom: 4,
                      display: 'block'
                    }}>{name}</span>
                    <p style={{ color: '#cbd5e1', lineHeight: 1.6, margin: 0 }}>{seg.text}</p>
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      )}

      {tab === 'search' && (
        <div>
          <div style={{
            background: '#1e293b', borderRadius: 10, padding: '10px 12px',
            border: '1px solid #334155', marginBottom: 12
          }}>
            <p style={{ color: '#94a3b8', fontSize: 13, margin: 0 }}>
              Searching within this meeting only (ID: {visibleMeetingId})
            </p>
          </div>

          <div style={{ display: 'flex', gap: 8, marginBottom: 20 }}>
            <input
              value={searchQuery}
              onChange={e => setSearchQuery(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && handleSearch()}
              placeholder="Ask anything about this meeting..."
              style={{
                flex: 1, padding: '10px 14px', borderRadius: 10,
                background: '#1e293b', border: '1px solid #334155',
                color: '#f1f5f9', fontSize: 15, outline: 'none'
              }}
            />
            <button onClick={handleSearch} disabled={searching} style={{
              display: 'inline-flex', alignItems: 'center', gap: 6,
              background: searching ? '#334155' : '#6366f1', color: '#fff', border: 'none',
              padding: '10px 16px', borderRadius: 10, cursor: searching ? 'not-allowed' : 'pointer'
            }}>
              {searching ? <RefreshCw size={16} className="spin" /> : <Search size={18} />}
              {searching ? 'Searching...' : 'Ask'}
            </button>
          </div>

          {!searchResult && (
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, marginBottom: 16 }}>
              {quickQuestions.map(ex => (
                <button key={ex} onClick={() => handleSearch(ex)} style={{
                  background: '#1e293b', border: '1px solid #334155',
                  color: '#64748b', borderRadius: 999, padding: '6px 14px',
                  fontSize: 13, cursor: 'pointer'
                }}>
                  {ex}
                </button>
              ))}
            </div>
          )}

          {searchResult && (
            <Section title="Answer">
              <p style={{ color: '#cbd5e1', lineHeight: 1.7, marginBottom: 16 }}>
                {searchResult.answer}
              </p>
              {searchResult.sources?.length > 0 && (
                <p style={{ color: '#475569', fontSize: 13 }}>
                  Based on {searchResult.chunks_used} relevant passages from this meeting
                </p>
              )}
            </Section>
          )}
        </div>
      )}
    </div>
  )
}