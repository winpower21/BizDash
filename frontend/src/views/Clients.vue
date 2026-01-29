<template>
    <div class="parent">
        <h1>Clients</h1>
        <hr>
        <div class="container" v-if="clients.length > 0">
            <div class="list-table">
                <table role="grid" :class="{ 'has-focus': focusedClientId !== null }" ref="clientTable">
                    <thead>
                        <tr>
                            <th>Name</th>
                            <th>Email</th>
                            <th>Phone</th>
                            <th>Address</th>
                            <th>Orders</th>
                            <th>Action</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="client in clients" :key="client.id" :data-client-id="client.id"
                            :class="{ 'focused-row': focusedClientId === client.id }">
                            <td>
                                <input type="text" class="client-name inp" name="name" v-model="client.name"
                                    @focus="focusedClientId = client.id" aria-label="name" />
                            </td>
                            <td>
                                <input type="email" class="client-email inp" name="email" v-model="client.email"
                                    @focus="focusedClientId = client.id" aria-label="email" />
                            </td>
                            <td :class="{ 'has-validation-error': validationErrors.has(client.id) }">
                                <div class="input-wrapper">
                                    <input type="tel" class="client-phone inp" name="phone" v-model="client.phone"
                                        @focus="focusedClientId = client.id" aria-label="phone"
                                        :class="{ 'is-invalid': validationErrors.has(client.id) }" />
                                    <div v-if="validationErrors.has(client.id)" class="invalid-feedback">
                                        {{ validationErrors.get(client.id) }}
                                    </div>
                                </div>
                            </td>
                            <td>
                                <textarea name="address" class="client-address" v-model="client.address" @focus="focusedClientId = client.id" aria-label="address"></textarea>
                            </td>
                            <td>
                                <p class="text-center">{{ client.orders.length }}</p>
                            </td>
                            <td class="action-cell">
                                <div class="d-flex justify-content-around">
                                    <button type="button" @click="updateClient(client)"
                                        class="submit-btn btn p-2 mx-2"
                                        :disabled="!dirtyClientIds.has(client.id) || validationErrors.has(client.id)">
                                        Submit
                                    </button>
                                    <button type="button" @click="deleteClient(client)"
                                        class="submit-btn btn p-2 mx-2">
                                        Delete
                                    </button>
                                </div>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
            <div class="text-center mt-4">
                <a href="/new-client" class="btn btn-primary new-client-button">Add New Client</a>
            </div>
        </div>
        <div v-else class="container text-center d-flex flex-column justify-content-center  align-items-center"
            style="min-height: 80vh;">
            <h1>No clients exist</h1>
            <a href="/new-client" class="btn btn-primary">Add New Client</a>
        </div>
    </div>
</template>


<script setup>
import fetchApi from '../../utils/api';
import { ref, onMounted, onUnmounted, watch } from 'vue';
import { useAlertStore } from '@/stores/alertMessageStore';
import { validatePhone } from '../../utils/validators';

// --- Reactive State ---

// Holds the list of clients displayed in the table.
const clients = ref([]);
// Tracks the ID of the client whose row is currently in focus.
const focusedClientId = ref(null);
// A Map to store a deep copy of the original client data to compare against for changes.
const originalClients = ref(new Map());
// A Set to store the IDs of clients that have been modified but not saved.
const dirtyClientIds = ref(new Set());
// A template ref to get direct access to the table DOM element.
const clientTable = ref(null);
// Instance of the Pinia store for showing global alert messages.
const alertStore = useAlertStore();
// A Map to store validation error messages for each client row, keyed by client ID.
const validationErrors = ref(new Map());


// --- Functions ---

/**
 * Reverts any changes made to a client's data back to its original state.
 * @param {number} clientId - The ID of the client to revert.
 */
const revertChanges = (clientId) => {
    // Only proceed if the client is marked as "dirty" (modified).
    if (dirtyClientIds.value.has(clientId)) {
        const clientIndex = clients.value.findIndex(p => p.id === clientId);
        if (clientIndex !== -1) {
            const originalClient = originalClients.value.get(clientId);
            if (originalClient) {
                // Restore the client's data by replacing it with the stored original copy.
                clients.value[clientIndex] = JSON.parse(JSON.stringify(originalClient));
            }
        }
    }
}

/**
 * Handles clicks outside the main data table.
 * If a row is in focus and the user clicks elsewhere, it reverts any unsaved changes.
 * @param {Event} event - The click event object.
 */
const handleClickOutside = (event) => {
    // Check if the click happened outside the table and a row is currently focused.
    if (clientTable.value && !clientTable.value.contains(event.target)) {
        if (focusedClientId.value !== null) {
            revertChanges(focusedClientId.value);
            // Reset the focus state.
            focusedClientId.value = null;
        }
    }
}

