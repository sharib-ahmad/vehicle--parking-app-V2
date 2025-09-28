import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { useNotificationStore } from './notification';
import { jwtDecode } from 'jwt-decode';
import api from '@/services/api';

export const useAuthStore = defineStore('auth', () => {
  const token = ref(null);
  const user = ref(JSON.parse(localStorage.getItem('user')) || null);
  let logoutTimer = null;
  const authReady = ref(false);

  const isAuthenticated = computed(() => !!token.value);
  const isAdmin = computed(() => user.value?.role === 'admin');

  function clearAuthData() {
    token.value = null;
    user.value = null;
    localStorage.removeItem('user');
    if (logoutTimer) clearTimeout(logoutTimer);
  }

  function login(accessToken, userData) {
    token.value = accessToken;
    user.value = userData;
    localStorage.setItem('user', JSON.stringify(userData));
    scheduleAutoLogout(accessToken);
  }

  async function checkSession() {
    if (user.value && !token.value) {
      try {
        await refreshToken();
      } catch {
        // Errors are handled inside refreshToken
      }
    }
    authReady.value = true;
  }

  async function refreshToken() {
    try {
      const response = await api.post('/auth/refresh');
      const newAccess = response.data.access_token;
      token.value = newAccess;
      scheduleAutoLogout(newAccess);
      return Promise.resolve();
    } catch (error) {
      clearAuthData();
      return Promise.reject(error);
    }
  }

  function scheduleAutoLogout(jwtToken) {
    if (logoutTimer) clearTimeout(logoutTimer);

    try {
      const decoded = jwtDecode(jwtToken);
      const exp = decoded.exp * 1000;
      const now = Date.now();
      const expiresIn = exp - now;
      const refreshBuffer = 20 * 1000;
      const timeout = expiresIn - refreshBuffer;

      if (timeout > 0) {
        logoutTimer = setTimeout(() => {
          refreshToken();
        }, timeout);
      } else {
        refreshToken();
      }
    } catch {
      clearAuthData();
    }
  }

  async function logout() {
    const notification = useNotificationStore();
    
    clearAuthData();
    try {
      await api.post('/auth/logout');
    } catch {
    }
    notification.showNotification({
      type: 'info',
      text: 'ℹ️ You have been logged out.',
    });
  }

  return { token, user, login, logout, refreshToken, isAuthenticated, isAdmin, checkSession, authReady };
});

