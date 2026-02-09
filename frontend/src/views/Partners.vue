<template>
    <h1>Partners</h1>
    <hr>
    <div class="container parent" v-if="partners.length > 0">
        <div class="list-table">
            <table role="grid" :class="{ 'has-focus': focusedPartnerId !== null }" ref="partnerTable">
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>Email</th>
                        <th>Phone</th>
                        <th>Revenue Share</th>
                        <th>Action</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="partner in partners" :key="partner.id" :data-partner-id="partner.id"
                        :class="{ 'focused-row': focusedPartnerId === partner.id }">
                        <td>
                            <input type="text" class="partner-name inp" name="name" v-model="partner.name"
                                @focus="focusedPartnerId = partner.id" aria-label="name" />
                        </td>
                        <td>
                            <input type="email" class="partner-email inp" name="email" v-model="partner.email"
                                @focus="focusedPartnerId = partner.id" aria-label="email" />
                        </td>
                        <td :class="{ 'has-validation-error': validationErrors.has(partner.id) }">
                            <div class="input-wrapper">
                                <input type="tel" class="partner-phone inp" name="phone" v-model="partner.phone"
                                    @focus="focusedPartnerId = partner.id" aria-label="phone"
                                    :class="{ 'is-invalid': validationErrors.has(partner.id) }" />
                                <div v-if="validationErrors.has(partner.id)" class="invalid-feedback">
                                    {{ validationErrors.get(partner.id) }}
                                </div>
                            </div>
                        </td>
                        <td>
                            <div>
                                <label class="form-label">
                                    Partner Share: {{ Math.round(partner.revenue_share * 100) }}%
                                </label>
                                <input type="range" class="form-range" min="0.05" max="0.95" step="0.05"
                                    v-model="partner.revenue_share" @focus="focusedPartnerId = partner.id" style="padding-top: 0px; 
                                    padding-bottom: 20px; margin-bottom: 20px;" />
                            </div>
                        </td>
                        <td class="action-cell">
                            <div class="d-flex justify-content-around">
                                <button type="button" @click="updatePartner(partner)" class="submit-btn btn p-2 mx-2"
                                    :disabled="!dirtyPartnerIds.has(partner.id) || validationErrors.has(partner.id)">
                                    Submit
                                </button>
                                <button type="button" @click="deletePartner(partner)" class="submit-btn btn p-2 mx-2">
                                    Delete
                                </button>
                            </div>
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>
        <div class="text-center mt-4">
            <a href="/new-partner" class="btn btn-primary new-client-button">Add New Partner</a>
        </div>
    </div>
    <div v-else class="alert alert-info" role="alert">
        <p>There are no partners. Create a new one.</p>
        <hr>
        <RouterLink class="btn btn-primary" to="/new-partner">New Partner</RouterLink>
    </div>
</template>


<script setup>
import {fetchApi} from '../../utils/api';
import { ref, onMounted, onUnmounted, watch } from 'vue';
import { useAlertStore } from '@/stores/alertMessageStore';
import { validatePhone } from '../../utils/validators';

// --- Reactive State ---

// Holds the list of partners displayed in the table.
const partners = ref([]);
// Tracks the ID of the partner whose row is currently in focus.
const focusedPartnerId = ref(null);
// A Map to store a deep copy of the original partner data to compare against for changes.
const originalPartners = ref(new Map());
// A Set to store the IDs of partners that have been modified but not saved.
const dirtyPartnerIds = ref(new Set());
// A template ref to get direct access to the table DOM element.
const partnerTable = ref(null);
// Instance of the Pinia store for showing global alert messages.
const alertStore = useAlertStore();
// A Map to store validation error messages for each partner row, keyed by partner ID.
const validationErrors = ref(new Map());


// --- Functions ---

/**
 * Reverts any changes made to a partner's data back to its original state.
 * @param {number} partnerId - The ID of the partner to revert.
 */
