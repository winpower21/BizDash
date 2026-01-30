<template>
    <h1>Order Types</h1>
    <hr>
    <div v-if="orderTypes.length > 0 & documentTypes.length > 0" class="container hero-content">
    <table class="table table-striped-columns">
        <thead>
            <tr>
                <th scope="col">#</th>
                <th scope="col">Name</th>
                <th scope="col">Description</th>
                <th scope="col">Requried Docs</th>
                <th scope="col">Action</th>
            </tr>
        </thead>
        <tbody>
            <tr v-for="order in orderTypes" :key="order.id">
                <th scope="row">{{ order.id }}</th>
                <td>{{ order.name }}</td>
                <td>{{ order.description }}</td>
                <td>{{ order.required_documents.length }}</td>
                <td>
                    <div>
                        <button class="btn btn-warning" @click="showEditOrderTypeModal(order)">Edit</button>
                        <button class="btn btn-danger" @click="showDeleteOrderTypeModal(order)">Delete</button>
                    </div>
                </td>
            </tr>
        </tbody>
    </table>
    <button class="btn btn-primary" @click="showNewOrderTypeModal">Create New</button>
    </div>
    <div v-else-if="orderTypes.length == 0 & documentTypes.length > 0" class="container text-center d-flex flex-column justify-content-center  align-items-center"
        style="min-height: 80vh;">
        There are no order types. Create a new one.
        <button class="btn btn-primary" @click="showNewOrderTypeModal">Create New</button>
    </div>
    <div v-else-if="orderTypes.length == 0 & documentTypes.length == 0"
        class="container text-center d-flex flex-column justify-content-center  align-items-center"
        style="min-height: 80vh;">
        There are no document types. Create them before creating order types.
        <RouterLink class="btn btn-primary" to="/document-types">Create Document Types</RouterLink>
        <!-- <button class="btn btn-primary" @click="showNewOrderTypeModal">Create New</button> -->
    </div>
    

    <div ref="deleteOrderTypeModal" class="modal fade" tabindex="-1">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Delete Order</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <div class="mb-3 align-items-center">
                        <h5>Delete order type: {{ deleteOrderTypeName }}</h5>
                    </div>
                </div>
                <div class="modal-footer">
                    <button @click="deleteOrderType(editOrderTypeId)" class="btn btn-danger">Delete</button>
                </div>
            </div>
        </div>
    </div>

    <div ref="editOrderTypeModal" class="modal fade" tabindex="-1">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Edit Order Type</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <h3>Edit Order Type</h3>
                    <div class="mb-3">
                        <label for="orderTypeName" class="form-label">Name</label>
                        <input type="text" v-model="editingOrderType.name" name="orderTypeName" id="orderTypeName"
                            class="form-control" placeholder="Order Type Name">
                    </div>
                    <div class="mb-3">
                        <label for="orderTypeDescription" class="form-label">Description</label>
                        <input type="text" v-model="editingOrderType.description" name="orderTypeDescription"
                            id="orderTypeDescription" class="form-control" placeholder="Order Type Description">
                    </div>
                    <div class="mb-3">
                        <label for="requiredDocuements" class="form-label">Required Documents</label>
                        <div class="form-check" v-for="docType in documentTypes" :key="docType.id">
                            <input class="form-check-input" type="checkbox" :value="docType.id"
                                :id="`docType-${docType.id}`" v-model="editingOrderType.required_documents_ids">
                            <label class="form-check-label" :for="`docType-${docType.id}`">
                                {{ docType.name }}
                            </label>
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button @click="editOrderType(editingOrderType)" class="btn btn-success">Submit</button>
                </div>
            </div>
        </div>
    </div>

    <div ref="newOrderTypeModal" class="modal fade" tabindex="-1">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Create Order Type</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <h3>New Order Type</h3>
                    <div class="mb-3">
                        <label for="orderTypeName" class="form-label">Name</label>
                        <input type="text" v-model="newOrderTypeName" name="orderTypeName" id="orderTypeName" class="form-control" placeholder="Order Type Name">
                    </div>
                    <div class="mb-3">
                        <label for="orderTypeDescription" class="form-label">Description</label>
                        <input type="text" v-model="newOrderTypeDescription" name="orderTypeDescription" id="orderTypeDescription"
                            class="form-control" placeholder="Order Type Description">
                    </div>
                    <div class="mb-3">
                        <label for="requiredDocuements" class="form-label">Required Documents</label>
                        <div class="form-check" v-for="docType in documentTypes" :key="docType.id">
                            <input class="form-check-input" type="checkbox" :value="docType.id" :id="`docType-${docType.id}`" v-model="newOrderTypeReqDocs">
                            <label class="form-check-label" :for="`docType-${docType.id}`">
                                {{ docType.name }}
                            </label>
                        </div>
                    </div>
                    <RouterLink class="btn btn-primary" to="/document-types">Add More Doc Types</RouterLink>
                </div>
                <div class="modal-footer">
                    <button @click="createOrderType" class="btn btn-success">Submit</button>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { nextTick, ref } from 'vue';
