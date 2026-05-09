import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { registerUser } from '../api/client'
import { useAuth } from '../auth/AuthContext'
import toast from 'react-hot-toast'

export default function Register() {
  const [fullName, setFullName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const { login } = useAuth()
  const navigate = useNavigate()

  const handleSubmit = async () => {
    if (!email || !password) return toast.error('Email and password are required')
    if (password.length < 8) return toast.error('Password must be at least 8 characters')
    setLoading(true)
    try {
      const data = await registerUser({ email, password, full_name: fullName })
      login(data.access_token, data.user)
      toast.success('Account created!')
      navigate('/')
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Registration failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{
      minHeight: '100vh', display: 'flex', alignItems: 'center',
      justifyContent: 'center', background: '#0f172a', padding: '24px 16px'
    }}>
      <div style={{
        background: '#1e293b', borderRadius: 16, padding: 'clamp(24px, 5vw, 40px)',
        width: '100%', maxWidth: 400, border: '1px solid #334155'
      }}>
        <h1 style={{ color: '#f1f5f9', fontSize: 24, fontWeight: 700, marginBottom: 8 }}>
          Create account
        </h1>
        <p style={{ color: '#64748b', marginBottom: 32 }}>Start using MeetIQ for free</p>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          <input
            placeholder="Full name (optional)"
            value={fullName}
            onChange={e => setFullName(e.target.value)}
            style={inputStyle}
          />
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={e => setEmail(e.target.value)}
            style={inputStyle}
          />
          <input
            type="password"
            placeholder="Password (min 8 chars)"
            value={password}
            onChange={e => setPassword(e.target.value)}
            style={inputStyle}
          />
          <button onClick={handleSubmit} disabled={loading} style={btnStyle(loading)}>
            {loading ? 'Creating account...' : 'Create Account'}
          </button>
        </div>

        <p style={{ color: '#64748b', textAlign: 'center', marginTop: 24, fontSize: 14 }}>
          Already have an account?{' '}
          <Link to="/login" style={{ color: '#6366f1' }}>Sign in</Link>
        </p>
      </div>
    </div>
  )
}

const inputStyle = {
  padding: '12px 14px', borderRadius: 10,
  background: '#0f172a', border: '1px solid #334155',
  color: '#f1f5f9', fontSize: 15, outline: 'none', width: '100%',
  boxSizing: 'border-box'
}

const btnStyle = (loading) => ({
  padding: '12px', borderRadius: 10, border: 'none',
  background: loading ? '#334155' : '#6366f1',
  color: '#fff', fontWeight: 700, fontSize: 16,
  cursor: loading ? 'not-allowed' : 'pointer', width: '100%'
})