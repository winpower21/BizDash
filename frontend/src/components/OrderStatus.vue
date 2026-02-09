<template>
    <h1>Order Status</h1>
    <hr>
    <div v-if="orderStatus.length > 0" class="container hero-content">
    <table class="table table-striped-columns">
        <thead class="table-dark">
            <tr>
                <th scope="col">#</th>
                <th scope="col">Name</th>
                <th scope="col">Description</th>
                <th scope="col">Action</th>
            </tr>
        </thead>
        <tbody>
            <tr v-for="status in orderStatus" :key="status.id">
                <th scope="row">{{ status.id }}</th>
                <td>{{ status.name }}</td>
                <td>{{ status.description }}</td>
                <td>
                    <div>
                        <button class="btn btn-warning" @click="showEditOrderStatusModal(status)">Edit</button>
                        <button class="btn btn-danger" @click="showDeleteOrderStatusModal(status)">Delete</button>
                    </div>
                </td>
            </tr>
        </tbody>
    </table>
    <button class="btn btn-primary" @click="showNewOrderStatusModal">Create New</button>
    </div>
    <div v-else class="alert alert-info" role="alert">
        <p>There are no order status types. Create a new one.</p>
        <hr>
        <button class="btn btn-primary" @click="showNewOrderStatusModal">Create New</button>
    </div>

    <div ref="deleteOrderStatusModal" class="modal fade" tabindex="-1">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Delete Order</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <div class="mb-3 align-items-center">
                        <h5>Delete status type: {{ deleteOrderStatusName }}</h5>
                    </div>
                </div>
                <div class="modal-footer">
                    <button @click="deleteStatusType(deleteOrderStatusId)" class="btn btn-danger">Delete</button>
                </div>
            </div>
        </div>
    </div>

    <div ref="editOrderStatusModal" class="modal fade" tabindex="-1">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Edit Status Type</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <div class="mb-3">
                        <label for="orderStatusName" class="form-label">Name</label>
                        <input type="text" v-model="editingOrderStatus.name" name="orderStatusName" id="orderStatusName"
                            class="form-control" placeholder="Order Status Name">
                    </div>
                    <div class="mb-3">
                        <label for="orderStatusDescription" class="form-label">Description</label>
                        <input type="text" v-model="editingOrderStatus.description" name="orderStatusDescription"
                            id="orderStatusDescription" class="form-control" placeholder="Order Status Description">
                    </div>
                </div>
                <div class="modal-footer">
                    <button @click="editOrderStatus(editingOrderStatus)" class="btn btn-success">Submit</button>
                </div>
            </div>
        </div>
    </div>

    <div ref="newOrderStatusModal" class="modal fade" tabindex="-1">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Create Order Status</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <div class="mb-3">
                        <label for="orderStatusName" class="form-label">Name</label>
                        <input type="text" v-model="newOrderStatusName" name="orderStatusName" id="orderStatusName" class="form-control" placeholder="Order Status Name">
                    </div>
                    <div class="mb-3">
                        <label for="orderStatusDescription" class="form-label">Description</label>
                        <input type="text" v-model="newOrderStatusDescription" name="orderStatusDescription" id="orderStatusDescription"
                            class="form-control" placeholder="Order Status Description">
                    </div>
                </div>
                <div class="modal-footer">
                    <button @click="createOrderStatus" class="btn btn-success">Submit</button>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { nextTick, ref } from 'vue';
import { onMounted } from 'vue';
import {fetchApi} from '../../utils/api';
import { useAlertStore } from '@/stores/alertMessageStore';
import { Modal } from 'bootstrap';
import { useRouter } from 'vue-router';

const router = useRouter()
const alert = useAlertStore();


const newOrderStatusName = ref("");
const newOrderStatusDescription = ref("");
const newOrderStatusModal = ref(null);
const newOrderStatus = ref(null);

const editOrderStatusModal = ref(null);
const newOrderS = ref(null);
const editingOrderStatus = ref({});

const deleteOrderStatusModal = ref(null);
const deleteOrderStatusName = ref('');
const deleteOrderStatusId = ref('');
const deleteOrderS = ref(null);

const orderStatus = ref([]);


//  Fetch order status
const getOrderStatus = async() => {
    try{
        const response = await fetchApi('/api/order-status', {
            method: "GET"
        })
        if (response.ok){
            const data = await response.json()
            orderStatus.value = data
        }
    } catch (e) {
        console.error("Error fetching data: ", e)
    }
}


//  Delete docuement types
const deleteStatusType = async(status_id) => {
    try{
        const response = await fetchApi(`/api/order-status/${status_id}`, {
            method: "DELETE"
        });
        if (response.ok) {
            deleteOrderS.value.hide();
            alert.show("Deleted Successfully", "success")
            await getOrderStatus()
        }
    } catch (e) {
        console.error(e)
    }
}


//  Create docuement types
const createOrderStatus = async() => {
    try {
        const response = await fetchApi('/api/order-status', {
            method: "POST",
            body: JSON.stringify({
                "name": newOrderStatusName.value,
                "description": newOrderStatusDescription.value,
            })
        })
        if (response.ok) {
            newOrderStatus.value.hide()
            alert.show(`Order ${newOrderStatusName.value} created successfully`)
            await getOrderStatus()
        } else {
            newOrderStatus.value.hide()
            const data = await response.json();
            alert.show(`Error creating ${newOrderStatusName.value}: ${data.message}`)
        }
    } catch (e) {
        console.error(e)
    }
}

//  Edit docuement types
const editOrderStatus = async (order) => {
    try {
        const response = await fetchApi(`/api/order-status/${order.id}`, {
            method: "PUT",
            body: JSON.stringify({
                "name": order.name,
                "description": order.description,
            })
        })
        if (response.ok) {
            newOrderS.value.hide()
            alert.show(`Order ${order.name} edited successfully`)
            await getOrderStatus()
        } else {
            newOrderS.value.hide()
            const data = await response.json();
            alert.show(`Error editing ${order.name}: ${data.message}`)
        }
    } catch (e) {
        console.error(e)
    }
}

const showDeleteOrderStatusModal = (order) => {
    deleteOrderStatusName.value = order.name;
    deleteOrderStatusId.value = order.id;
    if (!deleteOrderS.value && deleteOrderStatusModal.value) {
        deleteOrderS.value = new Modal(deleteOrderStatusModal.value);
    }
    deleteOrderS.value?.show();
};


const showNewOrderStatusModal = () => {
    if (!newOrderStatus.value && newOrderStatusModal.value) {
        newOrderStatus.value = new Modal(newOrderStatusModal.value);
    }
    newOrderStatus.value?.show();
};

const showEditOrderStatusModal = (status) => {
    editingOrderStatus.value = JSON.parse(JSON.stringify(status))

    if (!newOrderS.value && editOrderStatusModal.value) {
        newOrderS.value = new Modal(editOrderStatusModal.value);
    }
    newOrderS.value?.show();
};


onMounted(async () => {
    getOrderStatus();
    await nextTick();
    if (deleteOrderStatusModal.value) {
        deleteOrderS.value = new Modal(deleteOrderStatusModal.value)
    }
    if (newOrderStatusModal.value) {
        newOrderStatus.value = new Modal(newOrderStatusModal.value)
    }
    if (editOrderStatusModal.value) {
        newOrderS.value = new Modal(editOrderStatusModal.value)
    }
})


</script>

<style scoped>
.btn {
    margin-right: 5px;
}

thead th {
    text-align: center;
}

tbody tr {
    text-align: center;
}

tbody td .content{
    text-align: center;
}

.btn {
    min-width: 100px;
}
</style>