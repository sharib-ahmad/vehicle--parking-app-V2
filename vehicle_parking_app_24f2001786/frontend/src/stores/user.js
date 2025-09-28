import { ref, computed, reactive } from 'vue'
import { defineStore } from 'pinia'
import api from '@/services/api'
import { useAuthStore } from '@/stores/auth'


export const useUserStore = defineStore('user', () => {
  const userData = reactive({
  full_name: '',
  username: '',
  email: '',
  password: '',
  phone_number: '',
  address: '',
  pincode: ''
  })
  
  const auth = useAuthStore()
  async function fetchUserData() {
    try {
      const response = await api.get('/users/me')
      Object.assign(userData, response.data)
    } catch (error) {
      console.error('Error fetching user data:', error)
    }
  }

  async function resetUserData() {
    Object.keys(userData).forEach(key => {
      userData[key] = ''
    })  
  }

  return { userData, fetchUserData, resetUserData   }
})
