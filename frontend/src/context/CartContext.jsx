import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import client, { getApiError } from '../api/client';
import { useAuth } from './AuthContext';

const CartContext = createContext(null);
const GUEST_CART_KEY = 'wax-warmth-guest-cart';
const readGuestCart = () => { try { return JSON.parse(localStorage.getItem(GUEST_CART_KEY) || '[]'); } catch { return []; } };
const guestTotals = (items) => ({ items, total_items: items.reduce((sum, item) => sum + item.quantity, 0), subtotal: items.reduce((sum, item) => sum + Number(item.line_total || 0), 0).toFixed(2) });

export function CartProvider({ children }) {
  const [cart, setCart] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [isOpen, setIsOpen] = useState(false);
  const { user, loading: authLoading } = useAuth();

  const fetchCart = useCallback(async () => {
    if (!user) {
      setCart(guestTotals(readGuestCart()));
      setError('');
      return null;
    }
    setLoading(true);
    setError('');
    try {
      const { data } = await client.get('/cart/');
      let remoteCart = data.data;
      const guestItems = readGuestCart();
      if (guestItems.length) {
        for (const item of guestItems) {
          await client.post('/cart/add/', { product_id: item.product_details.id, quantity: item.quantity });
        }
        localStorage.removeItem(GUEST_CART_KEY);
        const refreshed = await client.get('/cart/');
        remoteCart = refreshed.data.data;
      }
      setCart(remoteCart);
      return remoteCart;
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

  const addToCart = useCallback(async (product, quantity = 1) => {
    const productId = typeof product === 'object' ? product?.id : product;
    if (!user) {
      const snapshot = typeof product === 'object' ? product : { id: productId, name: 'Product', price: 0, available_quantity: quantity };
      const items = readGuestCart();
      const existing = items.find((item) => String(item.product_details.id) === String(productId));
      if (existing) existing.quantity += quantity;
      else items.push({ id: `guest-${productId}`, product_details: snapshot, quantity, line_total: (Number(snapshot.price || 0) * quantity).toFixed(2) });
      for (const item of items) item.line_total = (Number(item.product_details.price || 0) * item.quantity).toFixed(2);
      localStorage.setItem(GUEST_CART_KEY, JSON.stringify(items));
      setCart(guestTotals(items));
      setIsOpen(true);
      return { success: true };
    }
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
    if (String(itemId).startsWith('guest-')) {
      const items = readGuestCart().map((item) => String(item.id) === String(itemId) ? { ...item, quantity, line_total: (Number(item.product_details.price || 0) * quantity).toFixed(2) } : item);
      localStorage.setItem(GUEST_CART_KEY, JSON.stringify(items)); setCart(guestTotals(items)); return;
    }
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
    if (String(itemId).startsWith('guest-')) { const items=readGuestCart().filter((item)=>String(item.id)!==String(itemId)); localStorage.setItem(GUEST_CART_KEY,JSON.stringify(items)); setCart(guestTotals(items)); return; }
    try {
      const { data } = await client.delete(`/cart/items/${itemId}/remove/`);
      setCart(data.data);
    } catch (requestError) {
      setError(getApiError(requestError, 'Could not remove this item.'));
    }
  }, []);

  const clearCart = useCallback(async () => {
    setError('');
    if (!user) { localStorage.removeItem(GUEST_CART_KEY); setCart(guestTotals([])); return; }
    try {
      await client.post('/cart/clear/');
      setCart((current) => current ? { ...current, items: [], total_items: 0, subtotal: '0.00' } : current);
    } catch (requestError) {
      setError(getApiError(requestError, 'Could not clear the cart.'));
      throw requestError;
    }
  }, [user]);

  const value = useMemo(() => ({
    cart, loading, error, isOpen, setIsOpen, addToCart, updateQuantity,
    removeItem, clearCart, refreshCart: fetchCart,
  }), [cart, loading, error, isOpen, addToCart, updateQuantity, removeItem, clearCart, fetchCart]);

  return <CartContext.Provider value={value}>{children}</CartContext.Provider>;
}

export const useCart = () => useContext(CartContext);
