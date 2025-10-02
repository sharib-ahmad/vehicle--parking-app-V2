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
    
    // Only add the Authorization header if the request is NOT for refreshing the token.
    if (auth.token && !config.url.endsWith('/auth/refresh')) {
      config.headers.Authorization = `Bearer ${auth.token}`;
    }

    // Always add the CSRF token for requests that use the refresh cookie.
    // This is crucial for /auth/refresh and /auth/logout.
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
