<template>
  <div>
    <!-- Main Modal -->
    <div class="modal fade show d-block" tabindex="-1" @click.self="close">
      <div class="modal-dialog modal-dialog-centered modal-lg">
        <div class="modal-content shadow-lg border-0">
          <!-- Header -->
          <div class="modal-header bg-light border-bottom-0">
            <h5 class="modal-title" id="bookingModalLabel">Book Your Spot</h5>
            <button type="button" class="btn-close" @click="close" aria-label="Close"></button>
          </div>

          <!-- Body -->
          <div class="modal-body p-4">
            <div class="row g-4">
              <!-- Left Column: Booking Details -->
              <div class="col-md-5">
                <div class="card h-100 border-light bg-light">
                  <div class="card-body">
                    <h6 class="card-title text-primary mb-3">Booking Summary</h6>
                    <ul class="list-unstyled">
                      <li class="mb-3 d-flex align-items-start">
                        <svg class="bi me-2 text-muted flex-shrink-0" width="20" height="20" fill="currentColor" viewBox="0 0 16 16"><path d="M8 8a3 3 0 1 0 0-6 3 3 0 0 0 0 6m2-3a2 2 0 1 1-4 0 2 2 0 0 1 4 0m4 8c0 1-1 1-1 1H3s-1 0-1-1 1-4 6-4 6 3 6 4m-1-.004c-.001-.246-.154-.986-.832-1.664C11.516 10.68 10.289 10 8 10s-3.516.68-4.168 1.332c-.678.678-.83 1.418-.832 1.664z"/></svg>
                        <div>
                          <strong>{{ form.username }}</strong>
                          <small class="d-block text-muted">Username</small>
                        </div>
                      </li>
                      <li class="mb-3 d-flex align-items-start">
                        <svg class="bi me-2 text-muted flex-shrink-0" width="20" height="20" fill="currentColor" viewBox="0 0 16 16"><path d="M8 16s6-5.686 6-10A6 6 0 0 0 2 6c0 4.314 6 10 6 10M8 9a3 3 0 1 1 0-6 3 3 0 0 1 0 6"/></svg>
                        <div>
                          <strong>{{ lot.prime_location_name }}</strong>
                          <small class="d-block text-muted">Parking Lot</small>
                        </div>
                      </li>
                       <li class="d-flex align-items-start">
                        <svg class="bi me-2 text-muted flex-shrink-0" width="20" height="20" fill="currentColor" viewBox="0 0 16 16"><path d="M4 1.5a.5.5 0 0 1 .5.5v1.5H10V2a.5.5 0 0 1 1 0v1.5h1.5a.5.5 0 0 1 .5.5v12a.5.5 0 0 1-.5.5H2a.5.5 0 0 1-.5-.5v-12a.5.5 0 0 1 .5-.5H4V2a.5.5 0 0 1 .5-.5m10 3H2v10h12zM3 5.5a.5.5 0 0 1 .5-.5h2a.5.5 0 0 1 0 1h-2a.5.5 0 0 1-.5-.5m0 2a.5.5 0 0 1 .5-.5h2a.5.5 0 0 1 0 1h-2a.5.5 0 0 1-.5-.5"/></svg>
                        <div>
                          <strong>Spot #{{ form.spot_number }}</strong>
                          <small class="d-block text-muted">Assigned Spot</small>
                        </div>
                      </li>
                    </ul>
                  </div>
                </div>
              </div>

              <!-- Right Column: Vehicle Details Form -->
              <div class="col-md-7">
                <h6 class="text-primary mb-3">Vehicle Information</h6>
                <form @submit.prevent="handleBooking" class="row g-3">
                  <div class="col-12 position-relative">
                    <label for="vehicle-number" class="form-label">Vehicle Number</label>
                    <input type="text" class="form-control" id="vehicle-number" v-model="form.vehicle_number" placeholder="e.g., MH01AB1234" :class="{ 'is-invalid': errors.vehicle_number }">
                    <div v-if="isFetchingVehicle" class="spinner-border spinner-border-sm text-secondary position-absolute end-0 top-50 me-3" style="margin-top: 0.6rem;" role="status">
                      <span class="visually-hidden">Loading...</span>
                    </div>
                    <div v-if="errors.vehicle_number" class="invalid-feedback">{{ errors.vehicle_number }}</div>
                  </div>

                  <div class="col-md-6">
                    <label for="fuel-type" class="form-label">Fuel Type</label>
                    <select id="fuel-type" v-model="form.fuel_type" class="form-select" :class="{ 'is-invalid': errors.fuel_type }" :disabled="vehicleFound">
                       <option disabled value="">Select Fuel Type</option>
                       <option v-for="type in fuelTypes" :key="type" :value="type">{{ type }}</option>
                    </select>
                    <div v-if="errors.fuel_type" class="invalid-feedback">{{ errors.fuel_type }}</div>
                  </div>

                  <div class="col-md-6">
                    <label for="vehicle-color" class="form-label">Color</label>
                    <select id="vehicle-color" v-model="form.color" class="form-select" :disabled="vehicleFound || loading.colors" :class="{ 'is-invalid': errors.color }">
                      <option disabled value="">{{ loading.colors ? "Loading..." : "Select Color" }}</option>
                      <option v-for="color in colors" :key="color" :value="color">{{ color }}</option>
                    </select>
                    <div v-if="errors.color" class="invalid-feedback">{{ errors.color }}</div>
                  </div>

                  <div class="col-md-6">
                    <label for="vehicle-brand" class="form-label">Brand</label>
                    <select id="vehicle-brand" v-model="form.brand" class="form-select" :disabled="vehicleFound || loading.brands" :class="{ 'is-invalid': errors.brand }">
                      <option disabled value="">{{ loading.brands ? "Loading..." : "Select Brand" }}</option>
                      <option v-for="brand in brands" :key="brand" :value="brand">{{ brand }}</option>
                    </select>
                    <div v-if="errors.brand" class="invalid-feedback">{{ errors.brand }}</div>
                  </div>

                  <div class="col-md-6">
                    <label for="vehicle-model" class="form-label">Model</label>
                    <select id="vehicle-model" v-model="form.model" class="form-select" :disabled="vehicleFound || !form.brand || loading.models" :class="{ 'is-invalid': errors.model }">
                      <option disabled value="">{{ loading.models ? "Loading..." : "Select Model" }}</option>
                      <option v-for="model in models" :key="model" :value="model">{{ model }}</option>
                    </select>
                     <div v-if="errors.model" class="invalid-feedback">{{ errors.model }}</div>
                  </div>
                </form>
              </div>
            </div>
          </div>

          <!-- Footer -->
          <div class="modal-footer bg-light border-top-0">
            <button type="button" class="btn btn-outline-secondary" @click="close">Cancel</button>
            <button type="button" class="btn btn-primary px-4" @click="handleBooking" :disabled="isSubmitting">
              <span v-if="isSubmitting" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
              {{ isSubmitting ? "Booking..." : "Confirm Booking" }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal Backdrop -->
    <div class="modal-backdrop fade show"></div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch, computed } from "vue";
