import { useState, useEffect, useRef } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { Upload, Archive, Search, Brain, Menu, X, LogOut } from 'lucide-react'
import { useAuth } from '../auth/AuthContext'
import { useIsMobile } from '../hooks/useIsMobile'

const links = [
  { to: '/upload',  label: 'Upload',   icon: Upload  },
  { to: '/archive', label: 'Meetings', icon: Archive },
  { to: '/search',  label: 'Search',   icon: Search  },
]

export default function Navbar() {
  const { pathname } = useLocation()
  const { user, logout } = useAuth()
  const { isMobile } = useIsMobile()
  const [menuOpen, setMenuOpen] = useState(false)
  const menuRef = useRef(null)

  // Close menu on route change
  useEffect(() => { setMenuOpen(false) }, [pathname])

  // Close menu when screen goes desktop-sized
  useEffect(() => { if (!isMobile) setMenuOpen(false) }, [isMobile])

  // Close menu on outside click
  useEffect(() => {
    if (!menuOpen) return
    const handler = (e) => {
      if (menuRef.current && !menuRef.current.contains(e.target)) {
        setMenuOpen(false)
      }
    }
    document.addEventListener('mousedown', handler)
    document.addEventListener('touchstart', handler)
    return () => {
      document.removeEventListener('mousedown', handler)
      document.removeEventListener('touchstart', handler)
    }
  }, [menuOpen])

  // Prevent body scroll when mobile menu is open
  useEffect(() => {
    document.body.style.overflow = menuOpen ? 'hidden' : ''
    return () => { document.body.style.overflow = '' }
  }, [menuOpen])

  return (
    <nav ref={menuRef} style={{
      background: '#0f172a',
      padding: '0 var(--page-px)',
      display: 'flex',
      alignItems: 'center',
      height: 'var(--navbar-height)',
      position: 'sticky',
      top: 0,
      zIndex: 200,
      borderBottom: menuOpen ? '1px solid #1e293b' : '1px solid transparent',
      transition: 'border-color 0.15s',
    }}>

      {/* ── Logo ── */}
      <Link to="/upload" style={{
        display: 'flex', alignItems: 'center', gap: 8,
        color: '#6366f1', fontWeight: 700, fontSize: 18,
        textDecoration: 'none', flexShrink: 0,
      }}>
        <Brain size={22} /> MeetIQ
      </Link>

      {/* ── Desktop nav (hidden on mobile) ── */}
      {!isMobile && (
        <>
          <div style={{ display: 'flex', gap: 4, marginLeft: 'auto' }}>
            {links.map(({ to, label, icon: Icon }) => (
              <Link key={to} to={to} style={{
                display: 'flex', alignItems: 'center', gap: 6,
                padding: '6px 14px', borderRadius: 8,
                color: pathname === to ? '#6366f1' : '#94a3b8',
                background: pathname === to ? '#1e1b4b' : 'transparent',
                textDecoration: 'none', fontSize: 14, fontWeight: 500,
                transition: 'all 0.15s',
              }}>
                <Icon size={15} /> {label}
              </Link>
            ))}
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginLeft: 16 }}>
            <span style={{ color: '#64748b', fontSize: 14 }}>{user?.email}</span>
            <button onClick={logout} style={{
              background: '#1e293b', border: '1px solid #334155',
              color: '#94a3b8', borderRadius: 8, padding: '6px 14px',
              cursor: 'pointer', fontSize: 13,
            }}>
              Sign out
            </button>
          </div>
        </>
      )}

      {/* ── Hamburger button (mobile only) ── */}
      {isMobile && (
        <button
          onClick={() => setMenuOpen(o => !o)}
          aria-label={menuOpen ? 'Close menu' : 'Open menu'}
          aria-expanded={menuOpen}
          style={{
            marginLeft: 'auto',
            background: 'none',
            border: 'none',
            color: '#94a3b8',
            cursor: 'pointer',
            padding: 8,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            borderRadius: 8,
            minHeight: 44,
            minWidth: 44,
          }}
        >
          {menuOpen ? <X size={22} /> : <Menu size={22} />}
        </button>
      )}

      {/* ── Mobile dropdown menu ── */}
      {isMobile && menuOpen && (
        <div style={{
          position: 'fixed',
          top: 'var(--navbar-height)',
          left: 0,
          right: 0,
          bottom: 0,
          background: '#0f172a',
          zIndex: 199,
          display: 'flex',
          flexDirection: 'column',
          padding: '8px 0 24px',
          overflowY: 'auto',
          borderTop: '1px solid #1e293b',
          animation: 'slideDown 0.18s ease',
        }}>

          {/* Nav links */}
          {links.map(({ to, label, icon: Icon }) => {
            const active = pathname === to
            return (
              <Link key={to} to={to} style={{
                display: 'flex', alignItems: 'center', gap: 14,
                padding: '14px var(--page-px)',
                color: active ? '#6366f1' : '#94a3b8',
                background: active ? 'rgba(99,102,241,0.08)' : 'transparent',
                textDecoration: 'none',
                fontSize: 16,
                fontWeight: active ? 600 : 500,
                borderLeft: active ? '3px solid #6366f1' : '3px solid transparent',
                transition: 'all 0.15s',
                minHeight: 52,
              }}>
                <Icon size={20} /> {label}
              </Link>
            )
          })}

          {/* Divider */}
          <div style={{
            height: 1,
            background: '#1e293b',
            margin: '12px 0',
          }} />

          {/* User email */}
          {user?.email && (
            <div style={{
              padding: '4px var(--page-px) 8px',
              color: '#475569',
              fontSize: 13,
            }}>
              {user.email}
            </div>
          )}

          {/* Sign out */}
          <button onClick={() => { logout(); setMenuOpen(false) }} style={{
            display: 'flex', alignItems: 'center', gap: 12,
            margin: '0 var(--page-px)',
            padding: '12px 16px',
            background: '#1e293b',
            border: '1px solid #334155',
            borderRadius: 10,
            color: '#94a3b8',
            fontSize: 15,
            fontWeight: 500,
            cursor: 'pointer',
            minHeight: 48,
          }}>
            <LogOut size={18} /> Sign out
          </button>
        </div>
      )}

      {/* Slide-down animation */}
      <style>{`
        @keyframes slideDown {
          from { opacity: 0; transform: translateY(-8px); }
          to   { opacity: 1; transform: translateY(0); }
        }
      `}</style>
    </nav>
  )
}