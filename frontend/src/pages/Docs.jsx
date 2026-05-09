import { Link } from 'react-router-dom'
import { Upload, Zap, Search, FileAudio, FileText, Mic, Users, Brain, ChevronRight, CheckCircle2, HelpCircle } from 'lucide-react'

const steps = [
  {
    num: '01', icon: <Upload size={18} />, title: 'Upload a file',
    content: [
      'Click Upload in the top nav or go to the home page.',
      'Choose Audio/Video for MP3, WAV, MP4, M4A files (max 100MB).',
      'Choose Transcript for TXT or PDF files — processed instantly, no transcription wait.',
      'Give your meeting a title and hit Upload & Process.',
    ]
  },
  {
    num: '02', icon: <Mic size={18} />, title: 'Wait for transcription',
    content: [
      'Audio/video files are sent to AssemblyAI for transcription. This usually takes 1–3 minutes.',
      'The status badge on the meeting shows: Uploaded → Transcribing → Completed.',
      'The page auto-refreshes every few seconds — no need to manually reload.',
      'Transcript files skip this step entirely and go straight to Completed.',
    ]
  },
  {
    num: '03', icon: <Brain size={18} />, title: 'Run AI Analysis',
    content: [
      'Once transcription is complete, open the meeting and click Run AI Analysis.',
      'A 4-agent AI pipeline runs in the background: Summary, Action Items, Decisions, Blockers.',
      'Results appear in the Report tab once complete (usually under 1 minute).',
      'The report includes a TL;DR, full summary, topics discussed, and structured lists.',
    ]
  },
  {
    num: '04', icon: <Users size={18} />, title: 'Review the transcript & speakers',
    content: [
      'Open the Transcript tab to read the full conversation with timestamps.',
      'Speakers are auto-detected as Speaker_1, Speaker_2, etc.',
      'Click the edit icon next to any speaker to rename them (e.g. "Rahul", "Alice").',
      'Renamed speakers update instantly across the entire transcript.',
    ]
  },
  {
    num: '05', icon: <Search size={18} />, title: 'Search your meetings',
    content: [
      'Use the Search tab inside a meeting to ask questions about that specific call.',
      'Use the global Search page (top nav) to search across all your meetings.',
      'Ask in plain English: "What decisions were made?", "Who owns the deployment task?"',
      'Answers are grounded in your actual meeting content — not hallucinated.',
    ]
  },
]

const faqs = [
  { q: 'Why is transcription taking so long?',            a: 'Transcription depends on file length and AssemblyAI queue times. A 1-hour meeting typically takes 3–6 minutes. If it stays stuck for over 10 minutes, try re-uploading.' },
  { q: 'What is speaker diarization?',                   a: 'Diarization separates "who spoke when". MeetIQ automatically identifies different speakers and labels them Speaker_1, Speaker_2, etc. You can rename them after.' },
  { q: 'Why does search say "No relevant meeting data found"?', a: 'Search only works on meetings that have been analyzed. Make sure you clicked "Run AI Analysis" and it completed successfully before searching.' },
  { q: 'Can I upload video files?',                      a: 'Yes. MP4 video files are supported. The audio track is extracted automatically before transcription.' },
  { q: 'Is there a file size limit?',                    a: 'The frontend allows up to 100MB. For longer meetings, consider compressing the audio to MP3 first.' },
  { q: 'What languages are supported?',                  a: 'AssemblyAI supports 99+ languages. The default is English but it auto-detects language from the audio.' },
  { q: 'Can I search across all my meetings at once?',   a: 'Yes. Use the Search page from the top navigation. Switch to "Global" mode to search across all analyzed meetings simultaneously.' },
]

const stack = [
  { label: 'Backend',             items: ['FastAPI', 'MongoDB Atlas', 'AssemblyAI (transcription)', 'Groq + LangGraph (AI agents)'] },
  { label: 'Embeddings & Search', items: ['Jina AI embeddings', 'MongoDB Atlas Vector Search', 'RAG with Groq LLaMA 3.3'] },
  { label: 'Frontend',            items: ['React + Vite', 'React Router', 'Axios', 'Lucide Icons'] },
  { label: 'Deployment',          items: ['Render (backend)', 'Render Static Site (frontend)', 'MongoDB Atlas M0 free tier'] },
]