import api from "@/services/api";
import { useNotificationStore } from "@/stores/notification";
import { useAuthStore } from "@/stores/auth";

const props = defineProps({
  lot: { type: Object, required: true },
});

const emit = defineEmits(["close", "booked"]);
const notification = useNotificationStore();
const auth = useAuthStore();

const isSubmitting = ref(false);
const vehicleFound = ref(false);
const isFetchingVehicle = ref(false);
let debounceTimer = null;

const sortedSpots = computed(() => {
  return [...props.lot.parking_spots].sort((a, b) => {
    const [lotA, spotA] = a.spot_number.split("-").map(Number);
    const [lotB, spotB] = b.spot_number.split("-").map(Number);

    if (lotA !== lotB) return lotA - lotB;
    return spotA - spotB;
  });
});

const firstAvailable = computed(() =>
  sortedSpots.value.find(spot => spot.status === "available")
);

const form = reactive({
  username: auth.user?.username || "",
  lot_id: props.lot.id,
  spot_number: firstAvailable.value?.spot_number || "N/A",
  spot_id: firstAvailable.value?.id || "N/A",
  fuel_type: "",
  vehicle_number: "",
  brand: "",
  model: "",
  color: "",
});

const errors = reactive({});
const fuelTypes = ["Petrol", "Diesel", "Electric", "CNG", "Hybrid"];

