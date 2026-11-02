import { Link } from 'react-router-dom';
import { useCart } from '../context/CartContext';
import './ProductCard.css';
import ProductImage from './ProductImage';

export default function ProductCard({ product }) {
  const { addToCart } = useCart();

  const isOutOfStock = product.stock_status === 'OUT_OF_STOCK';
  const isLowStock = product.stock_status === 'LOW_STOCK';

  const handleAddToCart = (e) => {
    e.preventDefault(); // Prevent navigating to product detail
    e.stopPropagation();
    if (!isOutOfStock) {
      addToCart(product.id, 1);
    }
  };

  return (
    <Link to={`/products/${product.slug}`} className="product-card">
      <div className="product-image-container">
        {product.image ? (
          <ProductImage src={product.image} alt={product.name} className="product-image" />
        ) : (
          <div className="product-image-placeholder">
            <span>Wax & Warmth</span>
          </div>
        )}

        {/* Badges */}
        <div className="product-badges">
          {product.is_featured && <span className="badge featured">Featured</span>}
          {isOutOfStock ? (
            <span className="badge out-of-stock">Sold Out</span>
          ) : isLowStock ? (
            <span className="badge low-stock">Low Stock</span>
          ) : null}
        </div>

        {/* Quick Add Button */}
        {!isOutOfStock && (
          <button
            className="quick-add-btn"
            onClick={handleAddToCart}
          >
            Add to Cart
          </button>
        )}
      </div>

      <div className="product-info">
        <h3 className="product-title">{product.name}</h3>

        <p className="product-meta">
          {product.scent_family}
          {product.scent_notes_list && product.scent_notes_list.length > 0 && (
            <> &middot; {product.scent_notes_list[0]}</>
          )}
        </p>

        <div className="product-price-row">
          <span className="product-price">₹{product.price}</span>
          <span className="product-availability">
            <span className={`status-dot ${product.stock_status.toLowerCase()}`}></span>
            {isOutOfStock ? 'Out of Stock' : isLowStock ? 'Few Left' : 'In Stock'}
          </span>
        </div>
      </div>
    </Link>
  );
}
