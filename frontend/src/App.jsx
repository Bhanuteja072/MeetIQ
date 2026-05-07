import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import { AuthProvider } from './auth/AuthContext'
import ProtectedRoute from './auth/ProtectedRoute'
import Navbar from './components/Navbar'
import Upload from './pages/Upload'
import Archive from './pages/Archive'
import MeetingDetail from './pages/MeetingDetail'
import Search from './pages/Search'
import NotFound from './pages/NotFound'
import Login from './pages/Login'           // ← was missing
import Register from './pages/Register'     // ← was missing
import ForgotPassword from './pages/ForgotPassword'
import Landing from './pages/Landing'   // ← add this
import Docs from './pages/Docs' 

// Pages that use their OWN nav (no shared Navbar/main wrapper)
const PUBLIC_STANDALONE = ['/', '/docs', '/login', '/register', '/forgot-password']

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>              {/* ← moved UP, wraps everything including Navbar */}
        <Toaster position="top-right" />
        <Routes>
          {/* ── Standalone public pages (have their own nav) ── */}
          <Route path="/"                 element={<Landing />} />
          <Route path="/docs"             element={<Docs />} />
          <Route path="/login"            element={<Login />} />
          <Route path="/register"         element={<Register />} />
          <Route path="/forgot-password"  element={<ForgotPassword />} />
          {/* ── App pages (shared Navbar + main wrapper) ── */}
          <Route path="/*" element={
            <>
              <Navbar />
              <main style={{ maxWidth: 960, margin: '0 auto', padding: '24px 16px' }}>
                <Routes>
                  <Route path="/upload"        element={<ProtectedRoute><Upload /></ProtectedRoute>} />
                  <Route path="/archive"       element={<ProtectedRoute><Archive /></ProtectedRoute>} />
                  <Route path="/meetings/:id"  element={<ProtectedRoute><MeetingDetail /></ProtectedRoute>} />
                  <Route path="/search"        element={<ProtectedRoute><Search /></ProtectedRoute>} />
                  <Route path="*"              element={<NotFound />} />
                </Routes>
              </main>
            </>
          } />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  )
}