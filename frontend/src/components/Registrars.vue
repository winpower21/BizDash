<template>
    <h1>Document Types</h1>
    <hr>
    <div class="container hero-content" v-if="documentTypes.length > 0">
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
                <tr v-for="document in documentTypes" :key="document.id">
                    <th scope="row">{{ document.id }}</th>
                    <td>{{ document.name }}</td>
                    <td>{{ document.description }}</td>
                    <td>
                        <div>
                            <button class="btn btn-warning" @click="showEditDocumentModal(document)">Edit</button>
                            <button class="btn btn-danger" @click="showDeleteDocumentModal(document)">Delete</button>
                        </div>
                    </td>
                </tr>
            </tbody>
        </table>
        <button class="btn btn-primary" @click="showNewDocumentModal">Create New</button>
    </div>
    <div v-else class="container text-center d-flex flex-column justify-content-center  align-items-center"
        style="min-height: 80vh;">
        There are no document types. Create a new one.
        <button class="btn btn-primary" @click="showNewDocumentModal">Create New</button>
    </div>
    

    <div ref="deleteDocumentModal" class="modal fade" tabindex="-1">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Delete Document</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <div class="mb-3 align-items-center">
                        <h5>Delete document type: {{ deleteDocumentName }}</h5>
                    </div>
                </div>
                <div class="modal-footer">
                    <button @click="deleteDocumentType(deleteDocumentId)" class="btn btn-danger">Delete</button>
                </div>
            </div>
        </div>
    </div>

    <div ref="editDocumentModal" class="modal fade" tabindex="-1">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Edit Document</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <h3>Edit Document Type</h3>
                    <div class="mb-3">
                        <label for="documentName" class="form-label">Name</label>
                        <input type="text" v-model="editingDocument.name" name="documentName" id="documentName"
                            class="form-control" placeholder="Document Name">
                    </div>
                    <div class="mb-3">
                        <label for="documentDescription" class="form-label">Description</label>
                        <input type="text" v-model="editingDocument.description" name="documentDescription"
                            id="documentDescription" class="form-control" placeholder="Document Description">
                    </div>
                </div>
                <div class="modal-footer">
                    <button @click="editDocumentType(editingDocument)" class="btn btn-danger">Submit</button>
                </div>
            </div>
        </div>
    </div>

    <div ref="newDocumentModal" class="modal fade" tabindex="-1">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Create Document</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <h3>New Document Type</h3>
                    <div class="mb-3">
                        <label for="documentName" class="form-label">Name</label>
                        <input type="text" v-model="newDocumentName" name="documentName" id="documentName" class="form-control" placeholder="Document Name">
                    </div>
                    <div class="mb-3">
                        <label for="documentDescription" class="form-label">Description</label>
                        <input type="text" v-model="newDocumentDescription" name="documentDescription" id="documentDescription"
                            class="form-control" placeholder="Document Description">
                    </div>
                </div>
                <div class="modal-footer">
                    <button @click="createDocumentType" class="btn btn-danger">Submit</button>
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


const newDocumentName = ref("");
const newDocumentDescription = ref("");
const newDocumentModal = ref(null);
const newDocument = ref(null);

const editDocumentModal = ref(null);
const editDocument = ref(null);
const editingDocument = ref({});

const deleteDocumentModal = ref(null);
const deleteDocumentName = ref('');
const deleteDocumentId = ref('');
const deleteDocument = ref(null);

const documentTypes = ref([]);


//  Fetch docuement types
const getDocumentTypes = async() => {
    try{
        const response = await fetchApi('/api/document-types', {
            method: "GET"
        })
        if (response.ok){
            const data = await response.json()
            documentTypes.value = data
        }
    } catch (e) {
        console.error("Error fetching data: ", e)
    }
}


//  Delete docuement types
const deleteDocumentType = async(document_id) => {
    try{
        const response = await fetchApi(`/api/document-types/${document_id}`, {
            method: "DELETE"
        });
        if (response.ok) {
            deleteDocument.value.hide();
            alert.show("Deleted Successfully", "success")
            await getDocumentTypes()
        }
    } catch (e) {
        console.error(e)
    }
}


//  Create docuement types
const createDocumentType = async() => {
    try {
        const response = await fetchApi('/api/document-types', {
            method: "POST",
            body: JSON.stringify({
                "name": newDocumentName.value,
                "description": newDocumentDescription.value
            })
        })
        if (response.ok) {
            newDocument.value.hide()
            alert.show(`Document ${newDocumentName.value} created successfully`)
            await getDocumentTypes()
        } else {
            newDocument.value.hide()
            const data = await response.json();
            alert.show(`Error creating ${newDocumentName.value}: ${data.message}`)
            console.log(data.message)
        }
    } catch (e) {
        console.error(e)
    }
}

//  Edit docuement types
const editDocumentType = async (document) => {
    try {
        const response = await fetchApi(`/api/document-types/${document.id}`, {
            method: "PUT",
            body: JSON.stringify({
                "name": document.name,
                "description": document.description
            })
        })
        if (response.ok) {
            editDocument.value.hide()
            alert.show(`Document ${document.name} edited successfully`)
            await getDocumentTypes()
        } else {
            editDocument.value.hide()
            const data = await response.json();
            alert.show(`Error editing ${document.name}: ${data.message}`)
            console.log(data.message)
        }
    } catch (e) {
        console.error(e)
    }
}

const showDeleteDocumentModal = (document) => {
    deleteDocumentName.value = document.name;
    deleteDocumentId.value = document.id;
    if (!deleteDocument.value && deleteDocumentModal.value) {
        deleteDocument.value = new Modal(deleteDocumentModal.value);
    }
    deleteDocument.value?.show();
};


const showNewDocumentModal = () => {
    if (!newDocument.value && newDocumentModal.value) {
        newDocument.value = new Modal(newDocumentModal.value);
    }
    newDocument.value?.show();
};

const showEditDocumentModal = (document) => {
    editingDocument.value = document
    if (!editDocument.value && editDocumentModal.value) {
        editDocument.value = new Modal(editDocumentModal.value);
    }
    editDocument.value?.show();
};


onMounted(async () => {
    getDocumentTypes();
    await nextTick();
    if (deleteDocumentModal.value) {
        deleteDocument.value = new Modal(deleteDocumentModal.value)
    }
    if (newDocumentModal.value) {
        newDocument.value = new Modal(newDocumentModal.value)
    }
    if (editDocumentModal.value) {
        editDocument.value = new Modal(editDocumentModal.value)
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