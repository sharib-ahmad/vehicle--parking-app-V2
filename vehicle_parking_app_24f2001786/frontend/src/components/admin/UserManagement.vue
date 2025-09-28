<template>
  <div class="container py-5 mt-3">
    <!-- Header -->
    <header class="d-flex justify-content-between align-items-center pb-3 mb-4 border-bottom">
      <div>
        <h1 class="h2 mb-0">User Management</h1>
        <p class="text-muted mb-0">View and manage all registered users.</p>
      </div>
    </header>

    <!-- Loading State -->
    <div v-if="isLoading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="mt-2">Loading users...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="alert alert-danger">
      Failed to load users. Please try again later.
    </div>

    <!-- Empty State -->
    <div v-else-if="users.length === 0" class="text-center py-5 bg-light rounded">
      <h4 class="text-muted">No Users Found</h4>
      <p>There are currently no registered users in the system.</p>
    </div>

    <!-- Users Table -->
    <div v-else class="card shadow-sm">
      <div class="card-body">
        <div class="table-responsive">
          <table class="table table-hover align-middle">
            <thead class="table-light">
              <tr>
                <th scope="col">Full Name</th>
                <th scope="col">Username</th>
                <th scope="col">Email</th>
                <th scope="col">Phone Number</th>
                <th scope="col">Pin Code</th>
                <th scope="col">Joined On</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="user in users" :key="user.id">
                <td>{{ user.full_name }}</td>
                <td>{{ user.username }}</td>
                <td>{{ user.email }}</td>
                <td>{{ user.phone_number || 'N/A' }}</td>
                <td>{{ user.pincode || 'N/A' }}</td>
                <td>{{ formatJoinDate(user.created_at) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '@/services/api';
import { useNotificationStore } from '@/stores/notification';

const notification = useNotificationStore();
const users = ref([]);
const isLoading = ref(true);
const error = ref(null);

const fetchUsers = async () => {
  isLoading.value = true;
  error.value = null;
  try {
    // Note: The final endpoint will depend on how you register the namespace.
    // Assuming '/users' is correct based on the user.py file.
    const response = await api.get('/users/');
    users.value = response.data;
  } catch (err) {
    error.value = err;
    notification.showNotification({ type: 'error', text: '❌ Failed to fetch user data.' });
  } finally {
    isLoading.value = false;
  }
};

const formatJoinDate = (dateString) => {
  if (!dateString) return 'N/A';
  const options = { year: 'numeric', month: 'long', day: 'numeric' };
  return new Date(dateString).toLocaleDateString(undefined, options);
};

onMounted(fetchUsers);
</script>

<style scoped>
.table-hover tbody tr:hover {
  background-color: #f8f9fa;
}
</style>