import { onMounted } from 'vue';
import fetchApi from '../../utils/api';
import { useAlertStore } from '@/stores/alertMessageStore';
import { Modal } from 'bootstrap';
import { useRouter } from 'vue-router';

const router = useRouter()
const alert = useAlertStore();


const newOrderTypeName = ref("");
const newOrderTypeDescription = ref("");
const newOrderTypeReqDocs = ref([]);
const newOrderTypeModal = ref(null);
const newOrderType = ref(null);

const editOrderTypeModal = ref(null);
const editOrderT = ref(null);
const editingOrderType = ref({});

const deleteOrderTypeModal = ref(null);
const deleteOrderTypeName = ref('');
const editOrderTypeId = ref('');
const deleteOrderT = ref(null);

const orderTypes = ref([]);
const documentTypes = ref([])


const getDocumentTypes = async() => {
    try{
        const response = await fetchApi('/api/document-types', {
            method: 'GET'
        });
        if (response.ok) {
            const data = await response.json();
            documentTypes.value = data;
        } else {
            const data = await response.json();
            console.warn(data)
        }
    } catch (e) {
        console.error(e)
    }
}


//  Fetch docuement types
const getOrderTypes = async() => {
    try{
        const response = await fetchApi('/api/order-types', {
            method: "GET"
        })
        if (response.ok){
            const data = await response.json()
            console.log(data);
            orderTypes.value = data
        }
    } catch (e) {
        console.error("Error fetching data: ", e)
    }
}


//  Delete docuement types
const deleteOrderType = async(document_id) => {
    try{
        const response = await fetchApi(`/api/order-types/${document_id}`, {
            method: "DELETE"
        });
        if (response.ok) {
            deleteOrderT.value.hide();
            alert.show("Deleted Successfully", "success")
            await getOrderTypes()
        }
    } catch (e) {
        console.error(e)
    }
}


//  Create docuement types
const createOrderType = async() => {
    try {
        const response = await fetchApi('/api/order-types', {
            method: "POST",
            body: JSON.stringify({
                "name": newOrderTypeName.value,
                "description": newOrderTypeDescription.value,
                "required_documents_ids": newOrderTypeReqDocs.value
            })
        })
        if (response.ok) {
            newOrderType.value.hide()
            alert.show(`Order ${newOrderTypeName.value} created successfully`)
            await getOrderTypes()
        } else {
            newOrderType.value.hide()
            const data = await response.json();
            alert.show(`Error creating ${newOrderTypeName.value}: ${data.message}`)
            console.log(data.message)
        }
    } catch (e) {
        console.error(e)
    }
}

//  Edit docuement types
const editOrderType = async (order) => {
    try {
        const response = await fetchApi(`/api/order-types/${order.id}`, {
            method: "PUT",
            body: JSON.stringify({
                "name": order.name,
                "description": order.description,
                "required_documents_ids": order.required_documents_ids
            })
        })
        if (response.ok) {
            editOrderT.value.hide()
            alert.show(`Order ${order.name} edited successfully`)
            await getOrderTypes()
        } else {
            editOrderT.value.hide()
            const data = await response.json();
            alert.show(`Error editing ${order.name}: ${data.message}`)
            console.log(data.message)
        }
    } catch (e) {
        console.error(e)
    }
}

const showDeleteOrderTypeModal = (order) => {
    deleteOrderTypeName.value = order.name;
    editOrderTypeId.value = order.id;
    if (!deleteOrderT.value && deleteOrderTypeModal.value) {
        deleteOrderT.value = new Modal(deleteOrderTypeModal.value);
    }
    deleteOrderT.value?.show();
};


const showNewOrderTypeModal = () => {
    if (!newOrderType.value && newOrderTypeModal.value) {
        newOrderType.value = new Modal(newOrderTypeModal.value);
    }
    newOrderType.value?.show();
};

const showEditOrderTypeModal = (order) => {
    const orderCopy = JSON.parse(JSON.stringify(order))

    // Create an array of IDs from an array of objects
    orderCopy.required_documents_ids = orderCopy.required_documents.map(doc => doc.id)

    editingOrderType.value = orderCopy

    if (!editOrderT.value && editOrderTypeModal.value) {
        editOrderT.value = new Modal(editOrderTypeModal.value);
    }
    editOrderT.value?.show();
};


onMounted(async () => {
    getOrderTypes();
    getDocumentTypes();
    await nextTick();
    if (deleteOrderTypeModal.value) {
        deleteOrderT.value = new Modal(deleteOrderTypeModal.value)
    }
    if (newOrderTypeModal.value) {
        newOrderType.value = new Modal(newOrderTypeModal.value)
    }
    if (editOrderTypeModal.value) {
        editOrderT.value = new Modal(editOrderTypeModal.value)
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