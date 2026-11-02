import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import client, { restoreSession } from '../api/client';
import { tokenStore } from '../auth/tokenStore';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchProfile = useCallback(async () => {
    const { data } = await client.get('/auth/profile/');
    const profile = data.data;
    setUser(profile);
    return profile;
  }, []);

  useEffect(() => {
    let active = true;
    const expire = () => {
      tokenStore.clear();
      setUser(null);
      setLoading(false);
    };
    window.addEventListener('auth:expired', expire);
    restoreSession()
      .then(() => active && fetchProfile())
      .catch(() => { if (active) { tokenStore.clear(); setUser(null); } })
      .finally(() => { if (active) setLoading(false); });
    return () => {
      active = false;
      window.removeEventListener('auth:expired', expire);
    };
  }, [fetchProfile]);

  const login = useCallback(async (email, password) => {
    const { data } = await client.post('/auth/login/', { email: email.trim().toLowerCase(), password });
    tokenStore.set(data.data);
    try {
      return await fetchProfile();
    } catch (error) {
      await client.post('/auth/logout/', {}).catch(() => {});
      tokenStore.clear();
      setUser(null);
      throw error;
    }
  }, [fetchProfile]);

  const register = useCallback(async (userData) => {
    const { data } = await client.post('/auth/register/', userData);
    tokenStore.set({ access: data.data.access });
    setUser(data.data.user);
    return data.data.user;
  }, []);

  const logout = useCallback(async () => {
    try {
      if (tokenStore.getAccess()) await client.post('/auth/logout/', {}).catch(() => {});
    } finally {
      tokenStore.clear();
      setUser(null);
    }
  }, []);

  const value = useMemo(() => ({
    user,
    loading,
    login,
    register,
    logout,
    refreshProfile: fetchProfile,
    isAdmin: user?.is_admin === true || user?.role === 'ADMIN',
  }), [user, loading, login, register, logout, fetchProfile]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export const useAuth = () => useContext(AuthContext);
