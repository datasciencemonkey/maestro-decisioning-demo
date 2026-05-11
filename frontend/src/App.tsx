import { Routes, Route } from 'react-router-dom'
import Landing from './pages/Landing'
import Layout from './store/Layout'
import Home from './store/pages/Home'
import Category from './store/pages/Category'
import Product from './store/pages/Product'

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Landing />} />
      <Route path="/store" element={<Layout />}>
        <Route index element={<Home />} />
        <Route path="photo-books" element={<Category />} />
        <Route path="product/:id" element={<Product />} />
      </Route>
    </Routes>
  )
}
