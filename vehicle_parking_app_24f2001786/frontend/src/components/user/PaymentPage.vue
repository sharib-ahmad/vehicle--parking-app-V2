<template>
  <div class="payment-container d-flex align-items-center justify-content-center">
    <div class="payment-card card shadow-lg">
      <div class="card-body p-4 p-md-5">
        <h4 class="card-title text-center mb-2">Dummy Payment Gateway</h4>
        <p class="card-text text-center text-muted mb-4">
          You are paying <strong class="text-primary">₹{{ amount }}</strong> for your parking reservation.
        </p>
        
        <!-- Payment Method Tabs -->
        <ul class="nav nav-pills nav-fill mb-4" id="paymentTabs" role="tablist">
          <li class="nav-item" role="presentation">
            <button class="nav-link active" id="card-tab" data-bs-toggle="tab" data-bs-target="#card-payment" type="button" role="tab" aria-controls="card-payment" aria-selected="true">
              <i class="bi bi-credit-card-fill me-2"></i>Card
            </button>
          </li>
          <li class="nav-item" role="presentation">
            <button class="nav-link" id="upi-tab" data-bs-toggle="tab" data-bs-target="#upi-payment" type="button" role="tab" aria-controls="upi-payment" aria-selected="false">
              <i class="bi bi-qr-code me-2"></i>UPI / QR
            </button>
          </li>
        </ul>

        <!-- Tab Content -->
        <div class="tab-content" id="paymentTabsContent">
          <!-- Card Payment Form -->
          <div class="tab-pane fade show active" id="card-payment" role="tabpanel" aria-labelledby="card-tab">
            <div class="mb-3">
              <label for="cardNumber" class="form-label">Card Number</label>
              <input type="text" class="form-control" id="cardNumber" placeholder="0000 0000 0000 0000" v-model="cardDetails.number" maxlength="19">
            </div>
            <div class="row">
              <div class="col-7">
                <label for="expiryDate" class="form-label">Expiry Date</label>
                <input type="text" class="form-control" id="expiryDate" placeholder="MM/YY" v-model="cardDetails.expiry" maxlength="5">
              </div>
              <div class="col-5">
                <label for="cvv" class="form-label">CVV</label>
                <input type="text" class="form-control" id="cvv" placeholder="123" v-model="cardDetails.cvv" maxlength="3">
              </div>
            </div>
            <div class="d-grid mt-4">
              <button class="btn btn-primary btn-lg" @click="processCardPayment" :disabled="isProcessing">
                <span v-if="isProcessing" class="spinner-border spinner-border-sm me-2"></span>
                Pay with Card
              </button>
            </div>
          </div>

          <!-- UPI/QR Payment Form -->
          <div class="tab-pane fade" id="upi-payment" role="tabpanel" aria-labelledby="upi-tab">
              <div v-if="!showQrCode">
                <label for="upiId" class="form-label">Enter UPI ID</label>
                <div class="input-group">
                    <input type="text" class="form-control" id="upiId" placeholder="yourname@bank" v-model="upiId">
                    <button class="btn btn-outline-primary" @click="processUpiPayment" :disabled="isProcessing">Pay with UPI</button>
                </div>
                <div class="text-center my-3">OR</div>
                <div class="d-grid">
                    <button class="btn btn-secondary" @click="generateQrCode">Scan QR Code</button>
                </div>
              </div>
              <div v-else class="text-center">
                  <p class="text-muted">Scan the QR code with your payment app.</p>
                  <img :src="qrCodeUrl" alt="Dummy QR Code" class="img-fluid rounded mb-3">
                  <div class="d-grid">
                    <button class="btn btn-success" @click="confirmQrPayment" :disabled="isProcessing">
                        <span v-if="isProcessing" class="spinner-border spinner-border-sm me-2"></span>
                        I have Scanned & Paid
                    </button>
                  </div>
              </div>
          </div>
        </div>
        <div class="text-center mt-4">
            <button class="btn btn-link text-danger" @click="cancelPayment">Cancel Payment</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import api from '@/services/api';
import { useNotificationStore } from '@/stores/notification';