export default function Docs() {
  return (
    <div style={{ minHeight: '100vh', background: '#0f172a', fontFamily: "'DM Sans', sans-serif", color: '#f1f5f9' }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Syne:wght@700;800&display=swap');

        /* FIX: removed the '* { margin:0; padding:0 }' reset that was here —
           it fought index.css and caused padding glitches on mobile.
           Global reset already lives in index.css. */

        .doc-section {
          border-bottom: 1px solid #1e293b;
          /* FIX: was 'padding: 64px 0' — clamp shrinks on mobile */
          padding: clamp(32px, 6vw, 64px) 0;
        }
        .faq-item {
          border: 1px solid #1e293b;
          border-radius: 12px;
          padding: 18px 20px;
          margin-bottom: 10px;
          transition: border-color 0.15s;
        }
        .faq-item:hover { border-color: #334155; }

        /* FIX: hide secondary nav links on small phones */
        @media (max-width: 479px) {
          .docs-nav-hide { display: none !important; }
        }
      `}</style>

      {/* ── Navbar ── */}
      <nav style={{
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        /* FIX: was '20px 48px' — 48px side eats content on phones */
        padding: '16px var(--page-px)',
        borderBottom: '1px solid #1e293b',
        position: 'sticky', top: 0,
        background: 'rgba(15,23,42,0.95)',
        backdropFilter: 'blur(12px)', zIndex: 100,
      }}>
        <Link to="/" style={{ fontFamily: "'Syne', sans-serif", fontSize: 22, fontWeight: 800, color: '#f1f5f9', textDecoration: 'none', letterSpacing: '-0.5px', flexShrink: 0 }}>
          Meet<span style={{ color: '#6366f1' }}>IQ</span>
        </Link>
        <div style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
          <Link to="/login" className="docs-nav-hide" style={{ color: '#94a3b8', textDecoration: 'none', fontSize: 14, fontWeight: 500, padding: '8px 12px' }}>
            Sign in
          </Link>
          <Link to="/register" style={{
            background: '#6366f1', color: '#fff', textDecoration: 'none',
            fontSize: 14, fontWeight: 600, padding: '8px 16px', borderRadius: 8,
            whiteSpace: 'nowrap',
          }}>
            Get Started →
          </Link>
        </div>
      </nav>

      {/* ── Content wrapper ── */}
      {/* FIX: was 'padding: 0 24px' — hardcoded, now uses token */}
      <div style={{ maxWidth: 800, margin: '0 auto', padding: '0 var(--page-px)' }}>

        {/* Header */}
        <div style={{ padding: 'clamp(40px, 8vw, 72px) 0 clamp(32px, 6vw, 64px)', borderBottom: '1px solid #1e293b' }}>
          <p style={{ color: '#6366f1', fontSize: 12, fontWeight: 700, letterSpacing: 2, textTransform: 'uppercase', marginBottom: 16 }}>
            Documentation
          </p>
          <h1 style={{
            fontFamily: "'Syne', sans-serif",
            fontSize: 'clamp(28px, 5vw, 52px)',       /* FIX: floor was 36px, too big on small phones */
            fontWeight: 800, letterSpacing: 'clamp(-1px, -0.03em, -2px)',
            marginBottom: 20, lineHeight: 1.1,
          }}>
            How to use MeetIQ
          </h1>
          <p style={{ color: '#64748b', fontSize: 'clamp(14px, 2vw, 17px)', lineHeight: 1.7, maxWidth: 600 }}>
            MeetIQ turns meeting recordings and transcripts into structured intelligence —
            summaries, action items, decisions, and a searchable knowledge base.
          </p>
        </div>

        {/* What is MeetIQ */}
        <div className="doc-section">
          <h2 style={{ fontFamily: "'Syne', sans-serif", fontSize: 'clamp(20px, 3vw, 26px)', fontWeight: 800, letterSpacing: '-0.5px', marginBottom: 20 }}>
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
          {/* FIX: was 'gridTemplateColumns: 1fr 1fr' — never collapsed on small phones */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 12 }}>
            <div style={{ background: '#1e293b', borderRadius: 12, padding: '18px 20px', border: '1px solid #334155' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 10 }}>
                <FileAudio size={18} color="#818cf8" />
                <span style={{ fontWeight: 700, fontSize: 14 }}>Audio / Video</span>
              </div>
              <p style={{ color: '#475569', fontSize: 13, lineHeight: 1.6 }}>MP3, WAV, MP4, M4A<br />Max 100MB · Transcribed by AssemblyAI</p>
            </div>
            <div style={{ background: '#1e293b', borderRadius: 12, padding: '18px 20px', border: '1px solid #334155' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 10 }}>
                <FileText size={18} color="#818cf8" />
                <span style={{ fontWeight: 700, fontSize: 14 }}>Transcript</span>
              </div>
              <p style={{ color: '#475569', fontSize: 13, lineHeight: 1.6 }}>TXT, PDF<br />Processed instantly · No wait time</p>
            </div>
          </div>
        </div>

        {/* Step-by-step */}
        <div className="doc-section">
          <h2 style={{ fontFamily: "'Syne', sans-serif", fontSize: 'clamp(20px, 3vw, 26px)', fontWeight: 800, letterSpacing: '-0.5px', marginBottom: 'clamp(24px, 4vw, 40px)' }}>
            Step-by-step guide
          </h2>

          {steps.map((s, i) => (
            <div key={i} style={{ display: 'flex', gap: 20, marginBottom: 36 }}>
              {/* Icon + connector line */}
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

              {/* Content */}
              <div style={{ paddingBottom: 8, minWidth: 0 /* FIX: prevents text overflow in flex */ }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 12 }}>
                  <span style={{ color: '#6366f1', fontSize: 11, fontWeight: 700, letterSpacing: 1, flexShrink: 0 }}>{s.num}</span>
                  <h3 style={{ fontSize: 16, fontWeight: 700, color: '#f1f5f9', margin: 0 }}>{s.title}</h3>
                </div>
                <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: 8 }}>
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
          <h2 style={{ fontFamily: "'Syne', sans-serif", fontSize: 'clamp(20px, 3vw, 26px)', fontWeight: 800, letterSpacing: '-0.5px', marginBottom: 'clamp(20px, 3vw, 32px)' }}>
            FAQ
          </h2>
          {faqs.map((f, i) => (
            <div key={i} className="faq-item">
              <div style={{ display: 'flex', gap: 10, alignItems: 'flex-start', marginBottom: 8 }}>
                <HelpCircle size={16} color="#6366f1" style={{ marginTop: 2, flexShrink: 0 }} />
                <p style={{ fontWeight: 700, fontSize: 15, color: '#f1f5f9', margin: 0 }}>{f.q}</p>
              </div>
              <p style={{ color: '#64748b', fontSize: 14, lineHeight: 1.7, paddingLeft: 26, margin: 0 }}>{f.a}</p>
            </div>
          ))}
        </div>

        {/* Known Limitations */}
        <div className="doc-section">
          <h2 style={{ fontFamily: "'Syne', sans-serif", fontSize: 'clamp(20px, 3vw, 26px)', fontWeight: 800, letterSpacing: '-0.5px', marginBottom: 8 }}>
            Known limitations
          </h2>
          <p style={{ color: '#475569', fontSize: 14, marginBottom: 'clamp(20px, 3vw, 32px)' }}>
            This app runs on free-tier infrastructure. Here's what that means for you.
          </p>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            <div style={{ background: '#1e293b', borderRadius: 12, padding: '18px 20px', border: '1px solid #854d0e' }}>
              <p style={{ color: '#fbbf24', fontWeight: 700, fontSize: 14, marginBottom: 6 }}>⏳ Backend cold start (30–60 seconds)</p>
              <p style={{ color: '#64748b', fontSize: 13, lineHeight: 1.7, margin: 0 }}>
                The backend is on Render's free tier, which shuts down after 15 minutes of inactivity. The first API call after idle will take 30–60 seconds to respond. Just wait and retry.
              </p>
            </div>
            <div style={{ background: '#1e293b', borderRadius: 12, padding: '18px 20px', border: '1px solid #1e3a5f' }}>
              <p style={{ color: '#60a5fa', fontWeight: 700, fontSize: 14, marginBottom: 6 }}>🔍 Search works best with specific keywords</p>
              <p style={{ color: '#64748b', fontSize: 13, lineHeight: 1.7, margin: 0 }}>
                Search is powered by <strong style={{ color: '#94a3b8' }}>MongoDB Atlas Search (BM25)</strong> — keyword-based, not semantic. Use words that were actually said in the meeting for best results.
              </p>
            </div>
            <div style={{ background: '#1e293b', borderRadius: 12, padding: '18px 20px', border: '1px solid #14532d' }}>
              <p style={{ color: '#4ade80', fontWeight: 700, fontSize: 14, marginBottom: 6 }}>💡 Why not use SentenceTransformers?</p>
              <p style={{ color: '#64748b', fontSize: 13, lineHeight: 1.7, margin: 0 }}>
                Loading a 200–400MB embedding model on Render's 512MB free tier consistently caused OOM crashes. Atlas Search is a deliberate engineering tradeoff for stability — not a design limitation.
              </p>
            </div>
            <div style={{ background: '#1e293b', borderRadius: 12, padding: '18px 20px', border: '1px solid #334155' }}>
              <p style={{ color: '#94a3b8', fontWeight: 700, fontSize: 14, marginBottom: 6 }}>📁 File size limit: 100MB</p>
              <p style={{ color: '#64748b', fontSize: 13, lineHeight: 1.7, margin: 0 }}>
                The frontend enforces a 100MB upload limit. For longer recordings, compress to MP3 first — most 1-hour meetings compress well under 100MB.
              </p>
            </div>
          </div>
        </div>

        {/* Tech Stack */}
        <div className="doc-section">
          <h2 style={{ fontFamily: "'Syne', sans-serif", fontSize: 'clamp(20px, 3vw, 26px)', fontWeight: 800, letterSpacing: '-0.5px', marginBottom: 'clamp(20px, 3vw, 32px)' }}>
            Tech stack
          </h2>
          {/* FIX: minmax(280px→220px) so cards don't orphan on mid-size screens */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 14 }}>
            {stack.map((s, i) => (
              <div key={i} style={{ background: '#1e293b', borderRadius: 12, padding: '18px 20px', border: '1px solid #334155' }}>
                <p style={{ color: '#6366f1', fontSize: 11, fontWeight: 700, letterSpacing: 1, textTransform: 'uppercase', marginBottom: 10 }}>{s.label}</p>
                {s.items.map((item, j) => (
                  <p key={j} style={{ color: '#94a3b8', fontSize: 13, lineHeight: 1.8, margin: 0 }}>· {item}</p>
                ))}
              </div>
            ))}
          </div>
        </div>

        {/* Bottom CTA */}
        <div style={{ padding: 'clamp(40px, 6vw, 64px) 0', textAlign: 'center' }}>
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