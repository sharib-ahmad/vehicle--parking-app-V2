<template>
  <div class="container py-5 mt-4">
    <header class="d-flex justify-content-between align-items-center pb-3 mb-4 border-bottom">
      <div>
        <h1 class="h2">My Parking Summary</h1>
        <p class="text-muted mb-0">An overview of your parking history and expenses.</p>
      </div>
      <button 
        class="btn btn-primary" 
        @click="triggerCsvExport" 
        :disabled="isExporting">
        <span v-if="isExporting" class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
        <span v-if="isExporting"> Exporting...</span>
        <span v-else>Download CSV Report</span>
      </button>
    </header>

    <div v-if="isLoading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="mt-2">Loading your summary data...</p>
    </div>

    <div v-else-if="error" class="alert alert-danger">
      Failed to load your summary data. Please try again later.
    </div>

    <div v-else class="row g-4">
        <!-- Monthly Bookings Chart -->
        <div class="col-lg-6">
            <div class="card shadow-sm h-100">
                <div class="card-body d-flex flex-column">
                    <h5 class="card-title">Reservations per Month</h5>
                    <div class="flex-grow-1 position-relative">
                        <canvas ref="monthlyBookingsCanvas"></canvas>
                    </div>
                </div>
            </div>
        </div>

        <!-- Favorite Lots Chart -->
        <div class="col-lg-6">
            <div class="card shadow-sm h-100">
                <div class="card-body d-flex flex-column">
                    <h5 class="card-title">Most Used Parking Lots</h5>
                    <div class="flex-grow-1 position-relative">
                        <canvas ref="favoriteLotsCanvas"></canvas>
                        <div v-if="!hasParkingHistory" class="empty-chart-message">
                            No Parking History
                        </div>
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
const summaryData = ref(null);
const isLoading = ref(true);
const error = ref(null);
const isExporting = ref(false); // For the export button loading state

// Template refs
const monthlyBookingsCanvas = ref(null);
const favoriteLotsCanvas = ref(null);

// Chart instances
let monthlyBookingsChart = null;
let favoriteLotsChart = null;

const hasParkingHistory = computed(() => {
    return summaryData.value && summaryData.value.favorite_lots && Object.keys(summaryData.value.favorite_lots).length > 0;
});


const fetchSummaryData = async () => {
  isLoading.value = true;
  error.value = null;
  try {
    const response = await api.get('/users/summary');
    summaryData.value = response.data;
  } catch (err) {
    error.value = err;
    notification.showNotification({ type: 'error', text: '❌ Failed to fetch your summary.' });
  } finally {
    isLoading.value = false;
  }
};

const triggerCsvExport = async () => {
  isExporting.value = true;
  try {
    // This calls the POST /users/export-csv endpoint
    await api.post('/users/export-csv');
    notification.showNotification({ 
      type: 'success', 
      text: '✅ Export started! Your report will be emailed to you shortly.' 
    });
  } catch (err) {
    notification.showNotification({ 
      type: 'error', 
      text: '❌ Failed to start the export. Please try again.' 
    });
  } finally {
    isExporting.value = false;
  }
};

onMounted(fetchSummaryData);

onUnmounted(() => {
    if (monthlyBookingsChart) monthlyBookingsChart.destroy();
    if (favoriteLotsChart) favoriteLotsChart.destroy();
});

watch(summaryData, (newData) => {
    if (newData) {
        nextTick(() => {
            renderCharts();
        });
    }
});

const renderCharts = () => {
    if (monthlyBookingsChart) monthlyBookingsChart.destroy();
    if (favoriteLotsChart) favoriteLotsChart.destroy();

    const monthlyCtx = monthlyBookingsCanvas.value;
    const favoriteCtx = favoriteLotsCanvas.value;

    if (!summaryData.value) return;

    // Monthly Bookings Chart
    if (monthlyCtx && summaryData.value.monthly_bookings) {
        const labels = Object.keys(summaryData.value.monthly_bookings);
        const data = Object.values(summaryData.value.monthly_bookings);

        monthlyBookingsChart = new Chart(monthlyCtx, {
            type: 'bar',
            data: {
                labels,
                datasets: [{
                    label: 'Number of Bookings',
                    data,
                    backgroundColor: 'rgba(54, 162, 235, 0.6)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: { y: { beginAtZero: true, ticks: { stepSize: 1 } } }
            }
        });
    }

    // Favorite Lots Chart
    if (favoriteCtx && hasParkingHistory.value) {
        const labels = Object.keys(summaryData.value.favorite_lots);
        const data = Object.values(summaryData.value.favorite_lots);

        favoriteLotsChart = new Chart(favoriteCtx, {
            type: 'pie',
            data: {
                labels,
                datasets: [{
                    data,
                    backgroundColor: [
                        'rgba(255, 99, 132, 0.6)',
                        'rgba(75, 192, 192, 0.6)',
                        'rgba(255, 206, 86, 0.6)',
                        'rgba(153, 102, 255, 0.6)',
                    ],
                    borderColor: [
                        'rgba(255, 99, 132, 1)',
                        'rgba(75, 192, 192, 1)',
                        'rgba(255, 206, 86, 1)',
                        'rgba(153, 102, 255, 1)',
                    ],
                    borderWidth: 1
                }]
            },
            options: { responsive: true, maintainAspectRatio: false }
        });
    }
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
