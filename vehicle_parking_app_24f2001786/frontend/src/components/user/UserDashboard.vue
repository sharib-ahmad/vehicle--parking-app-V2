<template>
  <div class="container py-5 mt-3">
    <header class="pb-3 mb-4 border-bottom">
      <h1 class="h2">User Dashboard</h1>
      <p class="text-muted">Find and book your parking spot with ease.</p>
    </header>

    <div class="row g-4">
      <!-- Left Column: Search and Results -->
      <div class="col-lg-7">
        <div class="card shadow-sm">
          <div class="card-header bg-light">
            <h5 class="mb-0">Find a Parking Lot</h5>
          </div>
          <div class="card-body">
            <div class="input-group mb-3">
              <input 
                type="text" 
                class="form-control" 
                placeholder="Enter pincode or location name..."
                v-model.trim="searchQuery"
                @keyup.enter="searchLots"
              >
              <button class="btn btn-primary" type="button" @click="searchLots" :disabled="isSearching">
                <span v-if="isSearching" class="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span>
                <i v-else class="bi bi-search me-1"></i>
                Search
              </button>
            </div>
            
            <hr>

            <!-- Search Results -->
            <div v-if="isSearching && searchResults.length === 0" class="text-center py-3">
              <div class="spinner-border text-primary" role="status"></div>
              <p class="mt-2 text-muted">Searching for parking lots...</p>
            </div>
            <div v-else-if="searchError" class="alert alert-danger">{{ searchError }}</div>
            <div v-else-if="searchResults.length > 0">
              <h6 class="text-muted mb-3">Available Lots</h6>
              <ul class="list-group">
                <li v-for="lot in searchResults" :key="lot.id" class="list-group-item d-flex justify-content-between align-items-center">
                  <div>
                    <h6 class="mb-0">{{ lot.prime_location_name }}</h6>
                    <small class="text-muted fw-semibold">{{ lot.address }}</small>
                    <br>
                    <small class="text-muted mt-1"><span class="fw-semibold me-2">{{ lot.floor_level }} Floor</span><span class="fw-bold">{{ formatTime(lot.open_time) }} - {{ formatTime(lot.close_time) }}</span></small>
                  </div>
                  <div class="d-flex align-items-center">
                    <span :class="['badge', availableSpots(lot) > 0 ? 'bg-success' : 'bg-danger', 'me-3']">
                      {{ availableSpots(lot) > 0 ? `${availableSpots(lot)} Available` : 'Full' }}
                    </span>
                    <button 
                      class="btn btn-sm"
                      :class="availableSpots(lot) > 0 ? 'btn-primary' : 'btn-secondary'"
                      @click="openBookingModal(lot)"
                      :disabled="availableSpots(lot) === 0"
                      :title="availableSpots(lot) === 0 ? 'This parking lot is full' : 'Book a spot'"
                    >
                      <i v-if="availableSpots(lot) === 0" class="bi bi-slash-circle me-1"></i>
                      {{ availableSpots(lot) > 0 ? 'Book Now' : 'Unavailable' }}
                    </button>
                  </div>
                </li>
              </ul>
            </div>
            <div v-else class="text-center text-muted py-3">
              <p>No parking lots found. Your search for "{{ initialSearchQuery }}" did not return any results.</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Right Column: Recent History -->
      <div class="col-lg-5">
        <div class="card shadow-sm">
           <div class="card-header bg-light">
            <h5 class="mb-0">My Bookings</h5>
          </div>
          <div class="card-body recent-bookings">
             <div v-if="reservations.length === 0" class="text-center text-muted py-3">
                <p>Your recent parking history will be displayed here once you make a booking.</p>
             </div>
             <ul v-else class="list-group list-group-flush">
                <li v-for="reservation in reservations" :key="reservation.id" class="list-group-item d-flex justify-content-between align-items-center">
                    <div>
                        <h6 class="mb-1">{{ reservation.location }}</h6>
                        <p class="mb-1 text-muted">Vehicle No: <span class="fw-semibold">{{ reservation.vehicle_number }}</span></p>
                        <p class="mb-0 text-muted">Parked at: <span class="fw-semibold">{{ formatTimestampToIST(reservation.parking_timestamp) }}</span></p>
                        <p v-show="reservation.leaving_timestamp" class="mb-0 text-muted">Left at: <span class="fw-semibold">{{ formatTimestampToIST(reservation.leaving_timestamp) }}</span></p>
                    </div>
                    <div>
                        <button v-if="reservation.status === 'active'" class="btn btn-sm btn-warning" @click="openReleaseModal(reservation)">
                            Release
                        </button>
                        <span v-else class="badge bg-secondary">Parked Out</span>
                    </div>
                </li>
             </ul>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Booking Modal -->
  <BookingModal 
    v-if="showBookingModal"
    :lot="selectedLot"
    @close="closeBookingModal"
    @booked="handleSuccessfulBooking"
  />

  <!-- Release Confirmation Modal -->
  <div v-if="showReleaseModal" class="modal fade show d-block" tabindex="-1" style="background-color: rgba(0,0,0,0.5);">
    <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">Confirm Release & Payment</h5>
                <button type="button" class="btn-close" @click="closeReleaseModal"></button>
            </div>
            <div class="modal-body" v-if="selectedReservation">
                <p><strong>Spot Number:</strong> {{ selectedReservation.parking_spot.spot_number }}</p>
                <p><strong>Username:</strong> {{ auth.user.username }}</p>
                <p><strong>Parking Rate:</strong> ₹{{ selectedReservation.parking_cost_per_hour }}/hour</p>
                <hr>
                <p><strong>Parking Time:</strong> {{ formatTimestampToIST(selectedReservation.parking_timestamp) }}</p>
                <p><strong>Leaving Time:</strong> {{ formatTimestampToIST(leavingTime) }}</p>
                <h5 class="mt-3"><strong>Total Cost:</strong> ₹{{ totalCost(selectedReservation).toFixed(2) }}</h5>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" @click="closeReleaseModal">Cancel</button>
                <button type="button" class="btn btn-primary" @click="proceedToPayment">Confirm & Pay</button>
            </div>
        </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import api from '@/services/api';
