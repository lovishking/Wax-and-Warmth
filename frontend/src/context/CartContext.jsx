import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import client, { getApiError } from '../api/client';
import { useAuth } from './AuthContext';

const CartContext = createContext(null);

export function CartProvider({ children }) {
  const [cart, setCart] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [isOpen, setIsOpen] = useState(false);
  const { user, loading: authLoading } = useAuth();

  const fetchCart = useCallback(async () => {
    if (!user) {
      setCart(null);
      setError('');
      return null;
    }
    setLoading(true);
    setError('');
    try {
      const { data } = await client.get('/cart/');
      setCart(data.data);
      return data.data;
    } catch (requestError) {
      setError(getApiError(requestError, 'Could not load your cart.'));
      throw requestError;
    } finally {
      setLoading(false);
    }
  }, [user]);

  useEffect(() => {
    if (!authLoading) fetchCart().catch(() => {});
  }, [authLoading, fetchCart]);

  const addToCart = useCallback(async (productId, quantity = 1) => {
    if (!user) return { success: false, message: 'Sign in to add items to your saved cart.' };
    setError('');
    try {
      const { data } = await client.post('/cart/add/', { product_id: productId, quantity });
      setCart(data.data);
      setIsOpen(true);
      return { success: true };
    } catch (requestError) {
      const message = getApiError(requestError, 'Could not add this product to your cart.');
      setError(message);
      return { success: false, message };
    }
  }, [user]);

  const updateQuantity = useCallback(async (itemId, quantity) => {
    if (quantity < 1) return;
    setError('');
    try {
      const { data } = await client.patch(`/cart/items/${itemId}/`, { quantity });
      setCart(data.data);
    } catch (requestError) {
      setError(getApiError(requestError, 'Could not update the cart quantity.'));
    }
  }, []);

  const removeItem = useCallback(async (itemId) => {
    setError('');
    try {
      const { data } = await client.delete(`/cart/items/${itemId}/remove/`);
      setCart(data.data);
    } catch (requestError) {
      setError(getApiError(requestError, 'Could not remove this item.'));
    }
  }, []);

  const clearCart = useCallback(async () => {
    setError('');
    try {
      await client.post('/cart/clear/');
      setCart((current) => current ? { ...current, items: [], total_items: 0, subtotal: '0.00' } : current);
    } catch (requestError) {
      setError(getApiError(requestError, 'Could not clear the cart.'));
      throw requestError;
    }
  }, []);

  const value = useMemo(() => ({
    cart, loading, error, isOpen, setIsOpen, addToCart, updateQuantity,
    removeItem, clearCart, refreshCart: fetchCart,
  }), [cart, loading, error, isOpen, addToCart, updateQuantity, removeItem, clearCart, fetchCart]);

  return <CartContext.Provider value={value}>{children}</CartContext.Provider>;
}

export const useCart = () => useContext(CartContext);
