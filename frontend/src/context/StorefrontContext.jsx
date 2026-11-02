import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import client, { getApiError } from '../api/client';

const StorefrontContext = createContext(null);
const DEFAULT_SETTINGS = {
  site_name: 'Wax and Warmth',
  site_description: 'Hand-poured candles made with love and warmth. Crafted to fill your space with gentle aromas and cozy vibes.',
  contact_email: 'realwaxandwarmth@gmail.com',
  contact_phone: '+91 6200835077',
};

export function StorefrontProvider({ children }) {
  const [settings, setSettings] = useState(DEFAULT_SETTINGS);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const refreshSettings = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const { data } = await client.get('/settings/');
      setSettings(data.data);
      return data.data;
    } catch (requestError) {
      setError(getApiError(requestError, 'Store settings are temporarily unavailable.'));
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { refreshSettings(); }, [refreshSettings]);

  const saveSettings = useCallback(async (payload) => {
    const { data } = await client.patch('/settings/', payload);
    setSettings(data.data);
    return data.data;
  }, []);

  const value = useMemo(() => ({
    settings, loading, error, refreshSettings, saveSettings,
  }), [settings, loading, error, refreshSettings, saveSettings]);

  return <StorefrontContext.Provider value={value}>{children}</StorefrontContext.Provider>;
}

export const useStorefront = () => useContext(StorefrontContext);