const brands = ref([]);
const models = ref([]);
const colors = ref([]);
const loading = reactive({ brands: false, models: false, colors: false });

const fetchInitialData = async () => {
  loading.brands = true;
  loading.colors = true;
  try {
    const [brandsRes, colorsRes] = await Promise.all([
      api.get("/public/brands"),
      api.get("/public/colors"),
    ]);
    brands.value = brandsRes.data.brands;
    colors.value = colorsRes.data.colors;
  } catch (err) {
    notification.showNotification({ type: "error", text: "❌ Failed to load vehicle data." });
  } finally {
    loading.brands = false;
    loading.colors = false;
  }
};
onMounted(fetchInitialData);

const resetVehicleFields = () => {
  form.fuel_type = "";
  form.brand = "";
  form.model = "";
  form.color = "";
  vehicleFound.value = false;
  ['fuel_type', 'color', 'brand', 'model'].forEach(key => delete errors[key]);
};

watch(() => form.vehicle_number, (newValue) => {
  clearTimeout(debounceTimer);
  const formatted = (newValue || "").toUpperCase().replace(/\s/g, '');
  
  if (newValue !== formatted) {
    form.vehicle_number = formatted;
    return;
  }

  if (formatted.length <= 8) {
    if (vehicleFound.value) resetVehicleFields();
    return;
  }

  debounceTimer = setTimeout(async () => {
    isFetchingVehicle.value = true;
    try {
      const response = await api.get(`/users/booking/${formatted}`);
      const vehicleData = response.data;

      loading.models = true;
      const modelsRes = await api.get(`/public/models/${vehicleData.brand}`);
      models.value = modelsRes.data.models;
      loading.models = false;
      
      form.brand = vehicleData.brand;
      form.model = vehicleData.model;
      form.color = vehicleData.color;
      form.fuel_type = vehicleData.fuel_type;
      
      vehicleFound.value = true;
      notification.showNotification({ type: "info", text: "ℹ️ Existing vehicle details loaded." });
    } catch (error) {
      if (error.response?.status === 404) {
        resetVehicleFields();
      }
    } finally {
      isFetchingVehicle.value = false;
    }
  }, 500);
});

watch(() => form.brand, async (newBrand) => {
  if (vehicleFound.value) return;
  models.value = [];
  form.model = "";
  if (!newBrand) return;

  loading.models = true;
  try {
    const res = await api.get(`/public/models/${newBrand}`);
    models.value = res.data.models;
  } catch (err) {
    notification.showNotification({ type: "error", text: `Failed to load models for ${newBrand}.`});
  } finally {
    loading.models = false;
  }
});

const close = () => emit("close");

const validateForm = () => {
  Object.keys(errors).forEach(key => delete errors[key]);
  const requiredFields = {
    vehicle_number: "Vehicle number is required.",
    fuel_type: "Please select a fuel type.",
    color: "Please select a color.",
    brand: "Please select a brand.",
    model: "Please select a model.",
  };
  for (const field in requiredFields) {
    if (!form[field]) errors[field] = requiredFields[field];
  }
  return Object.keys(errors).length === 0;
};

const handleBooking = async () => {
  if (!validateForm()) {
    notification.showNotification({ type: "warning", text: "Please fill out all required fields." });
    return;
  }
  isSubmitting.value = true;
  try {
    const response = await api.post('/users/booking_spot', form);
    notification.showNotification({
      type: "success",
      text: `✅ Booking successful! Your spot is #${form.spot_number}.`,
    });
    emit("booked", response.data);
    close();
  } catch (err) {
    if (err.response?.status === 422 && err.response.data.errors) {
      Object.assign(errors, err.response.data.errors);
      notification.showNotification({ type: "warning", text: "Please correct the errors from the server." });
    } else {
      notification.showNotification({
        type: "error",
        text: "❌ " + (err.response?.data?.message || "An unexpected error occurred."),
      });
    }
  } finally {
    isSubmitting.value = false;
  }
};
</script>

<style scoped>
.modal-backdrop { z-index: 1050; opacity: 0.5; }
.modal { z-index: 1055; }
.form-label { font-weight: 500; }
.card-title { font-weight: 600; }
</style>

