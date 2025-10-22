<template>
  <div class="accordion" id="parkingLotsAccordion">
    <div v-for="lot in lots" :key="lot.id" class="accordion-item mb-3">
      <h2 class="accordion-header" :id="'heading' + lot.id">
        <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse"
          :data-bs-target="'#collapse' + lot.id" aria-expanded="false" :aria-controls="'collapse' + lot.id">
          <div class="d-flex justify-content-between w-100 align-items-center pe-3">
            <div>
              <h6 class="mb-0">{{ lot.prime_location_name }}</h6>
              <small class="text-muted fw-semibold">{{ lot.address }}</small>
              <br>
              <small class="text-muted mt-1"><span class="fw-semibold me-2">{{ lot.floor_level }} Floor</span><span class="fw-bold">{{ formatTime(lot.open_time) }} - {{ formatTime(lot.close_time) }}</span></small>
            </div>
            <div class="d-flex align-items-center">
              <span class="badge bg-success rounded-pill px-3 py-2 mx-2 shadow-sm fw-bold fs-5">
                {{ lot.price_per_hour }} ₹/hr
              </span> <span class="badge bg-success-subtle text-success-emphasis me-3">
                {{ getAvailableSpots(lot) }} Available
              </span>
              <span class="badge bg-primary rounded-pill">{{ lot.maximum_number_of_spots }} Total Spots</span>
            </div>
          </div>
        </button>
      </h2>
      <div :id="'collapse' + lot.id" class="accordion-collapse collapse" :aria-labelledby="'heading' + lot.id"
        data-bs-parent="#parkingLotsAccordion">
        <div class="accordion-body">
          <h5>Spots Overview</h5>
          <div v-if="lot.parking_spots && lot.parking_spots.length > 0" class="d-flex flex-wrap gap-2">
            <div v-for="spot in sortedSpots(lot.parking_spots)" :key="spot.id" class="spot-box" :class="{
              'available': spot.status === 'available',
              'occupied': spot.status === 'occupied'
            }" data-bs-toggle="tooltip" :title="`Status: ${spot.status}`" @click="handleSpotClick(spot)">
              {{ spot.spot_number }}
            </div>
          </div>
          <p v-else class="text-muted">No spots found for this lot.</p>

          <div class="mt-4 border-top pt-3">
            <button class="btn btn-outline-primary btn-sm me-2" @click.stop="openEditModal(lot)">
              <i class="bi bi-pencil-square me-1"></i> Edit Lot Details
            </button>
            <button class="btn btn-outline-danger btn-sm" @click.stop="openDeleteModal(lot)">
              <i class="bi bi-trash me-1"></i> Delete Lot
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Modals -->
  <ParkingLotFormModal :show="showFormModal" :lot="selectedLot" @close="closeFormModal" @saved="onLotSaved" />

  <div v-if="showStatusModal" class="modal fade show d-block" tabindex="-1" style="background-color: rgba(0,0,0,0.5);">
    <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">Occupied Spot Information</h5>
                <button type="button" class="btn-close" @click="showStatusModal = false"></button>
            </div>
            <div class="modal-body" v-if="reservationInfo">
                <p><strong>Spot Number:</strong> {{ reservationInfo.parking_spot.spot_number }}</p>
                <p><strong>Username:</strong> {{ reservationInfo.user.username }}</p>
                <p><strong>Parking Rate:</strong> ₹{{ reservationInfo.parking_cost_per_hour }}/hour</p>
                <hr>
                <p><strong>Parking Time:</strong> {{ formatTimestampToIST(reservationInfo.parking_timestamp) }}</p>
                <h5 class="mt-3"><strong>Est. Parking Cost:</strong> ₹{{ totalCost(reservationInfo).toFixed(2) }}</h5>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" @click="showStatusModal = false">Back</button>
            </div>
        </div>
    </div>
  </div>

  <div v-if="showAvailableSpotModal" class="modal fade show d-block" tabindex="-1" style="background-color: rgba(0,0,0,0.5);">
        <div class="modal-dialog modal-dialog-centered">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Available Spot Details</h5>
                    <button type="button" class="btn-close" @click="showAvailableSpotModal = false"></button>
                </div>
                <div class="modal-body" v-if="selectedSpot">
                    <p><strong>Spot Number:</strong> {{ selectedSpot.spot_number }}</p>
                    <p><strong>Status:</strong> <span class="badge bg-success">{{ selectedSpot.status }}</span></p>
                    <p class="text-danger mt-3">This action will permanently delete the spot.</p>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" @click="showAvailableSpotModal = false">Cancel</button>
                    <button type="button" class="btn btn-danger" @click="handleDeleteSpot">Delete Spot</button>
                </div>
            </div>
        </div>
    </div>

  <div v-if="showDeleteModal">
    <div class="modal fade show d-block" tabindex="-1">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Confirm Deletion</h5>
            <button type="button" class="btn-close" @click="showDeleteModal = false"></button>
          </div>
          <div class="modal-body">
            <p>Are you sure you want to delete the parking lot at <strong>{{ selectedLot?.prime_location_name
                }}</strong>?</p>
            <p class="text-danger">This action cannot be undone.</p>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="showDeleteModal = false">Cancel</button>
            <button type="button" class="btn btn-danger" @click="handleDeleteLot">Delete Lot</button>
          </div>
        </div>
      </div>
    </div>
    <div class="modal-backdrop fade show"></div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import api from '@/services/api';
