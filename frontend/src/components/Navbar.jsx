import { Link } from 'react-router-dom';
import { ShoppingBag, User as UserIcon, Menu } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { useCart } from '../context/CartContext';
import './Navbar.css';

export default function Navbar() {
  const { user, isAdmin } = useAuth();
  const { cart, setIsOpen } = useCart();

  return (
    <nav className="navbar">
      <div className="container navbar-container">
        <div className="navbar-left">
          <button className="mobile-menu-btn">
            <Menu size={24} />
          </button>
          <Link to="/" className="brand-logo">
            Wax & Warmth
          </Link>
          <div className="nav-links">
            <Link to="/products" className="nav-link">Shop All</Link>
            <Link to="/products?category=seasonal" className="nav-link">Seasonal</Link>
          </div>
        </div>

        <div className="navbar-right">
          {isAdmin && (
            <Link to="/admin" className="nav-link admin-link">Dashboard</Link>
          )}

          {user ? (
            <Link to="/orders" className="icon-btn">
              <UserIcon size={20} />
            </Link>
          ) : (
            <Link to="/login" className="nav-link">Login</Link>
          )}

          <button className="icon-btn cart-btn" onClick={() => setIsOpen(true)}>
            <ShoppingBag size={20} />
            {cart?.total_items > 0 && (
              <span className="cart-badge">{cart.total_items}</span>
            )}
          </button>
        </div>
      </div>
    </nav>
  );
}
