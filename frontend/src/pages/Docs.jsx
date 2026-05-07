import { Link } from 'react-router-dom'
import { Upload, Zap, Search, FileAudio, FileText, Mic, Users, Brain, ChevronRight, AlertCircle, CheckCircle2, HelpCircle } from 'lucide-react'

const steps = [
  {
    num: '01',
    icon: <Upload size={18} />,
    title: 'Upload a file',
    content: [
      'Click Upload in the top nav or go to the home page.',
      'Choose Audio/Video for MP3, WAV, MP4, M4A files (max 50MB).',
      'Choose Transcript for TXT or PDF files — processed instantly, no transcription wait.',
      'Give your meeting a title and hit Upload & Process.',
    ]
  },
  {
    num: '02',
    icon: <Mic size={18} />,
    title: 'Wait for transcription',
    content: [
      'Audio/video files are sent to AssemblyAI for transcription. This usually takes 1–3 minutes.',
      'The status badge on the meeting shows: Uploaded → Transcribing → Completed.',
      'The page auto-refreshes every few seconds — no need to manually reload.',
      'Transcript files skip this step entirely and go straight to Completed.',
    ]
  },
  {
    num: '03',
    icon: <Brain size={18} />,
    title: 'Run AI Analysis',
    content: [
      'Once transcription is complete, open the meeting and click Run AI Analysis.',
      'A 4-agent AI pipeline runs in the background: Summary, Action Items, Decisions, Blockers.',
      'Results appear in the Report tab once complete (usually under 1 minute).',
      'The report includes a TL;DR, full summary, topics discussed, and structured lists.',
    ]
  },
  {
    num: '04',
    icon: <Users size={18} />,
    title: 'Review the transcript & speakers',
    content: [
      'Open the Transcript tab to read the full conversation with timestamps.',
      'Speakers are auto-detected as Speaker_1, Speaker_2, etc.',
      'Click the edit icon next to any speaker to rename them (e.g. "Rahul", "Alice").',
      'Renamed speakers update instantly across the entire transcript.',
    ]
  },
  {
    num: '05',
    icon: <Search size={18} />,
    title: 'Search your meetings',
    content: [
      'Use the Search tab inside a meeting to ask questions about that specific call.',
      'Use the global Search page (top nav) to search across all your meetings.',
      'Ask in plain English: "What decisions were made?", "Who owns the deployment task?"',
      'Answers are grounded in your actual meeting content — not hallucinated.',
    ]
  },
]

const faqs = [
  {
    q: 'Why is transcription taking so long?',
    a: 'Transcription depends on file length and AssemblyAI queue times. A 1-hour meeting typically takes 3–6 minutes. If it stays stuck for over 10 minutes, try re-uploading.'
  },
  {
    q: 'What is speaker diarization?',
    a: 'Diarization is the process of separating "who spoke when". MeetIQ automatically identifies different speakers in your audio and labels them Speaker_1, Speaker_2, etc. You can rename them after.'
  },
  {
    q: 'Why does search say "No relevant meeting data found"?',
    a: 'Search only works on meetings that have been analyzed. Make sure you clicked "Run AI Analysis" and it completed successfully before searching.'
  },
  {
    q: 'Can I upload video files?',
    a: 'Yes. MP4 video files are supported. The audio track is extracted automatically before transcription.'
  },
  {
    q: 'Is there a file size limit?',
    a: 'The frontend allows up to 50MB. For longer meetings, consider compressing the audio to MP3 first.'
  },
  {
    q: 'What languages are supported?',
    a: 'AssemblyAI supports 99+ languages. The default is English but it auto-detects language from the audio.'
  },
  {
    q: 'Can I search across all my meetings at once?',
    a: 'Yes. Use the Search page from the top navigation. Switch to "Global" mode to search across all analyzed meetings simultaneously.'
  },
]

const stack = [
  { label: 'Backend', items: ['FastAPI', 'MongoDB Atlas', 'AssemblyAI (transcription)', 'Groq + LangGraph (AI agents)'] },
  { label: 'Embeddings & Search', items: ['Jina AI embeddings', 'MongoDB Atlas Vector Search', 'RAG with Groq LLaMA 3.3'] },
  { label: 'Frontend', items: ['React + Vite', 'React Router', 'Axios', 'Lucide Icons'] },
  { label: 'Deployment', items: ['Render (backend)', 'Render Static Site (frontend)', 'MongoDB Atlas M0 free tier'] },
]

