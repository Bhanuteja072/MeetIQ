import { Link } from 'react-router-dom'
import { Upload, Brain, Search, Users, FileAudio, FileText, Zap, ChevronRight, Mic, BarChart2, MessageSquare } from 'lucide-react'

const features = [
  {
    icon: <FileAudio size={22} />,
    title: 'Upload Any Format',
    desc: 'MP3, WAV, MP4, M4A audio/video files or TXT/PDF transcripts — we handle it all.'
  },
  {
    icon: <Mic size={22} />,
    title: 'Auto Transcription',
    desc: 'Powered by AssemblyAI. Accurate speech-to-text with speaker diarization in minutes.'
  },
  {
    icon: <Brain size={22} />,
    title: 'AI Analysis',
    desc: 'Multi-agent pipeline extracts summaries, action items, decisions and blockers automatically.'
  },
  {
    icon: <Search size={22} />,
    title: 'Semantic Search',
    desc: 'Ask anything in plain English. Search across all meetings or drill into one specific call.'
  },
  {
    icon: <Users size={22} />,
    title: 'Speaker Tracking',
    desc: 'Identifies every speaker, tracks talk time, and lets you rename them to real names.'
  },
  {
    icon: <BarChart2 size={22} />,
    title: 'Meeting Archive',
    desc: 'All your meetings in one place. Filter, browse and revisit any past discussion instantly.'
  },
]

const steps = [
  {
    num: '01',
    icon: <Upload size={20} />,
    title: 'Upload your meeting',
    desc: 'Drop an audio, video or transcript file. We support all major formats.'
  },
  {
    num: '02',
    icon: <Zap size={20} />,
    title: 'Run AI Analysis',
    desc: 'One click triggers transcription + 4-agent AI pipeline. Takes 1–3 minutes.'
  },
  {
    num: '03',
    icon: <MessageSquare size={20} />,
    title: 'Ask anything',
    desc: 'Search across meetings with natural language. Get grounded, cited answers instantly.'
  },
]

