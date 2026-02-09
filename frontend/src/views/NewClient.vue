<template>
    <div class="hero-section">
        <h1>New Client</h1>
        <hr>
        <form @submit.prevent="newClient">
            <div class="mb-3">
                <label for="name" class="form-label">Name</label>
                <input type="text" class="form-control" id="name" name="name" v-model="name" required />
            </div>
            <div class="mb-3">
                <label for="email" class="form-label">Email address</label>
                <input type="email" class="form-control" id="email" name="email" v-model="email" required />
            </div>
            <div class="mb-3">
                <label for="phone" class="form-label">Phone</label>
                <input type="tel" class="form-control" v-model="phone" :class="{ 'is-invalid': phoneError }"
                    inputmode="numeric" />

                <div class="invalid-feedback">
                    {{ phoneError }}
                </div>

            </div>
            <div class="mb-3">
                <label for="address" class="form-label">Address</label>
                <textarea name="address" id="address" class="form-control" v-model="address"></textarea>
            </div>
            <button type="submit" class="btn btn-primary">Submit</button>
        </form>
    </div>
</template>


<script setup>
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useAlertStore } from '@/stores/alertMessageStore'
import {fetchApi} from '../../utils/api';

const router = useRouter()
const alert = useAlertStore()

const name = ref(null);
const email = ref(null);
const phone = ref('');
const address = ref(null)

const phoneError = computed(() => {
    if (phone.value.length === 0) return ''
    if (!/^\d+$/.test(phone.value)) return 'Only digits are allowed'
    if (phone.value.startsWith('0')) return 'Phone number cannot start with 0'
    if (phone.value.length !== 10) return 'Phone number must be exactly 10 digits'
    return ''
})

const newClient = async () => {
    try {
        const response = await fetchApi('/api/clients', {
            method: "POST",
            // headers: {
            //     'Content-Type': 'application/json',
            // },
            body: JSON.stringify({
                name: name.value,
                email: email.value,
                phone: phone.value,
                address: address.value
            })
        });
        if (response.ok) {
            router.push({ name: 'clients' })
            alert.show('New Client Created Successfully', 'success')
        } else {
            const errorData = await response.json();
            alert.show(errorData.message, 'error');
        }
    } catch (error) {
        console.error("Error creating new client")
        alert.show(error, 'error');
    }
}

</script>

<style scoped>
.hero-section {
    max-width: 95vw;
    margin: 0px 40px 0px 40px;
}
</style>