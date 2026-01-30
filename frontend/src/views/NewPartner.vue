<template>
    <div class="hero-section">
        <h1>New Partner</h1>
        <hr>
        <form @submit.prevent="newPartner">
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
                <label class="form-label">
                    Partner Share: {{ Math.round(share * 100) }}%
                </label>

                <input type="range" class="form-range" v-model.number="share" min="0.05" max="0.95" step="0.05" />
            </div>
            <button type="submit" class="btn btn-primary">Submit</button>
        </form>
    </div>
</template>


<script setup>
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useAlertStore } from '@/stores/alertMessageStore'
import fetchApi from '../../utils/api';

const router = useRouter()
const alert = useAlertStore()

const name = ref(null);
const email = ref(null);
const phone = ref('');
const share = ref(0.5)

const phoneError = computed(() => {
    if (phone.value.length === 0) return ''
    if (!/^\d+$/.test(phone.value)) return 'Only digits are allowed'
    if (phone.value.startsWith('0')) return 'Phone number cannot start with 0'
    if (phone.value.length !== 10) return 'Phone number must be exactly 10 digits'
    return ''
})

const newPartner = async () => {
    try {
        const response = await fetchApi('/api/partners', {
            method: "POST",
            body: JSON.stringify({
                name: name.value,
                email: email.value,
                phone: phone.value,
                revenue_share: share.value
            })
        });
        if (response.ok) {
            router.push({ name: 'partners' })
            alert.show('New Partner Created Successfully', 'success')
        } else {
            const errorData = await response.json();
            alert.show(errorData.message, 'error');
        }
    } catch (error) {
        console.error("Error creating new partner")
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