export default function Landing() {
  return (
    <div style={{
      minHeight: '100vh',
      background: '#0f172a',
      fontFamily: "'DM Sans', sans-serif",
      color: '#f1f5f9',
      overflowX: 'hidden',
    }}>
      {/* Google Font */}
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Syne:wght@700;800&display=swap');
        * { box-sizing: border-box; margin: 0; padding: 0; }
        .hero-glow {
          position: absolute;
          width: 600px; height: 600px;
          background: radial-gradient(circle, rgba(99,102,241,0.18) 0%, transparent 70%);
          top: -100px; left: 50%; transform: translateX(-50%);
          pointer-events: none;
        }
        .feature-card:hover {
          border-color: #6366f1 !important;
          transform: translateY(-2px);
        }
        .feature-card { transition: all 0.2s; }
        .cta-btn:hover { opacity: 0.9; transform: translateY(-1px); }
        .cta-btn { transition: all 0.15s; }
        .outline-btn:hover { background: rgba(99,102,241,0.1) !important; }
        .outline-btn { transition: all 0.15s; }
        @keyframes fadeUp {
          from { opacity: 0; transform: translateY(24px); }
          to { opacity: 1; transform: translateY(0); }
        }
        .fade-up { animation: fadeUp 0.6s ease forwards; }
        .fade-up-2 { animation: fadeUp 0.6s 0.15s ease both; }
        .fade-up-3 { animation: fadeUp 0.6s 0.3s ease both; }
      `}</style>

      {/* Nav */}
      <nav style={{
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        padding: '20px 48px', borderBottom: '1px solid #1e293b',
        position: 'sticky', top: 0, background: 'rgba(15,23,42,0.95)',
        backdropFilter: 'blur(12px)', zIndex: 100,
      }}>
        <span style={{ fontFamily: "'Syne', sans-serif", fontSize: 22, fontWeight: 800, color: '#f1f5f9', letterSpacing: '-0.5px' }}>
          Meet<span style={{ color: '#6366f1' }}>IQ</span>
        </span>
        <div style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
          <Link to="/docs" style={{
            color: '#94a3b8', textDecoration: 'none', fontSize: 14,
            fontWeight: 500, padding: '8px 16px', borderRadius: 8,
          }}>
            Docs
          </Link>
          <Link to="/login" style={{
            color: '#94a3b8', textDecoration: 'none', fontSize: 14,
            fontWeight: 500, padding: '8px 16px', borderRadius: 8,
          }}>
            Sign in
          </Link>
          <Link to="/register" style={{
            background: '#6366f1', color: '#fff', textDecoration: 'none',
            fontSize: 14, fontWeight: 600, padding: '8px 18px',
            borderRadius: 8,
          }} className="cta-btn">
            Get Started →
          </Link>
        </div>
      </nav>

      {/* Hero */}
      <section style={{
        position: 'relative', textAlign: 'center',
        padding: '100px 24px 80px', overflow: 'hidden',
      }}>
        <div className="hero-glow" />

        <div className="fade-up" style={{
          display: 'inline-flex', alignItems: 'center', gap: 8,
          background: 'rgba(99,102,241,0.12)', border: '1px solid rgba(99,102,241,0.3)',
          borderRadius: 999, padding: '6px 16px', marginBottom: 28,
          fontSize: 13, color: '#a5b4fc', fontWeight: 500,
        }}>
          <Zap size={13} /> AI-powered meeting intelligence
        </div>

        <h1 className="fade-up-2" style={{
          fontFamily: "'Syne', sans-serif",
          fontSize: 'clamp(40px, 6vw, 72px)',
          fontWeight: 800, lineHeight: 1.08,
          letterSpacing: '-2px', marginBottom: 24,
          background: 'linear-gradient(135deg, #f1f5f9 30%, #94a3b8)',
          WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent',
        }}>
          Your meetings,<br />finally understood.
        </h1>

        <p className="fade-up-3" style={{
          color: '#64748b', fontSize: 18, lineHeight: 1.7,
          maxWidth: 520, margin: '0 auto 40px',
        }}>
          Upload any meeting recording or transcript. Get instant transcription,
          AI-generated reports, and a searchable knowledge base — all in minutes.
        </p>

        <div className="fade-up-3" style={{ display: 'flex', gap: 12, justifyContent: 'center', flexWrap: 'wrap' }}>
          <Link to="/register" className="cta-btn" style={{
            background: '#6366f1', color: '#fff', textDecoration: 'none',
            padding: '14px 28px', borderRadius: 12, fontWeight: 700,
            fontSize: 15, display: 'inline-flex', alignItems: 'center', gap: 8,
          }}>
            Start for free <ChevronRight size={16} />
          </Link>
          <Link to="/docs" className="outline-btn" style={{
            background: 'transparent', color: '#94a3b8', textDecoration: 'none',
            padding: '14px 28px', borderRadius: 12, fontWeight: 600,
            fontSize: 15, border: '1px solid #334155',
            display: 'inline-flex', alignItems: 'center', gap: 8,
          }}>
            How it works
          </Link>
        </div>
      </section>

      {/* How it works */}
      <section style={{ padding: '80px 24px', maxWidth: 900, margin: '0 auto' }}>
        <p style={{
          textAlign: 'center', color: '#6366f1', fontSize: 12,
          fontWeight: 700, letterSpacing: 2, textTransform: 'uppercase', marginBottom: 16,
        }}>
          How it works
        </p>
        <h2 style={{
          textAlign: 'center', fontFamily: "'Syne', sans-serif",
          fontSize: 'clamp(28px, 4vw, 40px)', fontWeight: 800,
          letterSpacing: '-1px', marginBottom: 56, color: '#f1f5f9',
        }}>
          Three steps to clarity
        </h2>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: 24 }}>
          {steps.map((s, i) => (
            <div key={i} style={{
              background: '#1e293b', borderRadius: 16, padding: 28,
              border: '1px solid #334155', position: 'relative',
            }}>
              <div style={{
                fontFamily: "'Syne', sans-serif", fontSize: 48,
                fontWeight: 800, color: 'rgba(99,102,241,0.12)',
                lineHeight: 1, marginBottom: 16, letterSpacing: '-2px',
              }}>
                {s.num}
              </div>
              <div style={{
                width: 40, height: 40, borderRadius: 10,
                background: 'rgba(99,102,241,0.15)', display: 'flex',
                alignItems: 'center', justifyContent: 'center',
                color: '#818cf8', marginBottom: 16,
              }}>
                {s.icon}
              </div>
              <p style={{ color: '#f1f5f9', fontWeight: 700, fontSize: 16, marginBottom: 8 }}>{s.title}</p>
              <p style={{ color: '#64748b', fontSize: 14, lineHeight: 1.6 }}>{s.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Features */}
      <section style={{ padding: '80px 24px', maxWidth: 1100, margin: '0 auto' }}>
        <p style={{
          textAlign: 'center', color: '#6366f1', fontSize: 12,
          fontWeight: 700, letterSpacing: 2, textTransform: 'uppercase', marginBottom: 16,
        }}>
          Features
        </p>
        <h2 style={{
          textAlign: 'center', fontFamily: "'Syne', sans-serif",
          fontSize: 'clamp(28px, 4vw, 40px)', fontWeight: 800,
          letterSpacing: '-1px', marginBottom: 56, color: '#f1f5f9',
        }}>
          Everything you need
        </h2>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: 16 }}>
          {features.map((f, i) => (
            <div key={i} className="feature-card" style={{
              background: '#1e293b', borderRadius: 14, padding: '24px 28px',
              border: '1px solid #334155',
            }}>
              <div style={{
                width: 44, height: 44, borderRadius: 10,
                background: 'rgba(99,102,241,0.12)', display: 'flex',
                alignItems: 'center', justifyContent: 'center',
                color: '#818cf8', marginBottom: 16,
              }}>
                {f.icon}
              </div>
              <p style={{ color: '#f1f5f9', fontWeight: 700, fontSize: 15, marginBottom: 8 }}>{f.title}</p>
              <p style={{ color: '#64748b', fontSize: 14, lineHeight: 1.6 }}>{f.desc}</p>
            </div>
          ))}
        </div>
      </section>

{/* Limitations / Honest Notes */}
<section style={{ padding: '0 24px 80px', maxWidth: 900, margin: '0 auto' }}>
  <p style={{
    textAlign: 'center', color: '#f59e0b', fontSize: 12,
    fontWeight: 700, letterSpacing: 2, textTransform: 'uppercase', marginBottom: 16,
  }}>
    Good to know
  </p>
  <h2 style={{
    textAlign: 'center', fontFamily: "'Syne', sans-serif",
    fontSize: 'clamp(24px, 3vw, 34px)', fontWeight: 800,
    letterSpacing: '-1px', marginBottom: 40, color: '#f1f5f9',
  }}>
    A few honest notes
  </h2>

  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: 16 }}>
    
    {/* Free tier cold start */}
    <div style={{
      background: '#1e293b', borderRadius: 14, padding: '22px 24px',
      border: '1px solid #854d0e',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 10 }}>
        <span style={{ fontSize: 18 }}>⏳</span>
        <p style={{ color: '#fbbf24', fontWeight: 700, fontSize: 14 }}>Cold Start Delay</p>
      </div>
      <p style={{ color: '#94a3b8', fontSize: 13, lineHeight: 1.7 }}>
        The backend runs on <strong style={{ color: '#f1f5f9' }}>Render's free tier</strong> and spins down after 15 minutes of inactivity.
        First request may take <strong style={{ color: '#f1f5f9' }}>30–60 seconds</strong> to wake up. Just wait a moment and try again.
      </p>
    </div>

    {/* Search limitation */}
    <div style={{
      background: '#1e293b', borderRadius: 14, padding: '22px 24px',
      border: '1px solid #1e3a5f',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 10 }}>
        <span style={{ fontSize: 18 }}>🔍</span>
        <p style={{ color: '#60a5fa', fontWeight: 700, fontSize: 14 }}>Search is Keyword-Based</p>
      </div>
      <p style={{ color: '#94a3b8', fontSize: 13, lineHeight: 1.7 }}>
        Search uses <strong style={{ color: '#f1f5f9' }}>MongoDB Atlas Search</strong> (BM25) instead of vector embeddings.
        It works well for direct keywords but won't match synonyms or paraphrased questions the way 
        SentenceTransformers would. Search with specific words from the meeting for best results.
      </p>
    </div>

    {/* Why Atlas Search */}
    <div style={{
      background: '#1e293b', borderRadius: 14, padding: '22px 24px',
      border: '1px solid #14532d',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 10 }}>
        <span style={{ fontSize: 18 }}>💡</span>
        <p style={{ color: '#4ade80', fontWeight: 700, fontSize: 14 }}>Why Atlas Search?</p>
      </div>
      <p style={{ color: '#94a3b8', fontSize: 13, lineHeight: 1.7 }}>
        SentenceTransformers require significant RAM to run embedding models on the server.
        On a free-tier deployment, this causes crashes. Atlas Search gives 
        <strong style={{ color: '#f1f5f9' }}> reliable full-text search</strong> with zero extra infrastructure — a deliberate tradeoff for stability.
      </p>
    </div>

  </div>
</section>


      {/* CTA Banner */}
      <section style={{ padding: '80px 24px' }}>
        <div style={{
          maxWidth: 700, margin: '0 auto', textAlign: 'center',
          background: 'linear-gradient(135deg, rgba(99,102,241,0.15), rgba(139,92,246,0.1))',
          border: '1px solid rgba(99,102,241,0.3)', borderRadius: 24, padding: '60px 40px',
        }}>
          <h2 style={{
            fontFamily: "'Syne', sans-serif", fontSize: 'clamp(26px, 4vw, 38px)',
            fontWeight: 800, letterSpacing: '-1px', marginBottom: 16, color: '#f1f5f9',
          }}>
            Ready to stop forgetting<br />what was decided?
          </h2>
          <p style={{ color: '#64748b', fontSize: 16, marginBottom: 32, lineHeight: 1.6 }}>
            Free to use. No credit card. Just upload and go.
          </p>
          <Link to="/register" className="cta-btn" style={{
            background: '#6366f1', color: '#fff', textDecoration: 'none',
            padding: '14px 32px', borderRadius: 12, fontWeight: 700, fontSize: 15,
            display: 'inline-flex', alignItems: 'center', gap: 8,
          }}>
            Create your account <ChevronRight size={16} />
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer style={{
        borderTop: '1px solid #1e293b', padding: '32px 48px',
        display: 'flex', justifyContent: 'space-between', alignItems: 'center',
        flexWrap: 'wrap', gap: 16,
      }}>
        <span style={{ fontFamily: "'Syne', sans-serif", fontSize: 18, fontWeight: 800, color: '#f1f5f9' }}>
          Meet<span style={{ color: '#6366f1' }}>IQ</span>
        </span>
        <div style={{ display: 'flex', gap: 24 }}>
          <Link to="/docs" style={{ color: '#475569', textDecoration: 'none', fontSize: 13 }}>Docs</Link>
          <Link to="/login" style={{ color: '#475569', textDecoration: 'none', fontSize: 13 }}>Sign in</Link>
          <Link to="/register" style={{ color: '#475569', textDecoration: 'none', fontSize: 13 }}>Register</Link>
        </div>
      </footer>
    </div>
  )
}