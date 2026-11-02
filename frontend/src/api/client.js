import axios from 'axios';
import { tokenStore } from '../auth/tokenStore';

export const API_URL = (import.meta.env.VITE_API_URL || 'http://localhost:8000/api').replace(/\/+$/, '');

const client = axios.create({
  baseURL: API_URL,
  headers: { Accept: 'application/json' },
  withCredentials: true,
});

client.interceptors.request.use((config) => {
  const token = tokenStore.getAccess();
  if (token) config.headers.Authorization = `Bearer ${token}`;
  if (typeof FormData !== 'undefined' && config.data instanceof FormData) {
    delete config.headers['Content-Type'];
  } else if (config.data !== undefined) {
    config.headers['Content-Type'] = 'application/json';
  }
  return config;
});

let refreshPromise;

client.interceptors.response.use((response) => response, async (error) => {
  const request = error.config;
  const url = request?.url || '';
  const isAuthRequest = /\/auth\/(login|register|token\/refresh)\//.test(url);
  if (error.response?.status !== 401 || !request || request._retry || isAuthRequest) {
    return Promise.reject(error);
  }

  request._retry = true;
  try {
    if (!refreshPromise) {
      refreshPromise = axios.post(`${API_URL}/auth/token/refresh/`, {}, { withCredentials: true })
        .then(({ data }) => {
          const access = data?.data?.access;
          if (!access) throw new Error('The refresh endpoint did not return an access token.');
          tokenStore.set({ access });
          return access;
        })
        .finally(() => { refreshPromise = undefined; });
    }
    const access = await refreshPromise;
    request.headers.Authorization = `Bearer ${access}`;
    return client(request);
  } catch (refreshError) {
    tokenStore.clear();
    window.dispatchEvent(new CustomEvent('auth:expired'));
    return Promise.reject(refreshError);
  }
});

export async function restoreSession() {
  const { data } = await axios.post(`${API_URL}/auth/token/refresh/`, {}, { withCredentials: true });
  const access = data?.data?.access;
  if (!access) throw new Error('The refresh endpoint did not return an access token.');
  tokenStore.set({ access });
  return access;
}

export function getApiError(error, fallback = 'Something went wrong. Please try again.') {
  const payload = error?.response?.data;
  if (payload?.error?.message) return payload.error.message;
  if (payload?.detail) return payload.detail;
  if (payload?.message) return payload.message;
  const details = payload?.details;
  if (details && typeof details === 'object') {
    const messages = Object.entries(details).flatMap(([field, value]) => {
      const values = Array.isArray(value) ? value : [value];
      return values.map((item) => `${field}: ${String(item)}`);
    });
    if (messages.length) return messages.join(' ');
  }
  return fallback;
}

export default client;
