<template>
  <transition name="slide-fade">
    <div v-if="notification.visible" 
         class="flash-message" 
         :class="`flash-${notification.type}`">
      <span>{{ notification.message }}</span>
      <button @click="notification.hideNotification()" class="close-btn">&times;</button>
    </div>
  </transition>
</template>

<script setup>
import { useNotificationStore } from '@/stores/notification';
const notification = useNotificationStore();
</script>

<style scoped>
.flash-message {
  position: fixed;
  top: 80px; /* Below the navbar */
  left: 50%;
  transform: translateX(-50%);
  z-index: 2000;
  padding: 1rem 1.5rem;
  border-radius: 8px;
  color: white;
  display: flex;
  align-items: center;
  justify-content: space-between;
  min-width: 300px;
  max-width: 90%;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  font-weight: 500;
}

/* Success - Green */
.flash-success {
  background-color: #28a745; 
}

/* Error/Danger - Red */
.flash-error {
  background-color: #dc3545;
}

/* Info - Blue */
.flash-info {
  background-color: #0dcaf0;
}

/* Warning - Yellow */
.flash-warning {
  background-color: #ffc107;
  color: #212529; /* Dark text for better contrast on yellow */
}
.flash-warning .close-btn {
    color: #212529;
}


.close-btn {
  background: none;
  border: none;
  color: white;
  font-size: 1.5rem;
  line-height: 1;
  margin-left: 1rem;
  opacity: 0.8;
  cursor: pointer;
}
.close-btn:hover {
    opacity: 1;
}

/* Animation */
.slide-fade-enter-active,
.slide-fade-leave-active {
  transition: all 0.4s ease;
}
.slide-fade-enter-from,
.slide-fade-leave-to {
  transform: translate(-50%, -20px);
  opacity: 0;
}
</style>