/**
 * Fetches the complete list of clients from the API.
 * Initializes the component's state, including the `clients` list for display
 * and a `originalClients` deep copy for tracking changes.
 */
const allClients = async () => {
    try {
        const response = await fetchApi('/api/clients', { method: "GET" })
        if (response.ok) {
            const data = await response.json();

            let clientData = Array.isArray(data) ? data : (data.clients || data.data || data.results || []);
            clients.value = clientData;

            const newOriginalClients = new Map();
            clientData.forEach(p => {
                newOriginalClients.set(p.id, JSON.parse(JSON.stringify(p)));
            });
            originalClients.value = newOriginalClients;

            dirtyClientIds.value.clear();
            validationErrors.value.clear();
        } else {
            if (response.status !== 404) {
                alertStore.show('Failed to load clients.', 'error');
                console.error(response.status);
            }
            else {
                console.warn(response.message)
            }
        }
    } catch (error) {
        console.error(error);
        alertStore.show('An error occurred while fetching clients.', 'error');
    }
}

/**
 * Prompts the user for confirmation and deletes a client both from the backend and the local state.
 * @param {object} client - The client object to be deleted.
 */
const deleteClient = async (client) => {
    // Use a confirmation dialog as a safeguard for destructive actions.
    if (!window.confirm(`Are you sure you want to delete ${client.name}?`)) {
        return;
    }

    try {
        const response = await fetchApi(`/api/clients/${client.id}`, {
            method: "DELETE",
        })
        if (response.ok) {
            const data = await response.json();
            alertStore.show(data.message || 'Client deleted successfully!', 'success');

            // Remove the client from the local reactive array to update the UI instantly.
            const index = clients.value.findIndex(p => p.id === client.id);
            if (index > -1) {
                clients.value.splice(index, 1);
            }

            // Clean up all related state.
            originalClients.value.delete(client.id);
            dirtyClientIds.value.delete(client.id);
            validationErrors.value.delete(client.id);

        } else {
            const errorData = await response.json();
            alertStore.show(errorData.message || 'Failed to delete client.', 'error');
            console.error('Failed to delete client:', response.statusText);
        }
    } catch (error) {
        alertStore.show('An error occurred while deleting.', 'error');
        console.error('Error deleting client:', error);
    }
}


/**
 * Submits updated client data to the backend.
 * Contains guards to prevent submission if data is unchanged or invalid.
 * On success, it updates the local state with the response from the server.
 * @param {object} client - The client object with updated data.
 */
const updateClient = async (client) => {
    // Guard against submitting if the data hasn't changed.
    if (!dirtyClientIds.value.has(client.id)) {
        console.log("No changes to update for client:", client.id);
        return;
    }
    // Guard against submitting if there are validation errors.
    if (validationErrors.value.has(client.id)) {
        alertStore.show('Please fix validation errors before submitting.', 'error');
        return;
    }

    try {
        const response = await fetchApi(`/api/clients/${client.id}`, {
            method: "PUT",
            body: JSON.stringify({
                name: client.name,
                email: client.email,
                phone: client.phone,
                address: client.address
            })
        });

        if (response.ok) {
            const updatedClient = await response.json();

            // --- IMPORTANT: Order of Operations ---
            // 1. Explicitly mark the row as not dirty. This is the most robust way
            // to prevent the watcher from incorrectly re-marking it as dirty.
            dirtyClientIds.value.delete(client.id);

            // 2. Update the "original" state to match the newly saved data.
            originalClients.value.set(updatedClient.id, JSON.parse(JSON.stringify(updatedClient)));

            // 3. Find and update the specific client in the local reactive array.
            // This will trigger the deep watcher, which will now find nothing to do.
            const index = clients.value.findIndex(p => p.id === updatedClient.id);
            if (index !== -1) {
                clients.value[index] = updatedClient;
            }

            // 4. Show success message.
            alertStore.show('Client updated successfully!', 'success');

        } else {
            const errorData = await response.json();
            alertStore.show(errorData.message || 'Failed to update client.', 'error');
            console.error('Failed to update client:', response.statusText);
        }
    } catch (error) {
        alertStore.show('An error occurred while updating.', 'error');
        console.error('Error updating client:', error);
    }
}


// --- Watchers & Lifecycle Hooks ---

/**
 * Deep watcher on the `clients` array. This is the core of the component's reactivity.
 * It compares the current state of each client with its original state to:
 * 1. Determine if a row is "dirty" (modified).
 * 2. Validate the phone number field as it changes.
 */
watch(clients, (newClients) => {
    newClients.forEach(client => {
        const originalClient = originalClients.value.get(client.id);
        if (originalClient) {
            // 1. Check for dirtiness by comparing the stringified versions of the objects.
            if (JSON.stringify(client) !== JSON.stringify(originalClient)) {
                dirtyClientIds.value.add(client.id);
            } else {
                dirtyClientIds.value.delete(client.id);
            }

            // 2. Perform validation on the phone number and update the errors map.
            const phoneError = validatePhone(client.phone);
            if (phoneError) {
                validationErrors.value.set(client.id, phoneError);
            } else {
                validationErrors.value.delete(client.id);
            }
        }
    });
}, { deep: true });

