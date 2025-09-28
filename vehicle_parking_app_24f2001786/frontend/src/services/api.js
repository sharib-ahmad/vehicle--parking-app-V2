import axios from 'axios';
import { useAuthStore } from '../stores/auth';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
}

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
});

// This interceptor runs before every request is sent.
api.interceptors.request.use(
  (config) => {
    const auth = useAuthStore();
    
    // Add the short-lived access token header if it exists.
    if (auth.token) {
      config.headers.Authorization = `Bearer ${auth.token}`;
    }

    // FIX: Read the CSRF token from the cookie and add it to the required header.
    // This is necessary for all requests that use the refresh token (e.g., /auth/refresh).
    // The default cookie name for the refresh token's CSRF is 'csrf_refresh_token'.
    const csrfToken = getCookie('csrf_refresh_token');
    if (csrfToken) {
      config.headers['X-CSRF-TOKEN'] = csrfToken;
    }
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

export default api;
