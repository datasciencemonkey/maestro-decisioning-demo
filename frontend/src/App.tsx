import { Routes, Route } from 'react-router-dom'
import Landing from './pages/Landing'

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Landing />} />
      <Route path="/store/*" element={<div>Store coming soon</div>} />
    </Routes>
  )
}
