<template>
    <div class="container mt-4">
        <div class="card shadow-sm">
            <div class="card-header">
                <h1 class="card-title">Create New Order</h1>
            </div>
            <div class="card-body">
                <form @submit.prevent="createOrder">
                    <div class="row">
                        <!-- Left Column -->
                        <div class="col-md-6">
                            <div class="mb-3">
                                <label for="name" class="form-label">Name</label>
                                <input type="text" class="form-control" id="name"
                                    v-model="formData.name" placeholder="Name">
                            </div>

                            <div class="mb-3">
                                <label for="partner" class="form-label">Partner</label>
                                <select class="form-select" id="partner" v-model="formData.partner_id" required>
                                    <option :value="null" disabled>Select a Partner</option>
                                    <option v-for="partner in lists.partners" :key="partner.id" :value="partner.id">
                                        {{ partner.name }}
                                    </option>
                                </select>
                            </div>
                            <div class="mb-3">
                                <label for="client" class="form-label">Client</label>
                                <select class="form-select" id="client" v-model="formData.client_id" required>
                                    <option :value="null" disabled>Select a Client</option>
                                    <option v-for="client in lists.clients" :key="client.id" :value="client.id">
                                        {{ client.name }}
                                    </option>
                                </select>
                            </div>

                            <div class="mb-3">
                                <label for="orderType" class="form-label">Order Type</label>
                                <select class="form-select" id="orderType" v-model="formData.order_type_id" required>
                                    <option :value="null" disabled>Select an Order Type</option>
                                    <option v-for="orderType in lists.orderTypes" :key="orderType.id" :value="orderType.id">
                                        {{ orderType.name }}
                                    </option>
                                </select>
                            </div>

                            <div class="mb-3">
                                <label for="company" class="form-label">Company</label>
                                <select class="form-select" id="company" v-model="formData.company_id" required>
                                    <option :value="null" disabled>Select a Company</option>
                                    <option v-for="company in lists.companies" :key="company.id" :value="company.id">
                                        {{ company.name }}
                                    </option>
                                </select>
                            </div>

                            <div class="mb-3">
                                <label for="status" class="form-label">Initial Status</label>
                                <select class="form-select" id="status" v-model="formData.status_id" required>
                                    <option :value="null" disabled>Select Initial Status</option>
                                    <option v-for="status in lists.orderStatuses" :key="status.id" :value="status.id">
                                        {{ status.name }}
                                    </option>
                                </select>
                            </div>
                        </div>

                        <!-- Right Column -->
                        <div class="col-md-6">
                            <div class="mb-3">
                                <label for="description" class="form-label">Description</label>
                                <input type="text" class="form-control" id="description" v-model="formData.description"
                                    placeholder="Description">
                            </div>

                            <div class="mb-3">
                                <label for="fees" class="form-label">Fees</label>
                                <input type="number" step="0.01" class="form-control" id="fees" v-model.number="formData.fees" placeholder="Enter fees">
                            </div>

                            <div class="mb-3">
                                <label for="baseCharges" class="form-label">Base Charges</label>
                                <input type="number" step="0.01" class="form-control" id="baseCharges" v-model.number="formData.base_charges" placeholder="Enter base charges">
                            </div>
                            <hr>
                             <div class="mb-3">
                                <label for="shareCount" class="form-label">Share Count</label>
                                <input type="number" class="form-control" id="shareCount" v-model.number="formData.share_count" placeholder="Enter share count">
                            </div>

                            <div class="mb-3">
                                <label for="sharePrice" class="form-label">Share Price</label>
                                <input type="number" step="0.01" class="form-control" id="sharePrice" v-model.number="formData.share_price" placeholder="Enter share price">
                            </div>
                        </div>
                    </div>

                    <div class="mt-3 text-end">
                        <button type="button" class="btn btn-secondary me-2" @click="goBack">Cancel</button>
                        <button type="submit" class="btn btn-primary">Create Order</button>
                    </div>
                </form>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue';
import { useRouter } from 'vue-router';
import {fetchApi} from '../../utils/api';
import { useAlertStore } from '@/stores/alertMessageStore';

const router = useRouter();
const alert = useAlertStore();

// Reactive object to hold all form data
const formData = reactive({
    name: null,
    description: null,
    client_id: null,
    partner_id: null,
    order_type_id: null,
    company_id: null,
    status_id: null,
    share_count: null,
    share_price: null,
    fees: 0.0,
    base_charges: 0.0,
});

// Reactive object to hold lists for dropdowns
const lists = reactive({
    clients: [],
    partners: [],
    orderTypes: [],
    companies: [],
    orderStatuses: [],
});

// Generic fetch function for populating dropdowns
const fetchDataForList = async (endpoint, listName) => {
    try {
        const response = await fetchApi(endpoint);
        if (response.ok) {
            lists[listName] = await response.json();
        } else {
            console.error(`Failed to fetch ${listName}`);
        }
    } catch (error) {
        console.error(`Error fetching ${listName}:`, error);
    }
};

// Fetch all necessary data when the component mounts
onMounted(() => {
    fetchDataForList('/api/clients', 'clients');
    fetchDataForList('/api/partners', 'partners');
    fetchDataForList('/api/order-types', 'orderTypes');
    fetchDataForList('/api/companies', 'companies');
    fetchDataForList('/api/order-status', 'orderStatuses');
});

// Function to handle form submission
const createOrder = async () => {
    try {
        // Filter out null values for optional fields before sending
        const payload = { ...formData };
        if (payload.share_count === null || payload.share_count === '') delete payload.share_count;
        if (payload.share_price === null || payload.share_price === '') delete payload.share_price;

        const response = await fetchApi('/api/orders', {
            method: 'POST',
            body: JSON.stringify(payload),
        });

        const data = await response.json();

        if (response.ok) {
            alert.show('Order created successfully!', 'success');
            router.push('/orders'); // Redirect to orders list or order detail page
        } else {
            alert.show(`Error: ${data.message || 'Failed to create order.'}`, 'danger');
        }
    } catch (error) {
        console.error('Submission error:', error);
        alert.show('An unexpected error occurred.', 'danger');
    }
};

const goBack = () => {
    router.back();
};
</script>

<style scoped>
.card {
    /* max-width: 900px; */
    margin: auto;
}
.card-header {
    background-color: #f8f9fa;
}
</style>
