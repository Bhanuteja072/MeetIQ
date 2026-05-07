import { Link, useLocation } from 'react-router-dom'
import { Upload, Archive, Search, Brain } from 'lucide-react'
import { useAuth } from '../auth/AuthContext'   // ← add this import


const links = [
  { to: '/upload', label: 'Upload', icon: Upload },
  { to: '/archive', label: 'Meetings', icon: Archive },
  { to: '/search', label: 'Search', icon: Search },
]

export default function Navbar() {
  const { pathname } = useLocation()
  const { user, logout } = useAuth()

  return (
    <nav style={{
      background: '#0f172a', padding: '0 24px',
      display: 'flex', alignItems: 'center', gap: 32,
      height: 56, position: 'sticky', top: 0, zIndex: 100
    }}>
      <Link to="/upload" style={{
        display: 'flex', alignItems: 'center', gap: 8,
        color: '#6366f1', fontWeight: 700, fontSize: 18,
        textDecoration: 'none'
      }}>
        <Brain size={22} /> MeetIQ
      </Link>

      <div style={{ display: 'flex', gap: 4, marginLeft: 'auto' }}>
        {links.map(({ to, label, icon: Icon }) => (
          <Link key={to} to={to} style={{
            display: 'flex', alignItems: 'center', gap: 6,
            padding: '6px 14px', borderRadius: 8,
            color: pathname === to ? '#6366f1' : '#94a3b8',
            background: pathname === to ? '#1e1b4b' : 'transparent',
            textDecoration: 'none', fontSize: 14, fontWeight: 500,
            transition: 'all 0.15s'
          }}>
            <Icon size={15} /> {label}
          </Link>
        ))}
      </div>
      <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
        <span style={{ color: '#64748b', fontSize: 14 }}>{user?.email}</span>
        <button onClick={logout} style={{
          background: '#1e293b', border: '1px solid #334155',
          color: '#94a3b8', borderRadius: 8, padding: '6px 14px',
          cursor: 'pointer', fontSize: 13
        }}>
          Sign out
        </button>
      </div>
    </nav>
  )
}