// Set up and tear down the global click listener for handling clicks outside the table.
onMounted(() => {
    allClients();
    document.addEventListener('click', handleClickOutside, true);
})

onUnmounted(() => {
    document.removeEventListener('click', handleClickOutside, true);
})

</script>



<style scoped>
.parent {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1rem;
    padding: 2rem;
}

h1 {
    margin: 0;
    color: var(--color);
    font-size: 1.8rem;
}

hr {
    border: none;
    height: 2px;
    background-color: var(--accent);
    width: 80%;
    margin: 0;
}

.list-table {
    background: var(--background);
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    overflow: hidden;
}

table {
    width: 100%;
    border-collapse: collapse;
    transition: all 0.3s ease;
}

thead {
    background: var(--head);
    position: sticky;
    top: 0;
    text-align: center;
}

th {
    padding: 1rem;
    text-align: center;
    font-weight: 600;
    font-size: 0.875rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: var(--color);
    border-bottom: 2px solid var(--border);
}

td {
    padding: 0;
    min-height: 48px;
    /* Use min-height for flexibility */
    border-bottom: 1px solid var(--border);
    transition: min-height 0.3s ease, padding-bottom 0.3s ease;
    /* Smooth transition */
}

/* Add extra space to the td when there's a validation error */
td.has-validation-error {
    padding-bottom: 25px;
    /* Enough space for the error message */
    min-height: 73px;
    /* 48px (base) + 25px (padding) */
}

input {
    width: 100%;
    height: 100%;
    border: none;
    padding: 1rem;
    background: transparent;
    color: var(--color);
    font-size: 0.9rem;
    font-family: inherit;
    transition: all 0.2s ease;
}

tbody tr {
    transition: background-color 0.3s ease, filter 0.3s ease, opacity 0.3s ease;
}

/* Rule 1 & 6: Hover effect on tbody rows only */
tbody tr:hover {
    background-color: var(--hover-background);
}

/* Rule 4: When a row is focused, disable hover effect for all rows */
table.has-focus tbody tr:hover {
    background-color: transparent;
}

/* Rule 2: When a row has focus, blur other rows */
table.has-focus tbody tr {
    filter: blur(2px);
    opacity: 0.6;
}

/* Rule 2: Selected row styles */
table.has-focus tr.focused-row {
    background-color: var(--selected-background) !important;
    filter: blur(0);
    opacity: 1;
}

/* Rule 3: Highlight the focused input */
input:focus {
    outline: none;
    background-color: var(--highlight) !important;
    box-shadow: inset 0 0 5px rgba(0, 0, 0, 0.1);
}

/* Make sure the selected row's inputs have the correct background */
tr.focused-row input {
    background-color: var(--selected-background);
}


.action-cell {
    text-align: center;
}

.submit-btn {
    width: 100%;
    height: 100%;
    padding: 1rem;
    background: transparent;
    color: var(--accent);
    border: none;
    font-weight: 600;
    font-size: 0.9rem;
    cursor: pointer;
    transition: all 0.2s ease;
    text-transform: uppercase;
}

.submit-btn:hover {
    background: #ff6a35;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(255, 127, 80, 0.3);
    /* background: rgba(96, 125, 139, 0.2); */
    /* Using the new --accent color with opacity */
    color: white;
    /* color: var(--accent); */
}

.submit-btn:active {
    background: rgba(96, 125, 139, 0.3);
    /* Slightly more opaque for active state */
}

.submit-btn:disabled {
    background-color: #e0e0e0;
    color: #9e9e9e;
    cursor: not-allowed;
}

.text-center {
    text-align: center;
    margin-top: 2rem;
}

.btn {
    display: inline-block;
    padding: 0.75rem 1.5rem;
    background: var(--accent);
    color: white;
    text-decoration: none;
    border-radius: 4px;
    font-weight: 600;
    transition: all 0.2s ease;
    cursor: pointer;
    border: none;
    font-size: 0.9rem;
}

.btn:hover {
    background: #ff6a35;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(255, 127, 80, 0.3);
}

.input-wrapper {
    position: relative;
    height: 100%;
}

.is-invalid {
    border: 1px solid #dc3545 !important;
}

.invalid-feedback {
    color: #dc3545;
    font-size: 0.8rem;
    position: absolute;
    bottom: -18px;
    left: 1rem;
    background: white;
    padding: 0 5px;
    z-index: 10;
    /* Ensure it's on top */
}

.client-phone {
    max-width: 120px;
}
.inp {
    text-align: center;
}
</style>