const route = useRoute();
const router = useRouter();
const notification = useNotificationStore();

const reservationId = route.params.reservationId;
const amount = route.query.amount;
const leavingTimestamp = route.query.leavingTimestamp;

const isProcessing = ref(false);

// Card Details
const cardDetails = ref({ number: '', expiry: '', cvv: '' });

// UPI Details
const upiId = ref('');
const showQrCode = ref(false);
const qrCodeUrl = computed(() => `https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=upi://pay?pa=dummy@pay&pn=ParkEase&am=${amount}&tid=${reservationId}`);

// Watch for changes on the card number for auto-formatting
watch(() => cardDetails.value.number, (newValue) => {
  const cleaned = newValue.replace(/\D/g, '').substring(0, 16);
  let formatted = cleaned.match(/.{1,4}/g)?.join(' ') || '';
  if (formatted !== cardDetails.value.number) {
    cardDetails.value.number = formatted;
  }
});

// Watch for changes on the expiry date for auto-formatting
watch(() => cardDetails.value.expiry, (newValue) => {
  const cleaned = newValue.replace(/\D/g, '').substring(0, 4);
  let formatted = cleaned;
  if (cleaned.length > 2) {
    formatted = `${cleaned.substring(0, 2)}/${cleaned.substring(2)}`;
  }
  if (formatted !== cardDetails.value.expiry) {
    cardDetails.value.expiry = formatted;
  }
});

// --- Validation Functions ---
const validateCardDetails = () => {
    if (cardDetails.value.number.replace(/\s/g, '').length !== 16) {
        notification.showNotification({ type: 'error', text: 'Please enter a valid 16-digit card number.' });
        return false;
    }
    if (!/^(0[1-9]|1[0-2])\/\d{2}$/.test(cardDetails.value.expiry)) {
        notification.showNotification({ type: 'error', text: 'Please enter a valid expiry date in MM/YY format.' });
        return false;
    }
    if (cardDetails.value.cvv.length !== 3) {
        notification.showNotification({ type: 'error', text: 'Please enter a valid 3-digit CVV.' });
        return false;
    }
    return true;
};

const validateUpiId = () => {
    if (!upiId.value.includes('@')) {
        notification.showNotification({ type: 'error', text: 'Please enter a valid UPI ID (e.g., yourname@bank).' });
        return false;
    }
    return true;
};

// --- Payment Processing ---
const processCardPayment = () => {
    if (validateCardDetails()) {
        handlePaymentConfirmation('Credit Card');
    }
};

const processUpiPayment = () => {
    if (validateUpiId()) {
        handlePaymentConfirmation('UPI');
    }
};

const generateQrCode = () => {
    showQrCode.value = true;
};

const confirmQrPayment = () => {
    handlePaymentConfirmation('QR Code');
};

const handlePaymentConfirmation = async (paymentMethod) => {
  isProcessing.value = true;
  try {
    // Simulate network delay for a better user experience
    await new Promise(resolve => setTimeout(resolve, 1500));

    await api.post('users/payments', {
      reservation_id: reservationId,
      amount: parseFloat(amount),
      payment_method: paymentMethod,
    });

    await api.put(`users/reservations?res_id=${reservationId}`, {
      leaving_timestamp: leavingTimestamp,
    });
    
    notification.showNotification({ type: "success", text: "✅ Payment successful! Your spot has been released." });
    router.push({ name: 'UserDashboard' });

  } catch (error) {
    console.error("Failed to process payment:", error);
    notification.showNotification({ type: "error", text: "❌ There was an error processing your payment." });
    isProcessing.value = false;
  }
};

const cancelPayment = () => {
    notification.showNotification({ type: "info", text: "ℹ️ Payment was cancelled." });
    router.push({ name: 'UserDashboard' });
};
</script>

<style scoped>
.payment-container {
  min-height: 100vh;
  background-color: #f8f9fa;
}
.payment-card {
  width: 100%;
  max-width: 500px;
  border: none;
  border-radius: .75rem;
}
.nav-pills .nav-link {
    color: #6c757d;
}
.nav-pills .nav-link.active {
    background-color: var(--bs-primary);
}
</style>

