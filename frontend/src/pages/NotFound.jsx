import { Link } from 'react-router-dom'

export default function NotFound() {
  return (
    <div style={{ textAlign: 'center', padding: '80px 0' }}>
      <p style={{ fontSize: 64, marginBottom: 16 }}>404</p>
      <p style={{ color: '#64748b', marginBottom: 24 }}>Page not found</p>
      <Link to="/" style={{ color: '#6366f1' }}>Go home →</Link>
    </div>
  )
}