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
    <div v-else-if="registrars.length > 0 & companies.length == 0" class="container text-center d-flex flex-column justify-content-center  align-items-center"
        style="min-height: 80vh;">
        There are no companies. Create a new one.
        <button class="btn btn-primary" @click="showNewCompanyModal">Create New</button>
    </div>
    <div v-else-if="registrars.length == 0"
        class="container text-center d-flex flex-column justify-content-center  align-items-center"
        style="min-height: 80vh;">
        There are no registrars yet. Create a new one before adding companies.
        <RouterLink class="btn btn-primary" to="/registrars">New Registrar</RouterLink>
    </div>
    
    
    <!-- Create company -->
    <div ref="newCompanyModal" class="modal fade" tabindex="-1">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Create Company</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <h3>New Company</h3>
                    <div class="mb-3">
                        <label for="companyName" class="form-label">Name</label>
                        <input type="text" v-model="newCompanyName" name="companyName" id="companyName" class="form-control" placeholder="Company Name">
                    </div>
                    <div class="mb-3">
                        <label for="registrar" class="form-label">Description</label>
                        <input type="text" v-model="newCompanyRegistrar" name="registrar" id="registrar"
                        class="form-control" placeholder="Registrar">
                    </div>
                    <div class="mb-3">
                        <label for="registrar" class="form-label">Registrar</label>
                        <select class="form-select" aria-label="Registrar">
                            <option selected>Select Registrar</option>
                            <option v-for="registrar in registrars" :key="registrar.id" value="{{registrar.id}}">{{
                                registrar.name }}</option>
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
    <div ref="editCompanyModal" class="modal fade" tabindex="-1">
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
                    <button @click="editComp(editingCompany)" class="btn btn-danger">Submit</button>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Delete company -->
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


const newCompanyName = ref("");
const newCompanyRegistrar = ref("");
const newCompanyModal = ref(null);
const newCompany = ref(null);

const editCompanyModal = ref(null);
const editCompany = ref(null);
const editingCompany = ref({});

const deleteCompanyModal = ref(null);
const deleteCompanyName = ref('');
const deleteCompanyId = ref('');
const delCompany = ref(null);

const companies = ref([]);
const registrars = ref([]);


const getRegistrars = async() => {
    try {
        const response = await fetchApi('/api/registrars', {
            method: "GET"
        })
        if (response.ok) {
            const data = await response.json();
            registrars.value = data;
        }
        else {
            console.warn("Error")
        }
    } catch (e) {
        console.log(e)
    }
}


const getCompanies = async() => {
    try {
        const response = await fetchApi('/api/companies', {
            method: "GET"
        })
        if (response.ok) {
            const data = await response.json();
            companies.value = data;
        }
        else {
            console.warn("Error")
        }
    } catch (e) {
        console.log(e)
    }
}


//  Delete company
const deleteCompany = async(company_id) => {
    try{
        const response = await fetchApi(`/api/companies/${company_id}`, {
            method: "DELETE"
        });
        if (response.ok) {
            delCompany.value.hide();
            alert.show("Deleted Successfully", "success")
            await getCompanies()
        }
    } catch (e) {
        console.error(e)
    }
}


//  Create company
const createCompany = async() => {
    try {
        const response = await fetchApi('/api/companies', {
            method: "POST",
            body: JSON.stringify({
                "name": newCompanyName.value,
                "description": newCompanyRegistrar.value
            })
        })
        if (response.ok) {
            newCompany.value.hide()
            alert.show(`Company ${newCompanyName.value} created successfully`)
            await getCompanies()
        } else {
            newCompany.value.hide()
            const data = await response.json();
            alert.show(`Error creating ${newCompanyName.value}: ${data.message}`)
            console.log(data.message)
        }
    } catch (e) {
        console.error(e)
    }
}

//  Edit company
const editComp = async (company) => {
    try {
        const response = await fetchApi(`/api/companies/${company.id}`, {
            method: "PUT",
            body: JSON.stringify({
                "name": company.name,
                "description": company.description
            })
        })
        if (response.ok) {
            editCompany.value.hide()
            alert.show(`Company ${company.name} edited successfully`)
            await getCompanies()
        } else {
            editCompany.value.hide();
            const data = await response.json();
            alert.show(`Error editing ${company.name}: ${data.message}`)
            console.log(data.message);
        }
    } catch (e) {
        console.error(e)
    }
}

const showDeleteCompanyModal = (company) => {
    deleteCompanyName.value = company.name;
    deleteCompanyId.value = company.id;
    if (!delCompany.value && deleteCompanyModal.value) {
        delCompany.value = new Modal(deleteCompanyModal.value);
    }
    delCompany.value?.show();
};


const showNewCompanyModal = () => {
    if (!newCompany.value && newCompanyModal.value) {
        newCompany.value = new Modal(newCompanyModal.value);
    }
    newCompany.value?.show();
};

const showEditCompanyModal = (company) => {
    editingCompany.value = company;
    if (!editCompany.value && editCompanyModal.value) {
        editCompany.value = new Modal(editCompanyModal.value);
    }
    editCompany.value?.show();
};


onMounted(async () => {
    getCompanies();
    getRegistrars();
    await nextTick();
    if (deleteCompanyModal.value) {
        delCompany.value = new Modal(deleteCompanyModal.value);
    }
    if (newCompanyModal.value) {
        newCompany.value = new Modal(newCompanyModal.value);
    }
    if (editCompanyModal.value) {
        editCompany.value = new Modal(editCompanyModal.value);
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