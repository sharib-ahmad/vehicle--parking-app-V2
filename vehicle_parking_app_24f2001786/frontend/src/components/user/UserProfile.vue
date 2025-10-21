<template>
  <div class="container py-5 mt-4">
    <header class="pb-3 mb-4 border-bottom">
      <h1 class="h2">My Profile</h1>
      <p class="text-muted">View and manage your personal information.</p>
    </header>

    <div v-if="isLoading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <div v-else-if="error" class="alert alert-danger">
      Failed to load your profile. Please try refreshing the page.
    </div>

    <div v-else-if="user" class="card shadow-sm">
      <div class="card-body p-4">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h5 class="card-title mb-0">Your Details</h5>
            <button v-if="!isEditing" @click="toggleEdit(true)" class="btn btn-outline-primary btn-sm">
                Edit Profile
            </button>
        </div>

        <form @submit.prevent="saveProfile">
          <div class="row g-3">
            <div class="col-md-6">
              <label for="fullName" class="form-label">Full Name</label>
              <input type="text" id="fullName" class="form-control" v-model="editableUser.full_name" :disabled="!isEditing">
            </div>
            <div class="col-md-6">
              <label for="username" class="form-label">Username</label>
              <input type="text" id="username" class="form-control" v-model="editableUser.username" disabled>
              <div class="form-text">Username cannot be changed.</div>
            </div>
            <div class="col-md-6">
              <label for="email" class="form-label">Email Address</label>
              <input type="email" id="email" class="form-control" v-model="editableUser.email" disabled>
               <div class="form-text">Email cannot be changed.</div>
            </div>
            <div class="col-md-6">
              <label for="phone" class="form-label">Phone Number</label>
              <input type="tel" id="phone" class="form-control" v-model="editableUser.phone_number" :disabled="!isEditing">
            </div>
            <div class="col-12">
              <label for="address" class="form-label">Address</label>
              <input type="text" id="address" class="form-control" v-model="editableUser.address" :disabled="!isEditing">
            </div>
             <div class="col-md-6">
              <label for="pincode" class="form-label">Pincode</label>
              <input type="text" id="pincode" class="form-control" v-model="editableUser.pincode" :disabled="!isEditing">
            </div>
          </div>

          <div v-if="isEditing" class="mt-4 text-end">
            <button type="button" @click="toggleEdit(false)" class="btn btn-secondary me-2">Cancel</button>
            <button type="submit" class="btn btn-primary" :disabled="isSaving">
                <span v-if="isSaving" class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
                Save Changes
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '@/services/api'; // Assuming you have an api service
import { useNotificationStore } from '@/stores/notification'; // Assuming a Pinia store for notifications

const notification = useNotificationStore();

const user = ref(null);
const editableUser = ref({});
const isLoading = ref(true);
const isEditing = ref(false);
const isSaving = ref(false);
const error = ref(null);

const fetchUserProfile = async () => {
  isLoading.value = true;
  error.value = null;
  try {
    const response = await api.get('/users/me');
    user.value = response.data;
    // Create a deep copy for editing to avoid mutating the original state until save
    editableUser.value = JSON.parse(JSON.stringify(response.data));
  } catch (err) {
    error.value = err;
    notification.showNotification({ type: 'error', text: '❌ Could not fetch profile.' });
  } finally {
    isLoading.value = false;
  }
};

const toggleEdit = (editing) => {
  isEditing.value = editing;
  // If canceling, revert changes
  if (!editing) {
    editableUser.value = JSON.parse(JSON.stringify(user.value));
  }
};

const saveProfile = async () => {
  isSaving.value = true;
  try {
    // Only send fields that can be updated
    const updatePayload = {
        full_name: editableUser.value.full_name,
        phone_number: editableUser.value.phone_number,
        address: editableUser.value.address,
        pincode: editableUser.value.pincode,
    };
    const response = await api.put('/users/me', updatePayload);
    user.value = response.data; // Update the main user object
    notification.showNotification({ type: 'success', text: '✅ Profile updated successfully!' });
    toggleEdit(false);
  } catch (err) {
    notification.showNotification({ type: 'error', text: '❌ Failed to update profile.' });
  } finally {
    isSaving.value = false;
  }
};

onMounted(fetchUserProfile);
</script>

<style scoped>
.card {
  border: none;
  border-radius: .75rem;
}
.form-label {
    font-weight: 500;
}
.form-text {
    font-size: 0.875em;
}
</style>
