<template>
    <div class="container-fluid mt-4">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h1>Orders</h1>
            <RouterLink to="/new-order" class="btn btn-primary" :class="{ 'disabled': !canCreateOrder }"
                :aria-disabled="!canCreateOrder">
                Create New Order
            </RouterLink>
        </div>

        <!-- Prerequisite Checks -->
        <div v-if="!canCreateOrder && !isLoading" class="alert alert-warning" role="alert">
            <h4 class="alert-heading">Prerequisites Missing!</h4>
            <p>To create a new order, you must first have at least one of each of the following resources. Please use
                the links below to create them.</p>
            <hr>
            <div class="d-flex flex-wrap gap-2">
                <template v-for="item in missingPrerequisites" :key="item.name">
                    <RouterLink :to="item.route" class="btn btn-sm btn-info">{{ item.name }}</RouterLink>
                </template>
            </div>
        </div>

        <div v-if="isLoading" class="text-center">
            <div class="spinner-border" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
        </div>

        <div v-else-if="orders.length > 0" class="row g-4">
            <div v-for="order in orders" :key="order.id" class="col-lg-6">
                <div class="card h-100 shadow-sm order-card">
                    <div class="card-header d-flex justify-content-between align-items-center"
                        :style="{ backgroundColor: order.status.name === 'Success' ? '#d3ff6e' : order.status.name === 'Failed' ? '#ff7070' : '#affbff' }">
                        <h5 class="mb-0">Order #{{ order.id }} : {{ order.name }}</h5>
                        <span :class="getStatusClass(order.status.name)"
                            :style="{ backgroundColor: order.status.name === 'Success' ? 'green' : 'red' }">{{
                            order.status.name
                            }}</span>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div>
                                <strong>Description</strong>
                                <p>{{ order.description }}</p>
                            </div>
                            <div class="col-sm-6">
                                <p><strong>Client:</strong> {{ order.client.name }}</p>
                                <p><strong>Partner:</strong> {{ order.partner.name }}</p>
                                <p><strong>Company:</strong> {{ order.company.name }}</p>
                            </div>
                            <div class="col-sm-6">
                                <p><strong>Order Type:</strong> {{ order.order_type.name }}</p>
                                <p><strong>Created:</strong> {{ formatDate(order.date_created) }}</p>
                                <p><strong>Fees:</strong> {{ order.fees?.toLocaleString('en-IN', {
                                    style: 'currency',
                                    currency: 'INR'
                                }) }}</p>
                            </div>
                        </div>
                    </div>
                    <div class="card-footer text-end">
                        <button class="btn btn-sm btn-outline-secondary me-2" @click="viewDetails(order.id)">View
                            Details</button>
                        <button v-if="order.status.name !== 'Success' && order.status.name !== 'Failed'"
                            class="btn btn-sm btn-outline-danger" @click="showDeleteModal(order)">Delete</button>
                    </div>
                </div>
            </div>
        </div>

        <div v-else class="text-center p-5 border rounded bg-light">
            <h4>No orders found.</h4>
            <p v-if="canCreateOrder">Get started by creating a new order.</p>
        </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div ref="deleteModal" class="modal fade" tabindex="-1">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Confirm Deletion</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <p>Are you sure you want to delete <strong>Order #{{ orderToDelete?.id }}</strong> for client
                        <strong>{{
                            orderToDelete?.client.name }}</strong>?</p>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                    <button type="button" class="btn btn-danger" @click="confirmDelete">Delete</button>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted, computed, reactive } from 'vue';
import { useRouter } from 'vue-router';
import {fetchApi} from '../../utils/api';
import { useAlertStore } from '@/stores/alertMessageStore';
import { Modal } from 'bootstrap';

const router = useRouter();
const alert = useAlertStore();

const orders = ref([]);
const isLoading = ref(true);
const deleteModal = ref(null);
const bsDeleteModal = ref(null);
const orderToDelete = ref(null);

const prerequisites = reactive({
    clients: [], partners: [], companies: [],
    registrars: [], orderTypes: [], orderStatuses: []
});

