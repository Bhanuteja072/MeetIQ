const colors = {
  uploaded:     { bg: '#1e3a5f', text: '#60a5fa' },
  transcribing: { bg: '#1c3a2a', text: '#4ade80' },
  completed:    { bg: '#14532d', text: '#86efac' },
  failed:       { bg: '#450a0a', text: '#fca5a5' },
  analyzing:    { bg: '#2d1f63', text: '#a78bfa' },
}

export default function StatusBadge({ status }) {
  const c = colors[status] || { bg: '#1e293b', text: '#94a3b8' }
  return (
    <span style={{
      background: c.bg, color: c.text,
      padding: '2px 10px', borderRadius: 999,
      fontSize: 12, fontWeight: 600, textTransform: 'uppercase'
    }}>
      {status}
    </span>
  )
}