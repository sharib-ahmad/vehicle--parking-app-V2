<template>
  <div class="container py-5 mt-4">
    <header class="pb-3 mb-4 border-bottom">
      <h1 class="h2">Admin Summary Dashboard</h1>
      <p class="text-muted">An overview of parking lot performance and revenue.</p>
    </header>

    <div v-if="isLoading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="mt-2">Loading summary data...</p>
    </div>

    <div v-else-if="error" class="alert alert-danger">
      Failed to load summary data. Please try again later.
    </div>

    <div v-else class="row g-4">
      <!-- Key Metric Cards -->
      <div class="col-md-4">
        <div class="card h-100 shadow-sm">
          <div class="card-body text-center">
            <h5 class="card-title text-muted">Total Revenue</h5>
            <p class="card-text fs-2 fw-bold">₹{{ totalRevenue.toFixed(2) }}</p>
          </div>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card h-100 shadow-sm">
          <div class="card-body text-center">
            <h5 class="card-title text-muted">Total Parking Lots</h5>
            <p class="card-text fs-2 fw-bold">{{ summaryData.length }}</p>
          </div>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card h-100 shadow-sm">
          <div class="card-body text-center">
            <h5 class="card-title text-muted">Overall Occupancy</h5>
            <p class="card-text fs-2 fw-bold">{{ overallOccupancy.toFixed(1) }}%</p>
          </div>
        </div>
      </div>

      <!-- Full-width Revenue Chart -->
      <div class="col-12">
        <div class="card shadow-sm">
          <div class="card-body">
            <h5 class="card-title">Revenue by Parking Lot</h5>
            <!-- FIX: Added a positioned container with a defined height to prevent resizing loop -->
            <div class="chart-container" style="position: relative; height: 40vh;">
              <canvas ref="revenueChartCanvas"></canvas>
            </div>
          </div>
        </div>
      </div>

      <!-- Row for smaller charts -->
      <!-- Pricing Analysis Chart -->
      <div class="col-lg-4">
        <div class="card shadow-sm h-100">
          <div class="card-body d-flex flex-column">
            <h5 class="card-title">Pricing Analysis (₹/hour)</h5>
            <div class="flex-grow-1 position-relative">
              <canvas ref="priceChartCanvas"></canvas>
            </div>
          </div>
        </div>
      </div>

      <!-- Occupancy by Lot Chart -->
      <div class="col-lg-4">
        <div class="card shadow-sm h-100">
          <div class="card-body position-relative d-flex flex-column">
            <h5 class="card-title">Occupancy Rate</h5>
            <div class="flex-grow-1 position-relative">
                <canvas ref="occupancyChartCanvas"></canvas>
                <div v-if="isOccupancyEmpty" class="empty-chart-message">
                No Occupied Spots
                </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Payment Status Chart -->
      <div class="col-lg-4">
        <div class="card shadow-sm h-100">
          <div class="card-body d-flex flex-column">
            <h5 class="card-title">Payment Status</h5>
             <div class="flex-grow-1 position-relative">
                <canvas ref="paymentStatusChartCanvas"></canvas>
             </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed, watch, nextTick } from 'vue';
import api from '@/services/api';
import Chart from 'chart.js/auto';
import { useNotificationStore } from '@/stores/notification';

const notification = useNotificationStore();
const summaryData = ref([]);
const paymentSummary = ref(null);
const isLoading = ref(true);
const error = ref(null);

// Template refs for canvas elements
const revenueChartCanvas = ref(null);
const occupancyChartCanvas = ref(null);
const priceChartCanvas = ref(null);
const paymentStatusChartCanvas = ref(null);

let revenueChartInstance = null;
let occupancyChartInstance = null;
let priceChartInstance = null;
let paymentStatusChartInstance = null;

const fetchSummaryData = async () => {
  isLoading.value = true;
  error.value = null;
  try {
    const response = await api.get('/admin/summary');
    summaryData.value = response.data.lots || []; 
    paymentSummary.value = response.data.payment_summary || { pending: 0, paid: 0 };
  } catch (err)
 {
    error.value = err;
    notification.showNotification({ type: 'error', text: '❌ Failed to fetch summary data.' });
  } finally {
    isLoading.value = false;
  }
};

onMounted(fetchSummaryData);

// Cleanup charts when the component is unmounted to prevent memory leaks and rendering bugs
onUnmounted(() => {
  if (revenueChartInstance) revenueChartInstance.destroy();
  if (occupancyChartInstance) occupancyChartInstance.destroy();
  if (priceChartInstance) priceChartInstance.destroy();
  if (paymentStatusChartInstance) paymentStatusChartInstance.destroy();
});

