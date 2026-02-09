<template>
    <h1>Registrar Types</h1>
    <hr>
    <div class="container hero-content" v-if="registrars.length > 0">
        <table class="table table-striped-columns">
            <thead class="table-dark">
                <tr>
                    <th scope="col">#</th>
                    <th scope="col">Name</th>
                    <th scope="col">Email</th>
                    <th scope="col">Address</th>
                    <th scope="col">Link</th>
                    <th scope="col">Action</th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="registrar in registrars" :key="registrar.id">
                    <th scope="row">{{ registrar.id }}</th>
                    <td>{{ registrar.name }}</td>
                    <td>{{ registrar.email }}</td>
                    <td>{{ registrar.address }}</td>
                    <td>{{ registrar.link }}</td>
                    <td>
                        <div>
                            <button class="btn btn-warning" @click="showeditRegModal(registrar)">Edit</button>
                            <button class="btn btn-danger" @click="showDeleteRegistrarModal(registrar)">Delete</button>
                        </div>
                    </td>
                </tr>
            </tbody>
        </table>
        <button class="btn btn-primary" @click="showNewRegistrarModal">Create New</button>
    </div>
    <div v-else class="alert alert-info" role="alert">
        <p>There are no registrar types. Create a new one.</p>
        <hr>
        <button class="btn btn-primary" @click="showNewRegistrarModal">Create New</button>
    </div>
    

    <div ref="deleteRegistrarModal" class="modal fade" tabindex="-1">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Delete Registrar</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <div class="mb-3 align-items-center">
                        <h5>Delete registrar type: {{ deleteRegistrarName }}</h5>
                    </div>
                </div>
                <div class="modal-footer">
                    <button @click="deleteRegistrar(deleteRegistrarId)" class="btn btn-danger">Delete</button>
                </div>
            </div>
        </div>
    </div>

    <div ref="editRegModal" class="modal fade" tabindex="-1">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Edit Registrar</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <div class="mb-3">
                        <label for="registrarName" class="form-label">Name</label>
                        <input type="text" v-model="editingRegistrar.name" name="registrarName" id="registrarName"
                            class="form-control" placeholder="Registrar Name">
                    </div>
                    <div class="mb-3">
                        <label for="registrarEmail" class="form-label">Email</label>
                        <input type="email" v-model="editingRegistrar.email" name="registrarEmail" id="registrarEmail"
                            class="form-control" placeholder="Registrar Email">
                    </div>
                    <div class="mb-3">
                        <label for="registrarAddress" class="form-label">Address</label>
                        <input type="text" v-model="editingRegistrar.address" name="registrarAddress" id="registrarAddress"
                            class="form-control" placeholder="Registrar Address">
                    </div>
                    <div class="mb-3">
                        <label for="registrarLink" class="form-label">Link</label>
                        <input type="url" v-model="editingRegistrar.link" name="registrarLink" id="registrarLink"
                            class="form-control" placeholder="Registrar Link">
                    </div>
                </div>
                <div class="modal-footer">
                    <button @click="editRegistrar(editingRegistrar)" class="btn btn-danger">Submit</button>
                </div>
            </div>
        </div>
    </div>

    <div ref="newRegistrarModal" class="modal fade" tabindex="-1">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Create Registrar</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <div class="mb-3">
                        <label for="newRegistrarName" class="form-label">Name</label>
                        <input type="text" v-model="newRegistrarName" name="newRegistrarName" id="newRegistrarName" class="form-control" placeholder="Registrar Name">
                    </div>
                    <div class="mb-3">
                        <label for="newRegistrarEmail" class="form-label">Email</label>
                        <input type="email" v-model="newRegistrarEmail" name="newRegistrarEmail" id="newRegistrarEmail" class="form-control" placeholder="Registrar Email">
                    </div>
                    <div class="mb-3">
                        <label for="newRegistrarAddress" class="form-label">Address</label>
                        <input type="text" v-model="newRegistrarAddress" name="newRegistrarAddress" id="newRegistrarAddress" class="form-control" placeholder="Registrar Address">
                    </div>
                    <div class="mb-3">
                        <label for="newRegistrarLink" class="form-label">Link</label>
                        <input type="url" v-model="newRegistrarLink" name="newRegistrarLink" id="newRegistrarLink" class="form-control" placeholder="Registrar Link">
                    </div>
                </div>
                <div class="modal-footer">
                    <button @click="createRegistrar" class="btn btn-danger">Submit</button>
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


