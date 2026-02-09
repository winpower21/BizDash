<template>
    <div class="container-fluid mt-4">
        <TaskSidebar :tasks="tasks" :show-order-name="true" @toggle-completion="toggleTaskCompletion" :show-grouping="true" />
        <div v-if="isLoading" class="d-flex justify-content-center align-items-center" style="min-height: 80vh;">
            <div class="spinner-border" style="width: 3rem; height: 3rem;" role="status">
                <span class="visually-hidden">Loading Dashboard...</span>
            </div>
        </div>

        <div v-else>
            <!-- Header -->
            <div class="d-flex justify-content-between align-items-center mb-4">
                <h1>Dashboard</h1>
                <RouterLink to="/orders" class="btn btn-primary">View All Orders</RouterLink>
            </div>

            <!-- Revenue Metrics -->
            <div class="row g-4 mb-4">
                <div class="col-md-4">
                    <div class="card text-center shadow-sm h-100">
                        <div class="card-body">
                            <h5 class="card-title text-muted">Realized Revenue (30 Days)</h5>
                            <p class="card-text fs-2 fw-bold text-success">{{
                                revenueSummary.realized_revenue_30_days?.toLocaleString('en-IN', {
                                    style: 'currency',
                                    currency: 'INR'
                                }) || '0.00' }}</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card text-center shadow-sm h-100">
                        <div class="card-body">
                            <h5 class="card-title text-muted">Realized Revenue (90 Days)</h5>
                            <p class="card-text fs-2 fw-bold text-primary">{{
                                revenueSummary.realized_revenue_90_days?.toLocaleString('en-IN', {
                                    style: 'currency',
                                    currency: 'INR'
                                }) || '0.00' }}</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card text-center shadow-sm h-100">
                        <div class="card-body">
                            <h5 class="card-title text-muted">Unrealized Revenue</h5>
                            <p class="card-text fs-2 fw-bold text-warning">{{
                                revenueSummary.unrealized_revenue?.toLocaleString('en-IN', {
                                    style: 'currency',
                                    currency: 'INR'
                                }) || '0.00' }}
                            </p>
                        </div>
                    </div>
                </div>
            </div>

            <div class="row g-4">
                <!-- Most Recent Order -->
                <div class="col-lg-7">
                    <div class="card shadow-sm h-100">
                        <div class="card-header bg-light">
                            <h5 class="mb-0">Most Recent Order</h5>
                        </div>
                        <div v-if="recentOrder" class="card-body">
                            <h4 class="card-title">Order #{{ recentOrder.id }} - {{ recentOrder.company.name }}</h4>
                            <div class="d-flex justify-content-between align-items-center mb-3">
                                <span :class="getStatusClass(recentOrder.status.name)">{{ recentOrder.status.name}}</span>
                                <small class="text-muted">{{ formatDate(recentOrder.date_created) }}</small>
                            </div>
                            <p><strong>Client:</strong> {{ recentOrder.client.name }}</p>
                            <p><strong>Partner:</strong> {{ recentOrder.partner.name }}</p>
                            <RouterLink :to="`/orders/${recentOrder.id}`" class="btn btn-outline-primary mt-2">View Details</RouterLink>
                        </div>
                        <div v-else class="card-body text-center text-muted">
                            <p>No orders found.</p>
                        </div>
                    </div>
                </div>

                <!-- Activity Timeline -->
                <div class="col-lg-5">
                    <div class="card shadow-sm h-100">
                        <div class="card-header bg-light">
                            <h5 class="mb-0">Activity Timeline</h5>
                        </div>
                        <ul class="list-group list-group-flush">
                            <li v-for="event in activityTimeline" :key="event.id" class="list-group-item">
                                <p class="mb-0">
                                    <strong>Order #{{ event.order_id }}</strong> moved to status <strong>{{
                                        event.status.name }}</strong>
                                </p>
                                <small class="text-muted">{{ formatRelativeTime(event.changed_at) }}</small>
                            </li>
                            <li v-if="!activityTimeline.length" class="list-group-item text-muted text-center">
                                <p class="mb-0">No recent activity.</p>
                            </li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import {fetchApi} from '../../utils/api';
import { useAlertStore } from '@/stores/alertMessageStore';
import TaskSidebar from '@/components/TaskSidebar.vue';

const alert = useAlertStore();
const isLoading = ref(true);

const recentOrder = ref(null);
const revenueSummary = ref({});
const activityTimeline = ref([]);
const tasks = ref([]);

// --- DATA FETCHING ---
const fetchDashboardData = async () => {
    try {
        const [ordersRes, revenueRes, timelineRes] = await Promise.all([
            fetchApi('/api/orders'),
            fetchApi('/api/dashboard/revenue-summary'),
            fetchApi('/api/dashboard/activity-timeline')
        ]);

        // Most Recent Order (from the sorted /api/orders endpoint)
        if (ordersRes.ok) {
            const allOrders = await ordersRes.json();
            if (allOrders.length > 0) {
                recentOrder.value = allOrders[0];
            }
        }

        // Revenue Summary
        if (revenueRes.ok) {
            revenueSummary.value = await revenueRes.json();
        }

        // Activity Timeline
        if (timelineRes.ok) {
            activityTimeline.value = await timelineRes.json();
        }

    } catch (e) {
        alert.show('Failed to load dashboard data. Please try again later.', 'danger');
        console.error(e);
    } finally {
        isLoading.value = false;
    }
};

const fetchAllTasks = async () => {
    try {
        const response = await fetchApi('/api/tasks');
        if (!response.ok) throw new Error('Failed to fetch tasks.');
        tasks.value = await response.json();
    } catch (e) {
        alert.show(e.message, 'warning');
    }
};

const toggleTaskCompletion = async (task) => {
    try {
        const response = await fetchApi(`/api/tasks/${task.id}`, {
            method: 'PUT',
            body: JSON.stringify({ is_completed: !task.is_completed })
        });
        if (!response.ok) throw new Error((await response.json()).message);
        await fetchAllTasks(); // Refresh task list
    } catch (e) {
        alert.show(e.message, 'danger');
    }
};


onMounted(() => {
    fetchDashboardData();
    fetchAllTasks();
});

// --- UI HELPERS ---
const formatDate = (dateString) => new Date(dateString).toLocaleDateString();

const getStatusClass = (statusName) => {
    const baseClass = 'badge';
    switch (statusName?.toLowerCase()) {
        case 'completed': case 'success': return `${baseClass} bg-success`;
        case 'in progress': return `${baseClass} bg-primary`;
        case 'pending': return `${baseClass} bg-secondary`;
        case 'received': return `${baseClass} bg-info`;
        case 'failed': return `${baseClass} bg-danger`;
        default: return `${baseClass} bg-dark`;
    }
};

const formatRelativeTime = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const seconds = Math.round((now - date) / 1000);
    const minutes = Math.round(seconds / 60);
    const hours = Math.round(minutes / 60);
    const days = Math.round(hours / 24);

    if (seconds < 60) return 'just now';
    if (minutes < 60) return `${minutes} minutes ago`;
    if (hours < 24) return `${hours} hours ago`;
    return `${days} days ago`;
};

</script>