const getPrerequisites = async () => {
    const endpoints = {
        clients: '/api/clients', partners: '/api/partners', companies: '/api/companies',
        registrars: '/api/registrars', orderTypes: '/api/order-types', orderStatuses: '/api/order-status'
    };
    const requests = Object.entries(endpoints).map(async ([key, endpoint]) => {
        try {
            const response = await fetchApi(endpoint);
            if (response.ok) {
                prerequisites[key] = await response.json();
            } else {
                prerequisites[key] = []; // Ensure it's an empty array on failure
            }
        } catch {
            prerequisites[key] = [];
        }
    });
    await Promise.all(requests);
};

const canCreateOrder = computed(() => {
    return prerequisites.clients.length > 0 &&
        prerequisites.partners.length > 0 &&
        prerequisites.companies.length > 0 &&
        prerequisites.registrars.length > 0 &&
        prerequisites.orderTypes.length > 0 &&
        prerequisites.orderStatuses.length > 0;
});

const missingPrerequisites = computed(() => {
    const missing = [];
    if (prerequisites.clients.length === 0) missing.push({ name: 'Create Client', route: '/new-client' });
    if (prerequisites.partners.length === 0) missing.push({ name: 'Create Partner', route: '/new-partner' });
    if (prerequisites.registrars.length === 0) missing.push({ name: 'Create Registrar', route: '/registrars' });
    if (prerequisites.companies.length === 0) missing.push({ name: 'Create Company', route: '/companies' });
    if (prerequisites.orderTypes.length === 0) missing.push({ name: 'Create Order Type', route: '/order-types' });
    if (prerequisites.orderStatuses.length === 0) missing.push({ name: 'Create Order Status', route: '/order-status' });
    return missing;
});


const getOrders = async () => {
    try {
        const response = await fetchApi('/api/orders');
        if (response.ok) {
            orders.value = await response.json();
        } else {
            const data = await response.json();
            if (response.status !== 404) { // 404 is "no orders", not an error
                alert.show(data.message || 'Failed to fetch orders.', 'warning');
            }
            orders.value = [];
        }
    } catch (error) {
        console.error('Error fetching orders:', error);
        alert.show('An unexpected error occurred while fetching orders.', 'danger');
    }
};



onMounted(async () => {
    isLoading.value = true;
    await Promise.all([getPrerequisites(), getOrders()]);
    isLoading.value = false;
    if (deleteModal.value) {
        bsDeleteModal.value = new Modal(deleteModal.value);
    }
});

const formatDate = (dateString) => new Date(dateString).toLocaleDateString();

const getStatusClass = (statusName) => {
    const baseClass = 'badge';
    switch (statusName.toLowerCase()) {
        case 'received': return `${baseClass} bg-info`;
        case 'confirmed': return `${baseClass} bg-primary`;
        case 'in-progress': return `${baseClass} bg-info`;
        case 'success': return `${baseClass} bg-success`;
        case 'failed': return `${baseClass} bg-danger`;
        default: return `${baseClass} bg-primary`;
    }
};

const viewDetails = (orderId) => router.push({ name: 'order-details', params: { id: orderId } });

const showDeleteModal = (order) => {
    orderToDelete.value = order;
    bsDeleteModal.value?.show();
};

const confirmDelete = async () => {
    if (!orderToDelete.value) return;
    try {
        const response = await fetchApi(`/api/orders/${orderToDelete.value.id}`, { method: 'DELETE' });
        if (response.ok) {
            alert.show(`Order #${orderToDelete.value.id} deleted successfully.`, 'success');
            await getOrders();
        } else {
            alert.show((await response.json()).message || 'Failed to delete order.', 'danger');
        }
    } catch (error) {
        alert.show('An unexpected error occurred.', 'danger');
    } finally {
        bsDeleteModal.value?.hide();
    }
};

</script>

<style scoped>
.order-card .card-header {
    background-color: #f8f9fa;
}

.order-card p {
    margin-bottom: 0.5rem;
}

.card-footer {
    background-color: transparent;
    border-top: none;
    padding-top: 0;
}

.gap-2 {
    gap: 0.5rem;
}

.disabled {
    pointer-events: none;
    opacity: 0.65;
}
</style>