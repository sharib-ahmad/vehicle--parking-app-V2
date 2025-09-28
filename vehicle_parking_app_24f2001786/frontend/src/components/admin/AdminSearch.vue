<template>
  <div class="container py-5 mt-4">
    <!-- Header -->
    <header class="pb-3 mb-4 border-bottom">
      <h1 class="h2 mb-0">Admin Search</h1>
      <p class="text-muted mb-0">Find parking lots, users, and vehicles.</p>
    </header>

    <!-- Search Form -->
    <div class="card shadow-sm mb-4">
      <div class="card-body">
        <form @submit.prevent="handleSearch" class="row g-3 align-items-end">
          <div class="col-md-3">
            <label for="searchType" class="form-label fw-bold">Search For:</label>
            <select id="searchType" v-model="searchType" class="form-select">
              <option value="lot">Parking Lot</option>
              <option value="user">User</option>
              <option value="vehicle">Vehicle</option>
            </select>
          </div>

          <div class="col-md-3">
            <label for="searchParam" class="form-label fw-bold">By:</label>
            <select id="searchParam" v-model="searchParam" class="form-select">
              <option v-for="option in searchOptions" :key="option.value" :value="option.value">
                {{ option.text }}
              </option>
            </select>
          </div>

          <div class="col-md-4">
            <label for="searchQuery" class="form-label fw-bold">Query:</label>
            <input type="text" id="searchQuery" v-model="searchQuery" class="form-control" :placeholder="placeholderText" required>
          </div>

          <div class="col-md-2">
            <button type="submit" class="btn btn-primary w-100">
              <i class="bi bi-search me-1"></i> Search
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Results Section -->
    <div>
      <!-- Loading State -->
      <div v-if="isLoading" class="text-center py-5">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
        <p class="mt-2">Searching...</p>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="alert alert-danger">
        {{ error }}
      </div>
      
      <!-- Initial State -->
      <div v-else-if="!searchPerformed" class="text-center py-5 bg-light rounded">
          <h4 class="text-muted">Please enter a search query to begin.</h4>
      </div>

      <!-- No Results State -->
      <div v-else-if="searchResults.length === 0" class="text-center py-5 bg-light rounded">
          <h4 class="text-muted">No results found.</h4>
          <p>Try adjusting your search criteria.</p>
      </div>

      <!-- Results Display -->
      <div v-else>
        <h3 class="mb-3">Search Results</h3>
        <!-- Parking Lot Results -->
        <ParkingLotList v-if="searchType === 'lot'" :lots="searchResults" @lot-updated="handleSearch" />

        <!-- User Results -->
        <div v-if="searchType === 'user'" class="row g-3">
            <div v-for="user in searchResults" :key="user.username" class="col-md-6">
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">{{ user.username }}</h5>
                        <p class="card-text mb-1"><strong>Email:</strong> {{ user.email }}</p>
                        <p class="card-text mb-1"><strong>Phone:</strong> {{ user.phone_number }}</p>
                        <p class="card-text"><strong>Address:</strong> {{ user.address }}, {{ user.pincode }}</p>
                    </div>
                </div>
            </div>
        </div>

        <!-- Vehicle Results -->
        <div v-if="searchType === 'vehicle'">
            <div class="card">
                 <div class="card-body">
                    <h5 class="card-title">Vehicle Information</h5>
                    <p class="card-text"><strong>Vehicle Number:</strong> {{ searchResults[0].vehicle_number }}</p>
                    <p class="card-text"><strong>Owner:</strong> {{ searchResults[0].user.username }}</p>
                    <p class="card-text"><strong>Model:</strong> {{ searchResults[0].model }}</p>
                    <p class="card-text"><strong>Type:</strong> {{ searchResults[0].brand }}</p>
                    <p class="card-text"><strong>Color:</strong> {{ searchResults[0].color }}</p>
                </div>
            </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue';
import api from '@/services/api';
import { useNotificationStore } from '@/stores/notification';
import ParkingLotList from './ParkingLotList.vue';

const notification = useNotificationStore();

const searchType = ref('lot');
const searchParam = ref('location');
const searchQuery = ref('');

const searchResults = ref([]);
const isLoading = ref(false);
const error = ref(null);
const searchPerformed = ref(false);


const searchOptionsMapping = {
  lot: [
    { value: 'location', text: 'Location Name' },
    { value: 'pincode', text: 'Pincode' },
  ],
  user: [
    { value: 'username', text: 'Username' },
    { value: 'phone', text: 'Phone Number' },
    { value: 'pincode', text: 'Pincode' },
  ],
  vehicle: [
    { value: 'vehicle_number', text: 'Vehicle Number' },
  ],
};

const searchOptions = computed(() => searchOptionsMapping[searchType.value]);
const placeholderText = computed(() => `Enter ${searchOptions.value.find(opt => opt.value === searchParam.value)?.text || ''}`);

// Reset searchParam when searchType changes
watch(searchType, (newType) => {
  searchParam.value = searchOptionsMapping[newType][0].value;
  searchResults.value = [];
  searchPerformed.value = false;
});

const handleSearch = async () => {
  if (!searchQuery.value.trim()) {
    notification.showNotification({ type: 'error', text: 'Search query cannot be empty.' });
    return;
  }

  isLoading.value = true;
  error.value = null;
  searchPerformed.value = true;
  searchResults.value = [];

  try {
    const params = { [searchParam.value]: searchQuery.value };
    const response = await api.get(`/admin/search/${searchType.value}`, { params });
    searchResults.value = response.data;
  } catch (err) {
    const errorMessage = err.response?.data?.message || 'An error occurred during search.';
    error.value = `Failed to fetch results: ${errorMessage}`;
    notification.showNotification({ type: 'error', text: '❌ ' + errorMessage });
  } finally {
    isLoading.value = false;
  }
};
</script>

<style scoped>
.form-label {
    font-size: 0.9rem;
    color: #495057;
}
.card {
    border: 1px solid #dee2e6;
    border-radius: .375rem;
}
</style>