const newRegistrarName = ref("");
const newRegistrarEmail = ref("");
const newRegistrarAddress = ref("");
const newRegistrarLink = ref("");
const newRegistrarModal = ref(null);
const newRegistrar = ref(null);

const editRegModal = ref(null);
const editReg = ref(null);
const editingRegistrar = ref({});

const deleteRegistrarModal = ref(null);
const deleteRegistrarName = ref('');
const deleteRegistrarId = ref('');
const deleteReg = ref(null);

const registrars = ref([]);


//  Fetch docuement types
const getRegistrars = async() => {
    try{
        const response = await fetchApi('/api/registrars', {
            method: "GET"
        })
        if (response.ok){
            const data = await response.json()
            registrars.value = data
        }
    } catch (e) {
        console.error("Error fetching data: ", e)
    }
}


//  Delete docuement types
const deleteRegistrar = async(registrar_id) => {
    try{
        const response = await fetchApi(`/api/registrars/${registrar_id}`, {
            method: "DELETE"
        });
        if (response.ok) {
            deleteReg.value.hide();
            alert.show("Deleted Successfully", "success")
            await getRegistrars();
        }
    } catch (e) {
        console.error(e)
    }
}


//  Create docuement types
const createRegistrar = async() => {
    try {
        const response = await fetchApi('/api/registrars', {
            method: "POST",
            body: JSON.stringify({
                "name": newRegistrarName.value,
                "email": newRegistrarEmail.value,
                "address": newRegistrarAddress.value,
                "link": newRegistrarLink.value
            })
        })
        if (response.ok) {
            newRegistrar.value.hide()
            alert.show(`Registrar ${newRegistrarName.value} created successfully`)
            await getRegistrars()
        } else {
            newRegistrar.value.hide()
            const data = await response.json();
            alert.show(`Error creating ${newRegistrarName.value}: ${data.message}`)
            console.log(data.message)
        }
    } catch (e) {
        console.error(e)
    }
}

//  Edit docuement types
const editRegistrar = async (registrar) => {
    try {
        const response = await fetchApi(`/api/registrars/${registrar.id}`, {
            method: "PUT",
            body: JSON.stringify({
                "name": registrar.name,
                "email": registrar.email,
                "address": registrar.address,
                "link": registrar.link
            })
        })
        if (response.ok) {
            editReg.value.hide()
            alert.show(`Registrar ${registrar.name} edited successfully`)
            await getRegistrars()
        } else {
            editReg.value.hide()
            const data = await response.json();
            alert.show(`Error editing ${registrar.name}: ${data.message}`)
            console.log(data.message)
        }
    } catch (e) {
        console.error(e)
    }
}

const showDeleteRegistrarModal = (registrar) => {
    deleteRegistrarName.value = registrar.name;
    deleteRegistrarId.value = registrar.id;
    if (!deleteReg.value && deleteRegistrarModal.value) {
        deleteReg.value = new Modal(deleteRegistrarModal.value);
    }
    deleteReg.value?.show();
};


const showNewRegistrarModal = () => {
    if (!newRegistrar.value && newRegistrarModal.value) {
        newRegistrar.value = new Modal(newRegistrarModal.value);
    }
    newRegistrar.value?.show();
};

const showeditRegModal = (registrar) => {
    editingRegistrar.value = JSON.parse(JSON.stringify(registrar))
    if (!editReg.value && editRegModal.value) {
        editReg.value = new Modal(editRegModal.value);
    }
    editReg.value?.show();
};


onMounted(async () => {
    getRegistrars();
    await nextTick();
    if (deleteRegistrarModal.value) {
        deleteReg.value = new Modal(deleteRegistrarModal.value)
    }
    if (newRegistrarModal.value) {
        newRegistrar.value = new Modal(newRegistrarModal.value)
    }
    if (editRegModal.value) {
        editReg.value = new Modal(editRegModal.value)
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