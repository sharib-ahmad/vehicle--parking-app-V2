<template>
  <div class="container py-5 mt-3">
    <!-- Header -->
    <header class="d-flex justify-content-between align-items-center pb-3 mb-4 border-bottom">
      <div>
        <h1 class="h2 mb-0">Parking Lot Management</h1>
        <p class="text-muted mb-0">Oversee all parking facilities.</p>
      </div>
      <button class="btn btn-primary" @click="openAddModal">
        <i class="bi bi-plus-lg me-1"></i> Add New Lot
      </button>
    </header>

    <!-- Loading State -->
    <div v-if="isLoading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="mt-2">Loading parking lots...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="alert alert-danger">
      Failed to load parking lots. Please try again later.
    </div>

    <!-- Empty State -->
    <div v-else-if="parkingLots.length === 0" class="text-center py-5 bg-light rounded">
      <h4 class="text-muted">No Parking Lots Found</h4>
      <p>Click the "Add New Lot" button to get started.</p>
    </div>

    <!-- Parking Lots List -->
    <ParkingLotList v-else :lots="parkingLots" @lot-updated="fetchParkingLots" />
  </div>

  <!-- Form Modal for Add -->
  <ParkingLotFormModal :show="showFormModal" :lot="null" @close="closeFormModal" @saved="onLotSaved" />
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '@/services/api';
import { useNotificationStore } from '@/stores/notification';
import ParkingLotFormModal from './ParkingLotFormModal.vue';
import ParkingLotList from './ParkingLotList.vue';

const notification = useNotificationStore();
const parkingLots = ref([]);
const isLoading = ref(true);
const error = ref(null);
const showFormModal = ref(false);

// Fetch all parking lots
const fetchParkingLots = async () => {
  isLoading.value = true;
  error.value = null;
  try {
    const response = await api.get('/admin/parking-lots');
    parkingLots.value = response.data;
  } catch (err) {
    error.value = err;
    console.log(err)
    notification.showNotification({ type: 'error', text: '❌ Failed to fetch parking lots.' });
  } finally {
    isLoading.value = false;
  }
};

onMounted(fetchParkingLots);

// Modal handling
const openAddModal = () => {
  showFormModal.value = true;
};

const closeFormModal = () => {
  showFormModal.value = false;
};

const onLotSaved = () => {
  closeFormModal();
  fetchParkingLots();
};
</script>
