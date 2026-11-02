import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import client from '../api/client';
import ProductCard from '../components/ProductCard';
import './Home.css';

export default function Home() {
  const [featuredProducts, setFeaturedProducts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchFeatured = async () => {
      try {
        const response = await client.get('/products/featured/');
        setFeaturedProducts(response.data.data);
      } catch (error) {
        console.error('Failed to fetch featured products', error);
      } finally {
        setLoading(false);
      }
    };

    fetchFeatured();
  }, []);

  return (
    <div className="home-page">
      {/* Hero Section */}
      <section className="hero">
        <div className="hero-content">
          <h1>Light up your space with elegance</h1>
          <p>Hand-poured artisanal candles crafted with premium fragrances and sustainable ingredients.</p>
          <Link to="/products" className="btn btn-primary hero-btn">
            Shop the Collection
          </Link>
        </div>
      </section>

      {/* Featured Products */}
      <section className="featured-section container">
        <div className="section-header">
          <h2>Curated For You</h2>
          <Link to="/products" className="view-all-link">View All Products →</Link>
        </div>

        {loading ? (
          <div className="loading-state">Loading premium selection...</div>
        ) : (
          <div className="product-grid">
            {featuredProducts.map((product) => (
              <ProductCard key={product.id} product={product} />
            ))}
          </div>
        )}
      </section>

      {/* Features/Values */}
      <section className="values-section">
        <div className="container values-grid">
          <div className="value-item">
            <h3>Premium Fragrances</h3>
            <p>Complex, sophisticated scent profiles crafted by master perfumers.</p>
          </div>
          <div className="value-item">
            <h3>Sustainable Wax</h3>
            <p>Clean-burning natural soy and coconut wax blend for a longer, cleaner burn.</p>
          </div>
          <div className="value-item">
            <h3>Hand-Poured</h3>
            <p>Crafted with care in small batches to ensure the highest quality.</p>
          </div>
        </div>
      </section>
    </div>
  );
}