import { useAuthStore } from '@/stores/auth';
import BookingModal from './BookingModal.vue';
import { formatTimestampToIST, formatTime } from '@/utils/formatters';
import { totalCost } from '@/utils/totalCost';

const auth = useAuthStore();
const router = useRouter();
const searchQuery = ref('');
const initialSearchQuery = ref('');
const searchResults = ref([]);
const isSearching = ref(false);
const searchError = ref(null);
const reservations = ref([]);

const showBookingModal = ref(false);
const selectedLot = ref(null);

const showReleaseModal = ref(false);
const selectedReservation = ref(null);
const leavingTime = ref(null);

const searchLots = async () => {
  if (!searchQuery.value) return;
  initialSearchQuery.value = searchQuery.value;
  isSearching.value = true;
  searchError.value = null;
  searchResults.value = [];
  try {
    const response = await api.get(`/users/search?q=${searchQuery.value}`);
    searchResults.value = response.data;
  } catch (error) {
    searchError.value = 'Failed to fetch parking lots. Please try again.';
    console.error(error);
  } finally {
    isSearching.value = false;
  }
};

const fetchReservations = async () => {
  try {
    const response = await api.get(`/users/reservations`);
    reservations.value = response.data.sort((a,b)=>{
      if (a.status === 'active' && b.status !=='active'){
        return -1;
      }
      if(a.status !=='active' && b.status ==='active'){
        return 1;
      }
      return new Date(b.leaving_timestamp)- new Date(a.leaving_timestamp);
    });
  } catch (error) {
    console.error("Failed to fetch reservations:", error);
  }
};

const myData = async () => {
  try {
    const response = await api.get(`/users/me`);
    if (response.data.pincode) {
        searchQuery.value = response.data.pincode;
        searchLots();
    }
  } catch (error) {
    console.error(error);
  } 
}

const availableSpots = (lot) => {
    return lot.parking_spots.filter(spot => spot.status === 'available').length;
};

const openBookingModal = (lot) => {
  selectedLot.value = lot;
  showBookingModal.value = true;
};

const closeBookingModal = () => {
  showBookingModal.value = false;
  selectedLot.value = null;
};

const handleSuccessfulBooking = () => {
  closeBookingModal();
  searchLots();
  fetchReservations(); // Refresh booking history
};

const openReleaseModal = (reservation) => {
    selectedReservation.value = reservation;
    leavingTime.value = new Date();
    showReleaseModal.value = true;
};

const closeReleaseModal = () => {
    showReleaseModal.value = false;
    selectedReservation.value = null;
    leavingTime.value = null;
};

const proceedToPayment = () => {
  const reservation = selectedReservation.value;
  if (reservation) {
    const cost = totalCost(reservation).toFixed(2);
    // Navigate to the new payment page with necessary details in query params
    router.push({
      name: 'PaymentPage',
      params: { reservationId: reservation.id },
      query: { amount: cost, leavingTimestamp: leavingTime.value.toISOString() }
    });
  }
  closeReleaseModal();
};

onMounted(() => {
  myData();
  fetchReservations();
});
</script>

<style scoped>
.btn:disabled {
  cursor: not-allowed;
}
.recent-bookings {
    max-height: 400px;
    overflow-y: auto;
}
</style>