import { useNotificationStore } from '@/stores/notification';
import ParkingLotFormModal from './ParkingLotFormModal.vue';
import { formatTimestampToIST, formatTime } from '@/utils/formatters';
import { totalCost } from '@/utils/totalCost';

defineProps({
  lots: {
    type: Array,
    required: true,
  },
});

const emit = defineEmits(['lot-updated']);

const notification = useNotificationStore();

const showFormModal = ref(false);
const showDeleteModal = ref(false);
const showStatusModal = ref(false);
const showAvailableSpotModal = ref(false);

const selectedLot = ref(null);
const selectedSpot = ref(null);
const reservationInfo = ref(null);

const getAvailableSpots = (lot) => {
  if (!lot.parking_spots) return 0;
  return lot.parking_spots.filter(spot => spot.status === "available").length;
};

const sortedSpots = (spots) => {
  if (!spots) return [];
  return [...spots].sort((a, b) => {
    const numA = parseInt(a.spot_number.split('-').pop(), 10);
    const numB = parseInt(b.spot_number.split('-').pop(), 10);
    return numA - numB;
  });
};

const handleSpotClick = (spot) => {
  if (spot.status === 'occupied') {
    openStatusModal(spot.id);
  } else if (spot.status === 'available') {
    selectedSpot.value = spot;
    showAvailableSpotModal.value = true;
  }
};

const openEditModal = (lot) => {
  selectedLot.value = { ...lot };
  showFormModal.value = true;
};

const openStatusModal = async (spot_id) => {
  showStatusModal.value = true;
  try {
    const response = await api.get(`admin/reservation/spot/${spot_id}`);
    reservationInfo.value = response.data;
  } catch (err) {
    console.log(err);
    notification.showNotification({ type: 'error', text: '❌ Failed to fetch spot info.' });
  }
};

const openDeleteModal = (lot) => {
  selectedLot.value = lot;
  showDeleteModal.value = true;
};

const closeFormModal = () => {
  showFormModal.value = false;
  selectedLot.value = null;
};

const onLotSaved = () => {
  closeFormModal();
  emit('lot-updated');
};

const handleDeleteLot = async () => {
  if (!selectedLot.value) return;
  try {
    await api.delete(`/admin/parking-lot/${selectedLot.value.id}`);
    notification.showNotification({ type: 'success', text: '✅ Parking lot deleted successfully.' });
    emit('lot-updated');
  } catch (err) {
    notification.showNotification({ type: 'error', text: '❌ ' + (err.response?.data?.message || 'Failed to delete parking lot.') });
  } finally {
    showDeleteModal.value = false;
  }
};

const handleDeleteSpot = async () => {
  if (!selectedSpot.value) return;
  try {
    await api.delete(`/admin/spot/${selectedSpot.value.id}`);
    notification.showNotification({ type: 'success', text: `✅ Spot ${selectedSpot.value.spot_number} deleted successfully.` });
    emit('lot-updated');
  } catch (err) {
    notification.showNotification({ type: 'error', text: '❌ ' + (err.response?.data?.message || 'Failed to delete spot.') });
  } finally {
    showAvailableSpotModal.value = false;
    selectedSpot.value = null;
  }
};
</script>

<style scoped>
.accordion-button:not(.collapsed) {
  color: var(--bs-primary);
  background-color: #e7f1ff;
}

.accordion-item {
  border: 1px solid #dee2e6;
  border-radius: .375rem;
  overflow: hidden;
}

.spot-box {
  width: 50px;
  height: 50px;
  border-radius: .375rem;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 0.9rem;
  border: 1px solid transparent;
  cursor: pointer;
  transition: all 0.2s ease;
}

.spot-box.available {
  background-color: var(--bs-success-bg-subtle);
  color: var(--bs-success-text-emphasis);
  border-color: var(--bs-success-border-subtle);
}

.spot-box.occupied {
  background-color: var(--bs-danger-bg-subtle);
  color: var(--bs-danger-text-emphasis);
  border-color: var(--bs-danger-border-subtle);
}

.spot-box:hover {
  transform: scale(1.05);
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
}

.modal {
  z-index: 1055;
}

.modal-backdrop {
  z-index: 1050;
}
</style>
