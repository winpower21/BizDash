<template>
    <h1>Companies</h1>
    <hr>
    <div class="container hero-content" v-if="companies.length > 0">
        <table class="table table-striped-columns">
            <thead class="table-dark">
                <tr>
                    <th scope="col">#</th>
                    <th scope="col">Name</th>
                    <th scope="col">Registrar</th>
                    <th scope="col">Action</th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="company in companies" :key="company.id">
                    <th scope="row">{{ company.id }}</th>
                    <td>{{ company.name }}</td>
                    <td>{{ company.registrar.name }}</td>
                    <td>
                        <div>
                            <button class="btn btn-warning" @click="showEditCompanyModal(company)">Edit</button>
                            <button class="btn btn-danger" @click="showDeleteCompanyModal(company)">Delete</button>
                        </div>
                    </td>
                </tr>
            </tbody>
        </table>
        <button class="btn btn-primary" @click="showNewCompanyModal">Create New</button>
    </div>
    <div v-else class="container text-center d-flex flex-column justify-content-center  align-items-center"
        style="min-height: 80vh;">
        There are no companies. Create a new one.
        <button class="btn btn-primary" @click="showNewCompanyModal">Create New</button>
    </div>
    

    <div ref="deleteCompanyModal" class="modal fade" tabindex="-1">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Delete Company</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <div class="mb-3 align-items-center">
                        <h5>Delete company: {{ deleteCompanyName }}</h5>
                    </div>
                </div>
                <div class="modal-footer">
                    <button @click="deleteCompany(deleteCompanyId)" class="btn btn-danger">Delete</button>
                </div>
            </div>
        </div>
    </div>

    <div ref="editDocumentModal" class="modal fade" tabindex="-1">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Edit Company</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <div class="mb-3">
                        <label for="companyName" class="form-label">Name</label>
                        <input type="text" v-model="editingCompany.name" name="companyName" id="companyName"
                            class="form-control" placeholder="Company Name">
                    </div>
                    <div class="mb-3">
                        <label for="registrar" class="form-label">Registrar</label>
                        <select class="form-select" aria-label="Registrar">
                            <option selected>Select Registrar</option>
                            <option v-for="registrar in registrars" :key="registrar.id" value="{{registrar.id}}">{{ registrar.name }}</option>
                        </select>
                    </div>
                </div>
                <div class="modal-footer">
                    <button @click="editDocumentType(editingCompany)" class="btn btn-danger">Submit</button>
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
                        <label for="companyName" class="form-label">Name</label>
                        <input type="text" v-model="newDocumentName" name="companyName" id="companyName" class="form-control" placeholder="Document Name">
                    </div>
                    <div class="mb-3">
                        <label for="registrar" class="form-label">Description</label>
                        <input type="text" v-model="newDocumentDescription" name="registrar" id="registrar"
                            class="form-control" placeholder="Registrar">
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
const editingCompany = ref({});

const deleteCompanyModal = ref(null);
const deleteCompanyName = ref('');
const deleteCompanyId = ref('');
const deleteDocument = ref(null);

const companies = ref([]);


//  Fetch docuement types
const getDocumentTypes = async() => {
    try{
        const response = await fetchApi('/api/document-types', {
            method: "GET"
        })
        if (response.ok){
            const data = await response.json()
            companies.value = data
        }
    } catch (e) {
        console.error("Error fetching data: ", e)
    }
}


//  Delete docuement types
const deleteCompany = async(document_id) => {
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

const showDeleteCompanyModal = (document) => {
    deleteCompanyName.value = document.name;
    deleteCompanyId.value = document.id;
    if (!deleteDocument.value && deleteCompanyModal.value) {
        deleteDocument.value = new Modal(deleteCompanyModal.value);
    }
    deleteDocument.value?.show();
};


const showNewCompanyModal = () => {
    if (!newDocument.value && newDocumentModal.value) {
        newDocument.value = new Modal(newDocumentModal.value);
    }
    newDocument.value?.show();
};

const showEditCompanyModal = (document) => {
    editingCompany.value = document
    if (!editDocument.value && editDocumentModal.value) {
        editDocument.value = new Modal(editDocumentModal.value);
    }
    editDocument.value?.show();
};


onMounted(async () => {
    getDocumentTypes();
    await nextTick();
    if (deleteCompanyModal.value) {
        deleteDocument.value = new Modal(deleteCompanyModal.value)
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