const revertChanges = (partnerId) => {
    // Only proceed if the partner is marked as "dirty" (modified).
    if (dirtyPartnerIds.value.has(partnerId)) {
        const partnerIndex = partners.value.findIndex(p => p.id === partnerId);
        if (partnerIndex !== -1) {
            const originalPartner = originalPartners.value.get(partnerId);
            if (originalPartner) {
                // Restore the partner's data by replacing it with the stored original copy.
                partners.value[partnerIndex] = JSON.parse(JSON.stringify(originalPartner));
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
    if (partnerTable.value && !partnerTable.value.contains(event.target)) {
        if (focusedPartnerId.value !== null) {
            revertChanges(focusedPartnerId.value);
            // Reset the focus state.
            focusedPartnerId.value = null;
        }
    }
}

/**
 * Fetches the complete list of partners from the API.
 * Initializes the component's state, including the `partners` list for display
 * and a `originalPartners` deep copy for tracking changes.
 */
const allPartners = async () => {
    try {
        const response = await fetchApi('/api/partners', { method: "GET" })
        if (response.ok) {
            const data = await response.json();

            let partnerData = Array.isArray(data) ? data : (data.partners || data.data || data.results || []);
            partners.value = partnerData;

            const newOriginalPartners = new Map();
            partnerData.forEach(p => {
                newOriginalPartners.set(p.id, JSON.parse(JSON.stringify(p)));
            });
            originalPartners.value = newOriginalPartners;

            dirtyPartnerIds.value.clear();
            validationErrors.value.clear();
        } else {
            if (response.status !== 404) {
                alertStore.show('Failed to load partners.', 'error');
                console.error(response.status);
            }
            else {
                console.warn(response.message)
            }
        }
    } catch (error) {
        console.error(error);
        alertStore.show('An error occurred while fetching partners.', 'error');
    }
}

/**
 * Prompts the user for confirmation and deletes a partner both from the backend and the local state.
 * @param {object} partner - The partner object to be deleted.
 */
const deletePartner = async (partner) => {
    // Use a confirmation dialog as a safeguard for destructive actions.
    if (!window.confirm(`Are you sure you want to delete ${partner.name}?`)) {
        return;
    }

    try {
        const response = await fetchApi(`/api/partners/${partner.id}`, {
            method: "DELETE",
        })
        if (response.ok) {
            const data = await response.json();
            alertStore.show(data.message || 'Partner deleted successfully!', 'success');

            // Remove the partner from the local reactive array to update the UI instantly.
            const index = partners.value.findIndex(p => p.id === partner.id);
            if (index > -1) {
                partners.value.splice(index, 1);
            }

            // Clean up all related state.
            originalPartners.value.delete(partner.id);
            dirtyPartnerIds.value.delete(partner.id);
            validationErrors.value.delete(partner.id);

        } else {
            const errorData = await response.json();
            alertStore.show(errorData.message || 'Failed to delete partner.', 'error');
            console.error('Failed to delete partner:', response.statusText);
        }
    } catch (error) {
        alertStore.show('An error occurred while deleting.', 'error');
        console.error('Error deleting partner:', error);
    }
}


/**
 * Submits updated partner data to the backend.
 * Contains guards to prevent submission if data is unchanged or invalid.
 * On success, it updates the local state with the response from the server.
 * @param {object} partner - The partner object with updated data.
 */
const updatePartner = async (partner) => {
    // Guard against submitting if the data hasn't changed.
    if (!dirtyPartnerIds.value.has(partner.id)) {
        console.log("No changes to update for partner:", partner.id);
        return;
    }
    // Guard against submitting if there are validation errors.
    if (validationErrors.value.has(partner.id)) {
        alertStore.show('Please fix validation errors before submitting.', 'error');
        return;
    }

    try {
        const response = await fetchApi(`/api/partners/${partner.id}`, {
            method: "PUT",
            body: JSON.stringify({
                name: partner.name,
                email: partner.email,
                phone: partner.phone,
                revenue_share: partner.revenue_share
            })
        });

        if (response.ok) {
            const updatedPartner = await response.json();

            // --- IMPORTANT: Order of Operations ---
            // 1. Explicitly mark the row as not dirty. This is the most robust way
            // to prevent the watcher from incorrectly re-marking it as dirty.
            dirtyPartnerIds.value.delete(partner.id);

            // 2. Update the "original" state to match the newly saved data.
            originalPartners.value.set(updatedPartner.id, JSON.parse(JSON.stringify(updatedPartner)));

            // 3. Find and update the specific partner in the local reactive array.
            // This will trigger the deep watcher, which will now find nothing to do.
            const index = partners.value.findIndex(p => p.id === updatedPartner.id);
            if (index !== -1) {
                partners.value[index] = updatedPartner;
            }

            // 4. Show success message.
            alertStore.show('Partner updated successfully!', 'success');

        } else {
            const errorData = await response.json();
            alertStore.show(errorData.message || 'Failed to update partner.', 'error');
            console.error('Failed to update partner:', response.statusText);
        }
    } catch (error) {
        alertStore.show('An error occurred while updating.', 'error');
        console.error('Error updating partner:', error);
    }
}


// --- Watchers & Lifecycle Hooks ---

/**
 * Deep watcher on the `partners` array. This is the core of the component's reactivity.
 * It compares the current state of each partner with its original state to:
 * 1. Determine if a row is "dirty" (modified).
 * 2. Validate the phone number field as it changes.
 */
watch(partners, (newPartners) => {
    newPartners.forEach(partner => {
        const originalPartner = originalPartners.value.get(partner.id);
        if (originalPartner) {
            // 1. Check for dirtiness by comparing the stringified versions of the objects.
            if (JSON.stringify(partner) !== JSON.stringify(originalPartner)) {
                dirtyPartnerIds.value.add(partner.id);
            } else {
                dirtyPartnerIds.value.delete(partner.id);
            }

            // 2. Perform validation on the phone number and update the errors map.
            const phoneError = validatePhone(partner.phone);
            if (phoneError) {
                validationErrors.value.set(partner.id, phoneError);
            } else {
                validationErrors.value.delete(partner.id);
            }
        }
    });
}, { deep: true });

// Set up and tear down the global click listener for handling clicks outside the table.
onMounted(() => {
    allPartners();
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
}

th {
    padding: 1rem;
    text-align: left;
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
    color: white;
    text-decoration: none;
    border-radius: 4px;
    font-weight: 600;
    transition: all 0.2s ease;
    cursor: pointer;
    border: none;
    font-size: 0.9rem;
}

tr .btn {
    background: var(--accent);
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
</style>