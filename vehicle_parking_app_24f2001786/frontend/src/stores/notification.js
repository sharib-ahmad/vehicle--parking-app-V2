import { defineStore } from 'pinia';
import { ref } from 'vue';

export const useNotificationStore = defineStore('notification', () => {
  const message = ref('');
  const type = ref('info'); // 'success', 'error', 'info', or 'warning'
  const visible = ref(false);
  let timeoutId = null;

  function showNotification(payload) {
    if (timeoutId) {
      clearTimeout(timeoutId);
    }

    message.value = payload.text;
    type.value = payload.type || 'info'; // Default to 'info' if no type is provided
    visible.value = true;

    timeoutId = setTimeout(() => {
      hideNotification();
    }, 5000);
  }

  function hideNotification() {
    visible.value = false;
    setTimeout(() => {
        message.value = '';
        type.value = 'info';
    }, 500); // Wait for fade-out transition
  }

  return { message, type, visible, showNotification, hideNotification };
});

