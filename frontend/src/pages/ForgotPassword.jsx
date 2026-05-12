import { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
// import axios from 'axios'
import api from '../api/client'  // ← use the shared instance
import toast from 'react-hot-toast'
// import { registerUser } from '../api/client'  // just to import the file isn't needed

// const api = axios.create({ baseURL: '/api' })
const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

export default function ForgotPassword() {
  const navigate = useNavigate()
  const [step, setStep] = useState(1)       // 1 | 2 | 3
  const [email, setEmail] = useState('')
  const [otp, setOtp] = useState('')
  const [resetToken, setResetToken] = useState(sessionStorage.getItem('reset_token') || '')
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)

  const [resendCooldown, setResendCooldown] = useState(0)
  const [loading, setLoading] = useState(false)
    // Cooldown timer
  useEffect(() => {
    if (resendCooldown <= 0) return

    const timer = setInterval(() => {
      setResendCooldown(prev => prev - 1)
    }, 1000)

    return () => clearInterval(timer)
  }, [resendCooldown])

  const validatePassword = password => {
    return (
      password.length >= 8 &&
      /[A-Z]/.test(password) &&
      /[a-z]/.test(password) &&
      /\d/.test(password)
    )
  }

  const getErrorMessage = err => {
    return (
      err?.response?.data?.detail ||
      err?.message ||
      'Something went wrong'
    )
  }


  // ── Step 1: Send OTP ──────────────────────────────────
  const handleSendOtp = async () => {
    const normalizedEmail = email.trim().toLowerCase()
    if (!normalizedEmail) return toast.error('Please enter your email')
    if (!EMAIL_REGEX.test(normalizedEmail)) return toast.error('Please enter a valid email')
    if (loading) return
    setLoading(true)
    try {
      await api.post('/auth/forgot-password', { email: normalizedEmail })
      toast.success('OTP sent! Check your inbox.')
      setStep(2)
      setResendCooldown(60) // 60 second cooldown
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Something went wrong')
    } finally {
      setLoading(false)
    }
  }

  // ── Step 2: Verify OTP ────────────────────────────────
  const handleVerifyOtp = async () => {
    if (otp.length !== 6) return toast.error('Enter the 6-digit OTP')
    if (loading) return
    setLoading(true)
    try {
      const res = await api.post('/auth/verify-otp', { email, otp })
      setResetToken(res.data.reset_token)
      sessionStorage.setItem('reset_token', res.data.reset_token)
      toast.success('OTP verified!')
      setStep(3)
    } catch (err) {
      toast.error(getErrorMessage(err))
    } finally {
      setLoading(false)
    }
  }

  // ── Step 3: Reset Password ────────────────────────────
  const handleResetPassword = async () => {
    if(!validatePassword(newPassword)) {
      toast.error('Password must be at least 8 characters and include uppercase, lowercase, and a number')
      return
    }
    if (newPassword !== confirmPassword) return toast.error('Passwords do not match')
    if (loading) return
    setLoading(true)
    try {
      await api.post('/auth/reset-password', {
        reset_token: resetToken,
        new_password: newPassword,
      })
      toast.success('Password reset! Please log in.')
      navigate('/login')
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Something went wrong')
    } finally {
      setLoading(false)
    }
  }

  // ── Shared styles ─────────────────────────────────────
  const inputStyle = {
    width: '100%', padding: '10px 14px', borderRadius: 10,
    background: '#1e293b', border: '1px solid #334155',
    color: '#f1f5f9', fontSize: 15, outline: 'none',
    boxSizing: 'border-box', marginBottom: 12,
  }

  const btnStyle = (disabled) => ({
    width: '100%', padding: '11px 0', borderRadius: 10,
    background: disabled ? '#334155' : '#6366f1',
    color: '#fff', border: 'none',
    cursor: disabled ? 'not-allowed' : 'pointer',
    fontWeight: 700, fontSize: 15, marginTop: 4,
  })

  const stepLabels = ['Email', 'Verify OTP', 'New Password']

  return (
    <div style={{
      minHeight: '100vh', display: 'flex', alignItems: 'center',
      justifyContent: 'center', background: '#0f172a', padding: 'clamp(12px, 4vw, 24px)',
    }}>
      <div style={{ width: '100%', maxWidth: 420 }}>

        {/* Logo */}
        <p style={{
          color: '#6366f1', fontWeight: 800, fontSize: 22,
          textAlign: 'center', marginBottom: 32, letterSpacing: -0.5,
        }}>
          MeetIQ
        </p>

        {/* Step indicators */}
        <div style={{
          display: 'flex', alignItems: 'center',
          justifyContent: 'center', marginBottom: 32, gap: 0,
        }}>
          {stepLabels.map((label, i) => {
            const n = i + 1
            const done = step > n
            const active = step === n
            return (
              <div key={n} style={{ display: 'flex', alignItems: 'center' }}>
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                  <div style={{
                    width: 28, height: 28, borderRadius: '50%',
                    background: done ? '#6366f1' : active ? '#1e1b4b' : '#1e293b',
                    border: `2px solid ${done || active ? '#6366f1' : '#334155'}`,
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    color: done ? '#fff' : active ? '#a78bfa' : '#475569',
                    fontSize: 12, fontWeight: 700,
                  }}>
                    {done ? '✓' : n}
                  </div>
                  <span style={{
                    fontSize: 11, marginTop: 4,
                    color: active ? '#a78bfa' : done ? '#6366f1' : '#475569',
                  }}>
                    {label}
                  </span>
                </div>
                {i < 2 && (
                  <div style={{
                    width: 48, height: 2, marginBottom: 18,
                    background: step > n ? '#6366f1' : '#334155',
                  }} />
                )}
              </div>
            )
          })}
        </div>

        {/* Card */}
        <div style={{
          background: '#1e293b', borderRadius: 14,
          border: '1px solid #334155', padding: '32px 28px',
        }}>

          {/* ── Step 1 ── */}
          {step === 1 && (
            <>
              <h2 style={{ color: '#f1f5f9', fontSize: 20, fontWeight: 700, marginBottom: 6 }}>
                Forgot password?
              </h2>
              <p style={{ color: '#64748b', fontSize: 14, marginBottom: 24 }}>
                Enter your registered email and we'll send you a one-time code.
              </p>
              <input
                style={inputStyle}
                type="email"
                placeholder="you@example.com"
                value={email}
                onChange={e => setEmail(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && handleSendOtp()}
                autoFocus
              />
              <button
                style={btnStyle(loading || !email.trim())}
                disabled={loading || !email.trim()}
                onClick={handleSendOtp}
              >
                {loading ? 'Sending...' : 'Send OTP'}
              </button>
            </>
          )}

          {/* ── Step 2 ── */}
          {step === 2 && (
            <>
              <h2 style={{ color: '#f1f5f9', fontSize: 20, fontWeight: 700, marginBottom: 6 }}>
                Enter the OTP
              </h2>
              <p style={{ color: '#64748b', fontSize: 14, marginBottom: 24 }}>
                We sent a 6-digit code to <span style={{ color: '#a78bfa' }}>{email}</span>.
                It expires in 10 minutes.
              </p>
              <input
                style={{ ...inputStyle, letterSpacing: 8, fontSize: 22, textAlign: 'center' }}
                type="text"
                inputMode="numeric"
                maxLength={6}
                placeholder="······"
                value={otp}
                onChange={e => setOtp(e.target.value.replace(/\D/g, '').slice(0, 6))}
                onKeyDown={e => e.key === 'Enter' && handleVerifyOtp()}
                autoFocus
              />
              <button
                style={btnStyle(loading || otp.length !== 6)}
                disabled={loading || otp.length !== 6}
                onClick={handleVerifyOtp}
              >
                {loading ? 'Verifying...' : 'Verify OTP'}
              </button>
              <button
                onClick={() => { setOtp(''); handleSendOtp() }}
                style={{
                  width: '100%', background: 'none', border: 'none',
                  color: '#475569', fontSize: 13, cursor: 'pointer',
                  marginTop: 12, padding: 0,
                }}
              >
                Didn't receive it? Resend OTP
              </button>
            </>
          )}

          {/* ── Step 3 ── */}
          {step === 3 && (
            <>
              <h2 style={{ color: '#f1f5f9', fontSize: 20, fontWeight: 700, marginBottom: 6 }}>
                Set new password
              </h2>
              <p style={{ color: '#64748b', fontSize: 14, marginBottom: 24 }}>
                Choose a strong password — at least 8 characters.
              </p>
              <input
                style={inputStyle}
                type="password"
                placeholder="New password"
                value={newPassword}
                onChange={e => setNewPassword(e.target.value)}
                autoFocus
              />
              <input
                style={inputStyle}
                type="password"
                placeholder="Confirm new password"
                value={confirmPassword}
                onChange={e => setConfirmPassword(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && handleResetPassword()}
              />
              {/* Password match indicator */}
              {confirmPassword && (
                <p style={{
                  fontSize: 12, marginBottom: 8, marginTop: -6,
                  color: newPassword === confirmPassword ? '#22c55e' : '#ef4444',
                }}>
                  {newPassword === confirmPassword ? '✓ Passwords match' : '✗ Passwords do not match'}
                </p>
              )}
              <button
                style={btnStyle(loading || !newPassword || !confirmPassword)}
                disabled={loading || !newPassword || !confirmPassword}
                onClick={handleResetPassword}
              >
                {loading ? 'Resetting...' : 'Reset Password'}
              </button>
            </>
          )}
        </div>

        {/* Back to login */}
        <p style={{ textAlign: 'center', marginTop: 20, color: '#475569', fontSize: 14 }}>
          <Link to="/login" style={{ color: '#6366f1' }}>← Back to login</Link>
        </p>

      </div>
    </div>
  )
}