export default function Docs() {
  return (
    <div style={{
      minHeight: '100vh',
      background: '#0f172a',
      fontFamily: "'DM Sans', sans-serif",
      color: '#f1f5f9',
    }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Syne:wght@700;800&display=swap');
        * { box-sizing: border-box; margin: 0; padding: 0; }
        .doc-section { border-bottom: 1px solid #1e293b; padding: 64px 0; }
        .faq-item { border: 1px solid #1e293b; border-radius: 12px; padding: 20px 24px; margin-bottom: 10px; }
        .faq-item:hover { border-color: #334155; }
      `}</style>

      {/* Nav */}
      <nav style={{
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        padding: '20px 48px', borderBottom: '1px solid #1e293b',
        position: 'sticky', top: 0, background: 'rgba(15,23,42,0.95)',
        backdropFilter: 'blur(12px)', zIndex: 100,
      }}>
        <Link to="/" style={{ fontFamily: "'Syne', sans-serif", fontSize: 22, fontWeight: 800, color: '#f1f5f9', textDecoration: 'none', letterSpacing: '-0.5px' }}>
          Meet<span style={{ color: '#6366f1' }}>IQ</span>
        </Link>
        <div style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
          <Link to="/login" style={{ color: '#94a3b8', textDecoration: 'none', fontSize: 14, fontWeight: 500, padding: '8px 16px' }}>
            Sign in
          </Link>
          <Link to="/register" style={{
            background: '#6366f1', color: '#fff', textDecoration: 'none',
            fontSize: 14, fontWeight: 600, padding: '8px 18px', borderRadius: 8,
          }}>
            Get Started →
          </Link>
        </div>
      </nav>

      <div style={{ maxWidth: 800, margin: '0 auto', padding: '0 24px' }}>

        {/* Header */}
        <div style={{ padding: '72px 0 64px', borderBottom: '1px solid #1e293b' }}>
          <p style={{ color: '#6366f1', fontSize: 12, fontWeight: 700, letterSpacing: 2, textTransform: 'uppercase', marginBottom: 16 }}>
            Documentation
          </p>
          <h1 style={{
            fontFamily: "'Syne', sans-serif", fontSize: 'clamp(36px, 5vw, 52px)',
            fontWeight: 800, letterSpacing: '-2px', marginBottom: 20, lineHeight: 1.1,
          }}>
            How to use MeetIQ
          </h1>
          <p style={{ color: '#64748b', fontSize: 17, lineHeight: 1.7, maxWidth: 600 }}>
            MeetIQ turns meeting recordings and transcripts into structured intelligence —
            summaries, action items, decisions, and a searchable knowledge base.
          </p>
        </div>

        {/* What is MeetIQ */}
        <div className="doc-section">
          <h2 style={{ fontFamily: "'Syne', sans-serif", fontSize: 26, fontWeight: 800, letterSpacing: '-0.5px', marginBottom: 20 }}>
            What is MeetIQ?
          </h2>
          <p style={{ color: '#94a3b8', lineHeight: 1.8, marginBottom: 16 }}>
            MeetIQ is a meeting intelligence platform. You upload a recording or transcript,
            and it automatically transcribes speech, identifies who said what, and runs an AI
            pipeline to extract the key information from the meeting.
          </p>
          <p style={{ color: '#94a3b8', lineHeight: 1.8, marginBottom: 24 }}>
            The result is a structured report with a summary, action items (with owners and deadlines),
            decisions made, and blockers raised — plus a natural language search interface so you can
            ask questions about any meeting.
          </p>

          {/* Supported formats */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
            <div style={{ background: '#1e293b', borderRadius: 12, padding: '20px 24px', border: '1px solid #334155' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 12 }}>
                <FileAudio size={18} color="#818cf8" />
                <span style={{ fontWeight: 700, fontSize: 14 }}>Audio / Video</span>
              </div>
              <p style={{ color: '#475569', fontSize: 13, lineHeight: 1.6 }}>MP3, WAV, MP4, M4A<br />Max 50MB · Transcribed by AssemblyAI</p>
            </div>
            <div style={{ background: '#1e293b', borderRadius: 12, padding: '20px 24px', border: '1px solid #334155' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 12 }}>
                <FileText size={18} color="#818cf8" />
                <span style={{ fontWeight: 700, fontSize: 14 }}>Transcript</span>
              </div>
              <p style={{ color: '#475569', fontSize: 13, lineHeight: 1.6 }}>TXT, PDF<br />Processed instantly · No wait time</p>
            </div>
          </div>
        </div>

        {/* Step by step */}
        <div className="doc-section">
          <h2 style={{ fontFamily: "'Syne', sans-serif", fontSize: 26, fontWeight: 800, letterSpacing: '-0.5px', marginBottom: 40 }}>
            Step-by-step guide
          </h2>

          {steps.map((s, i) => (
            <div key={i} style={{ display: 'flex', gap: 24, marginBottom: 40 }}>
              {/* Left — number + line */}
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', flexShrink: 0 }}>
                <div style={{
                  width: 44, height: 44, borderRadius: 12,
                  background: 'rgba(99,102,241,0.15)', border: '1px solid rgba(99,102,241,0.3)',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  color: '#818cf8', flexShrink: 0,
                }}>
                  {s.icon}
                </div>
                {i < steps.length - 1 && (
                  <div style={{ width: 1, flex: 1, background: '#1e293b', marginTop: 8, minHeight: 24 }} />
                )}
              </div>

              {/* Right — content */}
              <div style={{ paddingBottom: 8 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 14 }}>
                  <span style={{ color: '#6366f1', fontSize: 11, fontWeight: 700, letterSpacing: 1 }}>{s.num}</span>
                  <h3 style={{ fontSize: 17, fontWeight: 700, color: '#f1f5f9' }}>{s.title}</h3>
                </div>
                <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: 8 }}>
                  {s.content.map((c, j) => (
                    <li key={j} style={{ display: 'flex', gap: 10, alignItems: 'flex-start' }}>
                      <CheckCircle2 size={15} color="#22c55e" style={{ marginTop: 3, flexShrink: 0 }} />
                      <span style={{ color: '#94a3b8', fontSize: 14, lineHeight: 1.6 }}>{c}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          ))}
        </div>

        {/* FAQ */}
        <div className="doc-section">
          <h2 style={{ fontFamily: "'Syne', sans-serif", fontSize: 26, fontWeight: 800, letterSpacing: '-0.5px', marginBottom: 32 }}>
            FAQ
          </h2>
          {faqs.map((f, i) => (
            <div key={i} className="faq-item">
              <div style={{ display: 'flex', gap: 10, alignItems: 'flex-start', marginBottom: 8 }}>
                <HelpCircle size={16} color="#6366f1" style={{ marginTop: 2, flexShrink: 0 }} />
                <p style={{ fontWeight: 700, fontSize: 15, color: '#f1f5f9' }}>{f.q}</p>
              </div>
              <p style={{ color: '#64748b', fontSize: 14, lineHeight: 1.7, paddingLeft: 26 }}>{f.a}</p>
            </div>
          ))}
        </div>

        {/* Tech Stack */}
        <div className="doc-section">
          <h2 style={{ fontFamily: "'Syne', sans-serif", fontSize: 26, fontWeight: 800, letterSpacing: '-0.5px', marginBottom: 32 }}>
            Tech stack
          </h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 14 }}>
            {stack.map((s, i) => (
              <div key={i} style={{ background: '#1e293b', borderRadius: 12, padding: '20px 24px', border: '1px solid #334155' }}>
                <p style={{ color: '#6366f1', fontSize: 11, fontWeight: 700, letterSpacing: 1, textTransform: 'uppercase', marginBottom: 12 }}>
                  {s.label}
                </p>
                {s.items.map((item, j) => (
                  <p key={j} style={{ color: '#94a3b8', fontSize: 13, lineHeight: 1.8 }}>· {item}</p>
                ))}
              </div>
            ))}
          </div>
        </div>

        {/* Bottom CTA */}
        <div style={{ padding: '64px 0', textAlign: 'center' }}>
          <p style={{ color: '#475569', fontSize: 14, marginBottom: 24 }}>Ready to try it?</p>
          <Link to="/register" style={{
            background: '#6366f1', color: '#fff', textDecoration: 'none',
            padding: '14px 32px', borderRadius: 12, fontWeight: 700, fontSize: 15,
            display: 'inline-flex', alignItems: 'center', gap: 8,
          }}>
            Create your account <ChevronRight size={16} />
          </Link>
        </div>
      </div>
    </div>
  )
}