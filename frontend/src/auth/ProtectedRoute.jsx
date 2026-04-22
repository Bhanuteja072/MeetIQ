import { Navigate } from 'react-router-dom'
import { useAuth } from './AuthContext'

export default function ProtectedRoute({ children }) {
  const { token, loading } = useAuth()

  if (loading) return null  // wait for localStorage restore

  if (!token) return <Navigate to="/login" replace />

  return children
}