<template>
    <div class="container-fluid mt-4">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h1 class="h3">Financial & Operational Reports</h1>
            <div class="col-md-2">
                <select class="form-select" v-model="selectedYear" @change="fetchReportData">
                    <option v-for="year in availableYears" :key="year" :value="year">{{ year }}</option>
                </select>
            </div>
        </div>

        <div v-if="isLoading" class="text-center mt-5">
            <div class="spinner-border" style="width: 3rem; height: 3rem;" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
            <p class="mt-2">Generating Reports...</p>
        </div>

        <div v-else-if="stats" class="reports-container">
            <!-- Revenue Metrics -->
            <div class="row g-4">
                <div v-if="stats.is_current_year" class="col-md-4">
                    <div class="card h-100 shadow-sm">
                        <div class="card-header">Realized Revenue (Current Month)</div>
                        <div class="card-body">
                            <h5 class="card-title">{{ formatCurrency(stats.realized_revenue.month.total) }}</h5>
                            <p class="card-text">
                                <span class="text-success">Self: {{ formatCurrency(stats.realized_revenue.month.self_share) }}</span> | 
                                <span class="text-primary">Partners: {{ formatCurrency(stats.realized_revenue.month.partner_share) }}</span>
                            </p>
                        </div>
                    </div>
                </div>
                <div v-if="stats.is_current_year" class="col-md-4">
                    <div class="card h-100 shadow-sm">
                        <div class="card-header">Realized Revenue (Current Quarter)</div>
                        <div class="card-body">
                            <h5 class="card-title">{{ formatCurrency(stats.realized_revenue.quarter.total) }}</h5>
                            <p class="card-text">
                                <span class="text-success">Self: {{ formatCurrency(stats.realized_revenue.quarter.self_share) }}</span> | 
                                <span class="text-primary">Partners: {{ formatCurrency(stats.realized_revenue.quarter.partner_share) }}</span>
                            </p>
                        </div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card h-100 shadow-sm">
                        <div class="card-header">Realized Revenue ({{ stats.selected_year }})</div>
                        <div class="card-body">
                            <h5 class="card-title">{{ formatCurrency(stats.realized_revenue.year.total) }}</h5>
                            <p class="card-text">
                                <span class="text-success">Self: {{ formatCurrency(stats.realized_revenue.year.self_share) }}</span> | 
                                <span class="text-primary">Partners: {{ formatCurrency(stats.realized_revenue.year.partner_share) }}</span>
                            </p>
                        </div>
                    </div>
                </div>
            </div>

            <div class="row g-4 mt-1">
                 <div class="col-md-4">
                    <div class="card h-100 shadow-sm">
                        <div class="card-header">Unrealized Revenue ({{ stats.selected_year }})</div>
                        <div class="card-body">
                            <h5 class="card-title">{{ formatCurrency(stats.unrealized_revenue_year) }}</h5>
                        </div>
                    </div>
                </div>
                 <div class="col-md-4">
                    <div class="card h-100 shadow-sm">
                        <div class="card-header">Total Revenue ({{ stats.selected_year }})</div>
                        <div class="card-body">
                            <h5 class="card-title">{{ formatCurrency(stats.total_revenue_year) }}</h5>
                            <p class="card-text">
                                <span class="text-success">Realized: {{ formatCurrency(stats.realized_revenue.year.total) }}</span> | 
                                <span class="text-warning">Unrealized: {{ formatCurrency(stats.unrealized_revenue_year) }}</span>
                            </p>
                        </div>
                    </div>
                </div>
                 <div class="col-md-4">
                    <div class="card h-100 shadow-sm">
                        <div class="card-header">Avg. Order Completion</div>
                        <div class="card-body">
                            <h5 class="card-title">{{ formatDuration(stats.average_order_completion_duration_seconds) }}</h5>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="row g-4 mt-1">
                <div class="col-md-6">
                    <div class="card h-100 shadow-sm">
                        <div class="card-header">Average Order Value ({{ stats.selected_year }})</div>
                        <div class="card-body">
                            <h5 class="card-title">Fees: {{ formatCurrency(stats.average_order_value.fees) }}</h5>
                            <p class="card-text">
                                Order Value: {{ formatCurrency(stats.average_order_value.order_value) }}
                            </p>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Partner Revenue Share -->
            <div class="card mt-4 shadow-sm">
                <div class="card-header">
                    <h5 class="mb-0">Revenue Share by Partner ({{ stats.selected_year }})</h5>
                </div>
                <div class="table-responsive">
                    <table class="table table-striped mb-0">
                        <thead>
                            <tr>
                                <th>Partner</th>
                                <th class="text-end">Total Share</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="partner in stats.partner_revenue_share" :key="partner.partner_id">
                                <td>{{ partner.partner_name }}</td>
                                <td class="text-end">{{ formatCurrency(partner.total_share) }}</td>
                            </tr>
                             <tr v-if="!stats.partner_revenue_share.length">
                                <td colspan="2" class="text-center text-muted">No partner revenue for this year.</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        <div v-else class="text-center mt-5">
            <p>Could not load report data.</p>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import {fetchApi} from '../../utils/api';
import { useAlertStore } from '@/stores/alertMessageStore';

const alert = useAlertStore();
const isLoading = ref(true);
const stats = ref(null);

const currentYear = new Date().getFullYear();
const selectedYear = ref(currentYear);
const availableYears = computed(() => {
    const years = [];
    for (let year = currentYear; year >= 2020; year--) {
        years.push(year);
    }
    return years;
});

const fetchReportData = async () => {
    isLoading.value = true;
    stats.value = null;
    try {
        const response = await fetchApi(`/api/reports/revenue-stats?year=${selectedYear.value}`);
        if (!response.ok) throw new Error('Failed to fetch report data.');
        stats.value = await response.json();
    } catch (e) {
        alert.show(e.message, 'danger');
    } finally {
        isLoading.value = false;
    }
};

onMounted(() => {
    fetchReportData();
});

const formatCurrency = (value) => {
    if (value === null || value === undefined) return '₹ 0.00';
    return value.toLocaleString('en-IN', {
        style: 'currency',
        currency: 'INR',
        maximumFractionDigits: 2
    });
};

const formatDuration = (totalSeconds) => {
    if (totalSeconds === null || totalSeconds === undefined) return 'N/A';
    
    const days = Math.floor(totalSeconds / 86400);
    const hours = Math.floor((totalSeconds % 86400) / 3600);
    const minutes = Math.floor(((totalSeconds % 86400) % 3600) / 60);

    let result = '';
    if (days > 0) result += `${days}d `;
    if (hours > 0) result += `${hours}h `;
    if (minutes > 0) result += `${minutes}m`;
    
    return result.trim() || '0m';
};

</script>

<style scoped>
.card-header {
    background-color: #f8f9fa;
    font-weight: 500;
}
.card-title {
    font-size: 1.75rem;
    font-weight: 700;
}
</style>
