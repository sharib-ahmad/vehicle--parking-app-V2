<template>
  <div v-if="show">
    <!-- Main Modal Window -->
    <div class="modal fade show d-block" tabindex="-1" @click.self="close">
      <div class="modal-dialog modal-lg modal-dialog-centered modal-dialog-scrollable">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">{{ isEditMode ? 'Edit Parking Lot' : 'Add New Parking Lot' }}</h5>
            <button type="button" class="btn-close" @click="close"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="handleSubmit">
              <div class="row">
                <!-- Column 1: Location Details -->
                <div class="col-md-6">
                  <FormInput id="lot-name" v-model="form.prime_location_name" label="Location Name" placeholder="e.g., Downtown Central" :error="errors.prime_location_name" :disabled="isEditMode" />
                  
                  <div class="mb-3">
                    <label for="lot-pincode" class="form-label">Pincode</label>
                    <div class="input-group">
                      <input id="lot-pincode" v-model.trim="form.pin_code" class="form-control" :class="{'is-invalid': errors.pin_code || pincodeError}" placeholder="Enter 6-digit pincode" :disabled="isEditMode" />
                      <span v-if="isPincodeLoading" class="input-group-text">
                        <div class="spinner-border spinner-border-sm" role="status"></div>
                      </span>
                    </div>
                    <div v-if="errors.pin_code" class="invalid-feedback d-block">{{ errors.pin_code }}</div>
                    <div v-if="pincodeError" class="invalid-feedback d-block">{{ pincodeError }}</div>
                  </div>

                  <FormInput id="lot-city" v-model="form.city" label="City" :error="errors.city" :disabled="true" />
                  <FormInput id="lot-district" v-model="form.district" label="District" :error="errors.district" :disabled="true" />
                  <FormInput id="lot-state" v-model="form.state" label="State" :error="errors.state" :disabled="true" />
                </div>

                <!-- Column 2: Operational Details -->
                <div class="col-md-6">
                   <FormInput id="lot-floor" v-model="form.floor_level" label="Floor Level" placeholder="e.g., Ground, B1" :error="errors.floor_level" :disabled="isEditMode" />
         
                  <p v-if="isEditMode" class="text-muted small">You can only edit the fields below.</p>
                  <FormInput id="lot-price" v-model.number="form.price_per_hour" label="Price per Hour (₹)" type="number" :error="errors.price_per_hour" />
                  <FormInput id="lot-spots" v-model.number="form.maximum_number_of_spots" label="Maximum Spots" type="number" :error="errors.maximum_number_of_spots" />
                  <FormInput id="lot-open" v-model="form.open_time" label="Opening Time" type="time" :error="errors.open_time" />
                  <FormInput id="lot-close" v-model="form.close_time" label="Closing Time" type="time" :error="errors.close_time" />
                </div>
              </div>
            </form>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="close">Cancel</button>
            <button type="button" class="btn btn-primary" @click="handleSubmit" :disabled="isLoading">
              <span v-if="isLoading" class="spinner-border spinner-border-sm me-1"></span>
              {{ isLoading ? 'Saving...' : isEditMode ? 'Update' : 'Create' }}
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
import { ref, reactive, watch, computed } from 'vue';
import api from '@/services/api';
import { useNotificationStore } from '@/stores/notification';
import FormInput from '@/components/common/FormInput.vue';

const props = defineProps({
  show: { type: Boolean, required: true },
  lot: { type: Object, default: null },
});

const emit = defineEmits(['close', 'saved']);
const notification = useNotificationStore();
const isLoading = ref(false);
const isPincodeLoading = ref(false);
const pincodeError = ref(null);

const isEditMode = computed(() => !!props.lot?.id);

const initialFormState = {
  prime_location_name: '',
  city: '',
  state: '',
  pin_code: '',
  district: '',
  price_per_hour: null,
  maximum_number_of_spots: null,
  floor_level: 'Ground',
  open_time: '09:00',
  close_time: '22:00',
};

const form = reactive({ ...initialFormState });
const errors = reactive({});

// --- PIN Code API Logic ---
watch(() => form.pin_code, async (newPincode) => {
  // Don't run this logic in edit mode
  if (isEditMode.value) return;

  // Clear fields if pincode is not 6 digits
  if (newPincode?.length !== 6) {
    form.city = '';
    form.district = '';
    form.state = '';
    pincodeError.value = null;
    return;
  }

  isPincodeLoading.value = true;
  pincodeError.value = null;
  try {
    const response = await fetch(`https://api.postalpincode.in/pincode/${newPincode}`);
    if (!response.ok) throw new Error('Network response was not ok.');
    
    const data = await response.json();
    if (data[0].Status === 'Success') {
      const postOffice = data[0].PostOffice[0];
      form.city = postOffice.Block;
      form.district = postOffice.District;
      form.state = postOffice.State;
    } else {
      throw new Error(data[0].Message || 'Invalid PIN code.');
    }
  } catch (error) {
    pincodeError.value = error.message;
    form.city = '';
    form.district = '';
    form.state = '';
  } finally {
    isPincodeLoading.value = false;
  }
});


watch(() => props.show, (newVal) => {
  if (newVal) {
    Object.keys(errors).forEach(key => delete errors[key]);
    pincodeError.value = null;
    if (isEditMode.value) {
      Object.assign(form, props.lot);
    } else {
      Object.assign(form, initialFormState);
    }
  }
});

const close = () => {
  emit('close');
};

const handleSubmit = async () => {
  isLoading.value = true;
  Object.keys(errors).forEach(key => delete errors[key]);

  try {
    if (isEditMode.value) {
      const payload = {
        price_per_hour: form.price_per_hour,
        maximum_number_of_spots: form.maximum_number_of_spots,
        open_time: form.open_time,
        close_time: form.close_time,
      };
      await api.put(`/admin/parking-lot/${props.lot.id}`, payload);
      notification.showNotification({ type: 'success', text: '✅ Parking lot updated successfully!' });
    } else {
      await api.post('/admin/parking-lots', form);
      notification.showNotification({ type: 'success', text: '✅ Parking lot created successfully!' });
    }
  } catch (error) {
    if (error.response && error.response.status === 422) {
      Object.assign(errors, error.response.data.errors);
    } else {
      const action = isEditMode.value ? 'update' : 'create';
      notification.showNotification({
        type: 'error',
        text: `❌ Failed to ${action} parking lot. ` + (error.response?.data?.message || 'Please try again.'),
      });
    }
  } finally {
    isLoading.value = false;
    emit('saved');
  }
};
</script>

<style scoped>
/* Scoped styles remain the same */
.modal.d-block { display: block; }
.modal-backdrop { z-index: 1050; opacity: 0.5; }
.modal { z-index: 1055; }
</style>

