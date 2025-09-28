<template>
  <div class="mb-3">
    <label :for="id" class="form-label">{{ label }}</label>
    <div v-if="isPassword" class="input-group">
      <input :id="id" :value="modelValue" @input="$emit('update:modelValue', $event.target.value)"
        :type="isPasswordVisible ? 'text' : 'password'" :class="{ 'is-invalid': error }" class="form-control"
        :placeholder="placeholder" :disabled="disabled" />
      <button @click="togglePasswordVisibility" class="btn btn-outline-secondary" type="button">
        {{ isPasswordVisible ? 'Hide' : 'Show' }}
      </button>
      <div v-if="error" class="invalid-feedback">{{ error }}</div>
    </div>
    <input v-else :id="id" :value="modelValue" @input="$emit('update:modelValue', $event.target.value)" :type="type"
      :class="{ 'is-invalid': error }" class="form-control" :placeholder="placeholder"
      :step="type === 'number' ? '0.01' : null" :disabled="disabled" />
    <div v-if="error" class="invalid-feedback">{{ error }}</div>
  </div>
</template>

<script setup>
import { ref } from 'vue';

defineProps({
  id: { type: String, required: true },
  modelValue: { type: [String, Number], default: '' },
  label: { type: String, required: true },
  error: { type: String, default: null },
  type: { type: String, default: 'text' },
  placeholder: { type: String, default: '' },
  isPassword: { type: Boolean, default: false },
  disabled: { type: Boolean, default: false }, // New prop
});

defineEmits(['update:modelValue']);

const isPasswordVisible = ref(false);

const togglePasswordVisibility = () => {
  isPasswordVisible.value = !isPasswordVisible.value;
};
</script>

<style scoped>
/* Added styling for disabled inputs */
input:disabled {
  background-color: #e9ecef;
  cursor: not-allowed;
}
</style>
