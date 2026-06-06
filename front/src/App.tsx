import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { Layout } from './components/Layout'
import { ArtistsPage } from './pages/ArtistsPage'
import { DashboardPage } from './pages/DashboardPage'
import { SongsPage } from './pages/SongsPage'
import { TagsPage } from './pages/TagsPage'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route index element={<DashboardPage />} />
          <Route path="songs" element={<SongsPage />} />
          <Route path="artists" element={<ArtistsPage />} />
          <Route path="tags" element={<TagsPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App
