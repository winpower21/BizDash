<template>
    <h1>Companies</h1>
    <hr>
    <div class="container hero-content" v-if="companies.length > 0 & registrars.length > 0">
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
    <div v-else-if="registrars.length > 0 & companies.length == 0" class="alert alert-info" role="alert">
        <p>There are no companies. Create a new one.</p>
        <hr>
        <button class="btn btn-primary" @click="showNewCompanyModal">Create New</button>
    </div>
    <div v-else-if="registrars.length == 0" class="alert alert-warning" role="alert">
        <h4 class="alert-heading">Prerequisites Missing!</h4>
        <p>To create a new company, you must first have at least one registrar. Use the link below to create them.</p>
        <hr>
        <RouterLink class="btn btn-primary" to="/registrars">New Registrar</RouterLink>
    </div>


    <!-- Create company -->
    <div ref="newCompanyModalEl" class="modal fade" tabindex="-1">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Create Company</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <div class="mb-3">
                        <label for="companyName" class="form-label">Name</label>
                        <input type="text" v-model="newCompany.name" name="companyName" id="companyName"
                            class="form-control" placeholder="Company Name">
                    </div>
                    <div class="mb-3">
                        <label for="registrar" class="form-label">Registrar</label>
                        <select class="form-select" aria-label="Registrar" v-model="newCompany.registrar_id">
                            <option :value="null" disabled>Select Registrar</option>
                            <option v-for="registrar in registrars" :key="registrar.id" :value="registrar.id">
                                {{ registrar.name }}
                            </option>
                        </select>
                    </div>
                </div>
                <div class="modal-footer">
                    <button @click="createCompany" class="btn btn-danger">Submit</button>
                </div>
            </div>
        </div>
    </div>


    <!-- Edit company -->
    <div ref="editCompanyModalEl" class="modal fade" tabindex="-1">
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
                        <select class="form-select" aria-label="Registrar" v-model="editingCompany.registrar_id">
                            <option :value="null" disabled>Select Registrar</option>
                            <option v-for="registrar in registrars" :key="registrar.id" :value="registrar.id">{{
                                registrar.name }}</option>
                        </select>
                    </div>
                </div>
                <div class="modal-footer">
                    <button @click="editCompany()" class="btn btn-danger">Submit</button>
                </div>
            </div>
        </div>
    </div>

    <!-- Delete company -->
    <div ref="deleteCompanyModalEl" class="modal fade" tabindex="-1">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Delete Company</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <div class="mb-3 align-items-center">
                        <h5>Delete company: {{ delCompany.name }}</h5>
                    </div>
                </div>
                <div class="modal-footer">
                    <button @click="deleteCompany(delCompany.id)" class="btn btn-danger">Delete</button>
                </div>
            </div>
        </div>
    </div>

</template>

<script setup>
import { reactive, ref } from 'vue';
import { onMounted } from 'vue';
import { fetchApi, fetchBatchData } from '../../utils/api';
import { useAlertStore } from '@/stores/alertMessageStore';
import { Modal } from 'bootstrap';

const alert = useAlertStore();

const newCompanyModalEl = ref(null);
const editCompanyModalEl = ref(null);
const deleteCompanyModalEl = ref(null);

const newCompany = reactive({
    name: "",
    registrar_id: null
})
const editingCompany = reactive({
    name:"",
    registrar_id: null
});
const delCompany = reactive({
    name:"",
    registrar_id: null
})

let modals = {};

const companies = ref([]);
const registrars = ref([]);



const fetchData = async () => {
    const [
        regi,
        comp,
    ] = await fetchBatchData([
        '/api/registrars',
        '/api/companies',
    ])
    registrars.value = regi || []
    companies.value = comp || []
}


const getCompanies = async () => {
    try {
        const response = await fetchApi('/api/companies', {
            method: "GET"
        })
        if (response.ok) {
            const data = await response.json();
            console.log(data)
            companies.value = data;
        }
        else {
            console.warn("Error")
        }
    } catch (e) {
        console.log(e)
    }
}

//  Create company
const createCompany = async () => {
    try {
        const response = await fetchApi('/api/companies', {
            method: "POST",
            body: JSON.stringify({
                "name": newCompany.name,
                "registrar_id": newCompany.registrar_id
            })
        })
        if (response.ok) {
            modals.newCompany.hide();
            alert.show(`Company ${newCompany.name} created successfully`)
            await getCompanies()
        } else {
            modals.newCompany.hide();
            const data = await response.json();
            alert.show(`Error creating ${newCompany.name}: ${data.message}`)
            console.log(data.message)
        }
    } catch (e) {
        console.error(e)
    }
}

const showNewCompanyModal = () => {
    newCompany.name="";
    newCompany.registrar_id=null;
    modals.newCompany.show();
}




//  Edit company
const editCompany = async () => {
    try {
        const response = await fetchApi(`/api/companies/${editingCompany.id}`, {
            method: "PUT",
            body: JSON.stringify({
                "name": editingCompany.name,
                "registrar_id": editingCompany.registrar_id
            })
        })
        if (response.ok) {
            modals.editCompany.hide();
            alert.show(`Company ${company.name} edited successfully`)
            await getCompanies()
        } else {
            modals.editCompany.hide();
            const data = await response.json();
            alert.show(`Error editing ${company.name}: ${data.message}`)
            console.log(data.message);
        }
    } catch (e) {
        console.error(e)
    }
}

const showEditCompanyModal = (company) => {
    editingCompany.id = company.id;
    editingCompany.name = company.name;
    editingCompany.registrar_id = company.registrar.id;
    modals.editCompany.show();
}


//  Delete company
const deleteCompany = async (company_id) => {
    try {
        const response = await fetchApi(`/api/companies/${company_id}`, {
            method: "DELETE"
        });
        if (response.ok) {
            modals.deleteCompany.hide();
            alert.show("Deleted Successfully", "success")
            await getCompanies()
        } else {
            modals.deleteCompany.hide();
            const data = await response.json();
            alert.show(`Error deleting company: ${data.message}`)
            console.log(data.message)
        }
    } catch (e) {
        console.error(e)
    }
}

const showDeleteCompanyModal = (company) => {
    delCompany.id = company.id;
    delCompany.name = company.name;
    modals.deleteCompany.show();
}




onMounted(async () => {
    await fetchData();
    modals.newCompany = new Modal(newCompanyModalEl.value);
    modals.editCompany = new Modal(editCompanyModalEl.value);
    modals.deleteCompany = new Modal(deleteCompanyModalEl.value);
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

tbody td .content {
    text-align: center;
}

.btn {
    min-width: 100px;
}
</style>