// Watch for changes in summaryData and then render the charts
watch(summaryData, async (newData) => {
  if (newData) {
    await nextTick(); // Wait for the DOM to update
    renderCharts();
  }
}, { immediate: false });

const chartLabels = computed(() => summaryData.value.map(lot => lot.prime_location_name));
const revenueValues = computed(() => summaryData.value.map(lot => lot.revenue));

const occupancyRates = computed(() => summaryData.value.map(lot => {
    const totalSpots = lot.maximum_number_of_spots || 0;
    if (totalSpots === 0) return 0;
    const occupiedSpots = lot.occupied_spots || 0;
    return (occupiedSpots / totalSpots) * 100;
}));

const isOccupancyEmpty = computed(() => {
  return occupancyRates.value.every(rate => rate === 0);
});

const priceValues = computed(() => summaryData.value.map(lot => lot.price_per_hour));

const paymentStatusData = computed(() => {
    if (!paymentSummary.value) return [0, 0];
    return [paymentSummary.value.paid || 0, paymentSummary.value.pending || 0];
});

const totalRevenue = computed(() => revenueValues.value.reduce((acc, cur) => acc + cur, 0));

const overallOccupancy = computed(() => {
    const totalSpots = summaryData.value.reduce((acc, lot) => acc + (lot.maximum_number_of_spots || 0), 0);
    const totalOccupied = summaryData.value.reduce((acc, lot) => acc + (lot.occupied_spots || 0), 0);
    if (totalSpots === 0) return 0;
    return (totalOccupied / totalSpots) * 100;
});


const renderCharts = () => {
  if (revenueChartInstance) revenueChartInstance.destroy();
  if (occupancyChartInstance) occupancyChartInstance.destroy();
  if (priceChartInstance) priceChartInstance.destroy();
  if (paymentStatusChartInstance) paymentStatusChartInstance.destroy();

  const revenueCtx = revenueChartCanvas.value;
  const occupancyCtx = occupancyChartCanvas.value;
  const priceCtx = priceChartCanvas.value;
  const paymentStatusCtx = paymentStatusChartCanvas.value;

  if (!revenueCtx || !occupancyCtx || !priceCtx || !paymentStatusCtx) {
      return; 
  }

  // Revenue Chart (Bar)
  revenueChartInstance = new Chart(revenueCtx, {
    type: 'bar',
    data: {
      labels: chartLabels.value,
      datasets: [{
        label: 'Revenue (₹)',
        data: revenueValues.value,
        backgroundColor: 'rgba(54, 162, 235, 0.6)',
        borderColor: 'rgba(54, 162, 235, 1)',
        borderWidth: 1
      }]
    },
    options: { responsive: true, maintainAspectRatio: false, scales: { y: { beginAtZero: true } } }
  });

  // Occupancy Chart (Doughnut)
  if (!isOccupancyEmpty.value) {
    occupancyChartInstance = new Chart(occupancyCtx, {
        type: 'doughnut',
        data: {
        labels: chartLabels.value,
        datasets: [{
            label: 'Occupancy (%)', data: occupancyRates.value,
            backgroundColor: ['rgba(255, 99, 132, 0.6)','rgba(75, 192, 192, 0.6)','rgba(255, 206, 86, 0.6)'],
            borderColor: ['rgba(255, 99, 132, 1)','rgba(75, 192, 192, 1)','rgba(255, 206, 86, 1)'],
            borderWidth: 1
        }]
        },
        options: { responsive: true, maintainAspectRatio: false }
    });
  }

  // Price Chart (Bar)
  priceChartInstance = new Chart(priceCtx, {
    type: 'bar',
    data: {
      labels: chartLabels.value,
      datasets: [{
        label: 'Price per Hour (₹)', data: priceValues.value,
        backgroundColor: 'rgba(153, 102, 255, 0.6)',
        borderColor: 'rgba(153, 102, 255, 1)',
        borderWidth: 1
      }]
    },
    options: { responsive: true, maintainAspectRatio: false, scales: { y: { beginAtZero: true } } }
  });

  // Payment Status Chart (Pie)
  paymentStatusChartInstance = new Chart(paymentStatusCtx, {
    type: 'pie',
    data: {
      labels: ['Paid', 'Pending'],
      datasets: [{
        label: 'Payment Status',
        data: paymentStatusData.value,
        backgroundColor: ['rgba(75, 192, 192, 0.6)', 'rgba(255, 159, 64, 0.6)'],
        borderColor: ['rgba(75, 192, 192, 1)', 'rgba(255, 159, 64, 1)'],
        borderWidth: 1
      }]
    },
    options: { responsive: true, maintainAspectRatio: false }
  });
};
</script>

<style scoped>
.card {
  border: none;
  border-radius: .75rem;
}
.empty-chart-message {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: #6c757d;
  font-weight: 500;
}
</style>

