<template>
    <div class="hero-container">
        <component :is="activeComponent" />
    </div>
</template>


<script setup>
import { computed } from 'vue';
import { useRoute } from 'vue-router';
import DocumentTypes from '@/components/DocumentTypes.vue';
import OrderTypes from '@/components/OrderTypes.vue';
import Companies from '@/components/Companies.vue';
import Registrars from '@/components/Registrars.vue';
import OrderStatus from '@/components/OrderStatus.vue';

const route = useRoute();

const componentMap = {
    '/document-types': DocumentTypes,
    '/order-types': OrderTypes,
    '/order-status': OrderStatus,
    '/companies': Companies,
    '/registrars': Registrars,
}

const activeComponent = computed(() => {
    return componentMap[route.path] || null
})

</script>