import { Routes, Route } from 'react-router-dom';
import { CartProvider } from './context/CartContext';
import MenuPage from './pages/MenuPage';
import HomePage from './pages/HomePage';
import CartPage from './pages/CartPage';

export default function App() {
  return (
    <CartProvider>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/menu/:slug" element={<MenuPage />} />
        <Route path="/menu/:slug/cart" element={<CartPage />} />
      </Routes>
    </CartProvider>
  );
}
