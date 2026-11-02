import { X, Plus, Minus, ShoppingBag } from 'lucide-react';
import { useCart } from '../context/CartContext';
import { Link, useNavigate } from 'react-router-dom';
import './CartDrawer.css';
import ProductImage from './ProductImage';

export default function CartDrawer() {
  const { cart, isOpen, setIsOpen, updateQuantity, removeItem, clearCart } = useCart();
  const navigate = useNavigate();

  if (!isOpen) return null;

  const handleCheckout = () => {
    setIsOpen(false);
    navigate('/checkout');
  };

  return (
    <>
      <div className="cart-overlay" onClick={() => setIsOpen(false)} />
      <div className="cart-drawer">
        <div className="cart-header">
          <h2>Your Cart</h2>
          <button className="icon-btn" onClick={() => setIsOpen(false)}>
            <X size={24} />
          </button>
        </div>

        {!cart || cart.items.length === 0 ? (
          <div className="cart-empty">
            <ShoppingBag size={48} className="cart-empty-icon" />
            <p>Your cart is empty.</p>
            <button className="btn btn-primary" onClick={() => setIsOpen(false)}>
              Continue Shopping
            </button>
          </div>
        ) : (
          <>
            <div className="cart-items">
              {cart.items.map((item) => (
                <div key={item.id} className="cart-item">
                  <div className="cart-item-image">
                    {item.product_details?.image ? (
                      <ProductImage src={item.product_details.image} alt={item.product_details.name} />
                    ) : (
                      <div className="cart-item-placeholder" />
                    )}
                  </div>
                  <div className="cart-item-info">
                    <div className="cart-item-title-row">
                      <Link
                        to={`/products/${item.product_details?.slug}`}
                        onClick={() => setIsOpen(false)}
                      >
                        <h4>{item.product_details?.name}</h4>
                      </Link>
                      <button
                        className="remove-btn"
                        onClick={() => removeItem(item.id)}
                      >
                        <X size={16} />
                      </button>
                    </div>
                    <p className="cart-item-price">₹{item.product_details?.price}</p>

                    <div className="cart-item-actions">
                      <div className="quantity-controls">
                        <button
                          onClick={() => updateQuantity(item.id, item.quantity - 1)}
                          disabled={item.quantity <= 1}
                        >
                          <Minus size={14} />
                        </button>
                        <span>{item.quantity}</span>
                        <button
                          onClick={() => updateQuantity(item.id, item.quantity + 1)}
                          disabled={item.quantity >= item.product_details?.available_quantity}
                        >
                          <Plus size={14} />
                        </button>
                      </div>
                      <span className="cart-item-total">₹{item.line_total}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            <div className="cart-footer">
              <div className="cart-subtotal">
                <span>Subtotal</span>
                <span>₹{cart.subtotal}</span>
              </div>
              <p className="cart-taxes-note">Taxes and shipping calculated at checkout</p>
              <button className="btn btn-primary cart-checkout-btn" onClick={handleCheckout}>
                Proceed to Checkout
              </button>
            </div>
          </>
        )}
      </div>
    </>
  );
}
