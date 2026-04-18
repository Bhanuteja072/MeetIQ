import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import Navbar from './components/Navbar'
import Upload from './pages/Upload'
import Archive from './pages/Archive'
import MeetingDetail from './pages/MeetingDetail'
import Search from './pages/Search'
import NotFound from './pages/NotFound'

export default function App() {
  return (
    <BrowserRouter>
      <Toaster position="top-right" />
      <Navbar />
      <main className="max-w-5xl mx-auto px-4 py-8">
        <Routes>
          <Route path="/" element={<Upload />} />
          <Route path="/archive" element={<Archive />} />
          <Route path="/meetings/:id" element={<MeetingDetail />} />
          <Route path="/search" element={<Search />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </main>
    </BrowserRouter>
  )
}