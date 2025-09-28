<template>
  <div class="container d-flex justify-content-center align-items-center min-vh-100 mt-5 pt-3">
    <div class="card shadow-lg p-4 col-md-6 col-lg-5">
      <h3 class="text-center mb-4">Create Account</h3>
      
      <form @submit.prevent="handleRegister" novalidate>
        <FormInput id="fullName" label="Full Name" v-model.trim="form.full_name" :error="errors.full_name" placeholder="Enter your full name" />
        <FormInput id="username" label="Username" v-model.trim="form.username" :error="errors.username" placeholder="Choose a username" />
        <FormInput id="email" label="Email" type="email" v-model.trim="form.email" :error="errors.email" placeholder="Enter your email" />

        <div class="mb-3">
          <label for="password" class="form-label">Password</label>
          <div class="input-group">
            <input 
              :type="isPasswordVisible ? 'text' : 'password'"
              v-model.trim="form.password" 
              class="form-control" 
              :class="{ 'is-invalid': errors.password }"
              id="password" 
              placeholder="Enter password" 
              required>
            <button @click="togglePasswordVisibility" class="btn btn-outline-secondary" type="button" id="togglePassword">
              {{ isPasswordVisible ? 'Hide' : 'Show' }}
            </button>
            <div v-if="errors.password" class="invalid-feedback">{{ errors.password }}</div>
          </div>
        </div>
        
        <FormInput id="phone" label="Phone Number" type="tel" v-model.trim="form.phone_number" :error="errors.phone_number" placeholder="123-456-7890" />
        <FormInput id="address" label="Address" v-model.trim="form.address" :error="errors.address" placeholder="Enter your address" />
        <FormInput id="pincode" label="Pincode" v-model.trim="form.pincode" :error="errors.pincode" placeholder="Postal code" />

        <button type="submit" class="btn btn-primary w-100" :disabled="isLoading">
          <span v-if="isLoading" class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
          {{ isLoading ? 'Registering...' : 'Register' }}
        </button>

        <p class="text-center mt-3">
          Already have an account? 
          <router-link to="/login">Login here</router-link>
        </p>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import api from '@/services/api'
import { useRouter } from 'vue-router'
import { useNotificationStore } from '@/stores/notification'
import FormInput from '../common/FormInput.vue'

const router = useRouter()
const notification = useNotificationStore()

const form = reactive({
  full_name: '',
  username: '',
  email: '',
  password: '',
  phone_number: '',
  address: '',
  pincode: ''
})

const errors = reactive({})
const isPasswordVisible = ref(false)
const isLoading = ref(false)

const togglePasswordVisibility = () => {
  isPasswordVisible.value = !isPasswordVisible.value
}

const validateForm = () => {
  Object.keys(errors).forEach(key => delete errors[key]);

  if (!form.full_name) errors.full_name = "Full name is required.";
  else if (form.full_name.length < 3) errors.full_name = "Full name must be at least 3 characters.";
  
  if (!form.username) errors.username = "Username is required.";
  else if (form.username.length < 7) errors.username = "Username must be at least 7 characters.";
  
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!form.email) errors.email = "Email is required.";
  else if (!emailRegex.test(form.email)) errors.email = "Please enter a valid email address.";

  if (!form.password) errors.password = "Password is required.";
  else if (form.password.length < 8) errors.password = "Password must be at least 8 characters.";
  
  const phoneRegex = /^(\+\d{1,2}\s?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}$/;
  if (!form.phone_number) errors.phone_number = "Phone number is required.";
  else if (!phoneRegex.test(form.phone_number)) errors.phone_number = "Please enter a valid phone number.";
  
  if (!form.address) errors.address = "Address is required.";

  const pincodeRegex = /^\d{5,6}$/;
  if (!form.pincode) errors.pincode = "Pincode is required.";
  else if (!pincodeRegex.test(form.pincode)) errors.pincode = "Please enter a valid pincode.";

  return Object.keys(errors).length === 0;
};

const handleRegister = async () => {
  if (!validateForm()) {
    return;
  }

  isLoading.value = true;
  try {
    await api.post('/auth/register', form)
    notification.showNotification({ 
      type: 'success', 
      text: "✅ Registration successful! Redirecting to login..." 
    });
    
    setTimeout(() => {
      router.push({name:'Login'})
    }, 2000)

  } catch (error) {
    notification.showNotification({
        type: 'error', 
        text: "❌ Registration failed: " + (error.response?.data?.message || "Something went wrong")
    });
  } finally {
    isLoading.value = false;
  }
}
</script>

