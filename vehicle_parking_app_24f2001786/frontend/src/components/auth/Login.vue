<template>
  <div class="container d-flex justify-content-center align-items-center min-vh-100">
    <div class="card shadow-lg p-4 col-md-6 col-lg-4">
      <h2 class="text-center mb-4">Login</h2>

      <!-- Form -->
      <form @submit.prevent="handleLogin" novalidate>
        
        <FormInput
          id="email"
          label="Email"
          type="email"
          v-model.trim="form.email"
          :error="errors.email"
          placeholder="Enter your email"
          required
        />

        <div class="mb-3">
          <label for="password" class="form-label">Password</label>
          <div class="input-group">
            <input 
              v-model.trim="form.password" 
              :type="isPasswordVisible ? 'text' : 'password'"
              class="form-control" 
              :class="{ 'is-invalid': errors.password }"
              id="password"
              placeholder="Enter your password"
              required />
            <button @click="togglePasswordVisibility" class="btn btn-outline-secondary" type="button">
              {{ isPasswordVisible ? 'Hide' : 'Show' }}
            </button>
            <div v-if="errors.password" class="invalid-feedback">{{ errors.password }}</div>
          </div>
        </div>

        <button type="submit" class="btn btn-primary w-100" :disabled="isLoading">
          <span v-if="isLoading" class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
          {{ isLoading ? 'Logging in...' : 'Login' }}
        </button>
      </form>

      <div class="text-center mt-3">
        <small>Don’t have an account? 
          <router-link to="/register">Register</router-link>
        </small>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import api from '@/services/api' // your axios instance
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useNotificationStore } from '@/stores/notification'
import FormInput from '../common/FormInput.vue'

const router = useRouter()
const auth = useAuthStore()
const notification = useNotificationStore()

const form = reactive({
  email: '',
  password: ''
})

const errors = reactive({})
const isPasswordVisible = ref(false)
const isLoading = ref(false)

const togglePasswordVisibility = () => {
  isPasswordVisible.value = !isPasswordVisible.value
}

// Validation Logic
const validateForm = () => {
  Object.keys(errors).forEach(key => delete errors[key]);

  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!form.email) {
    errors.email = "Email is required.";
  } else if (!emailRegex.test(form.email)) {
    errors.email = "Please enter a valid email address.";
  }

  if (!form.password) {
    errors.password = "Password is required.";
  }

  return Object.keys(errors).length === 0;
};


const handleLogin = async () => {
  if (!validateForm()) {
    return;
  }

  isLoading.value = true;
  try {
    const response = await api.post('/auth/login', form)
    auth.login(response.data.access_token, response.data.user)
    notification.showNotification({
      type: 'success',
      text: "✅ Login successful! Redirecting..."
    });
    
    setTimeout(() => {
      if (auth.isAdmin) {
        router.push({ name: 'AdminDashboard' });
      } else {
        router.push({ name: 'UserDashboard' });
      }
    }, 2000)
  } catch (error) {
    notification.showNotification({
        type: 'error',
        text: "❌ Login failed: " + (error.response?.data?.message || "Incorrect email or password")
    });
  } finally {
    isLoading.value = false;
  }
}
</script>

