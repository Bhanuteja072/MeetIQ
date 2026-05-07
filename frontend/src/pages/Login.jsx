import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { loginUser } from '../api/client'
import { useAuth } from '../auth/AuthContext'
import toast from 'react-hot-toast'

export default function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const { login } = useAuth()
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!email || !password) return toast.error('Fill in all fields')
    setLoading(true)
    try {
      const data = await loginUser({ email, password })
      login(data.access_token, data.user)
      toast.success(`Welcome back, ${data.user.full_name || data.user.email}!`)
      navigate('/upload')
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Login failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{
      minHeight: '100vh', display: 'flex', alignItems: 'center',
      justifyContent: 'center', background: '#0f172a'
    }}>
      <div style={{
        background: '#1e293b', borderRadius: 16, padding: 40,
        width: '100%', maxWidth: 400, border: '1px solid #334155'
      }}>
        <h1 style={{ color: '#f1f5f9', fontSize: 24, fontWeight: 700, marginBottom: 8 }}>
          Welcome back
        </h1>
        <p style={{ color: '#64748b', marginBottom: 32 }}>Sign in to MeetIQ</p>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={e => setEmail(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleSubmit(e)}
            style={inputStyle}
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={e => setPassword(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleSubmit(e)}
            style={inputStyle}
          />
          <button onClick={handleSubmit} disabled={loading} style={btnStyle(loading)}>
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
          <p style={{ textAlign: 'center', marginTop: 16, fontSize: 13, color: '#475569' }}>
            <Link to="/forgot-password" style={{ color: '#6366f1' }}>
              Forgot password?
            </Link>
          </p>
        </div>

        <p style={{ color: '#64748b', textAlign: 'center', marginTop: 24, fontSize: 14 }}>
          Don't have an account?{' '}
          <Link to="/register" style={{ color: '#6366f1' }}>Sign up</Link>
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