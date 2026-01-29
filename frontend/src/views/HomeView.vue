<template>
    <h1>Home Page</h1>
    <div class="container text-center">
        <div class="row">
            <div class="col-4 column">
                <h3>Partners</h3>
                <router-link class="btn btn-info" to="/partners">View Partners</router-link>
                <router-link class="btn btn-info" to="/new-partner">New Partners</router-link>
            </div>
            <div class="col-4 column">
                <h3>Clients</h3>
                <router-link class="btn btn-info" to="/clients">View Clients</router-link>
                <router-link class="btn btn-info" to="/new-client">New Clients</router-link>
            </div>
            <div class="col-4 column">
                <h3>Orders</h3>
                <router-link class="btn btn-info" to="/orders">View Orders</router-link>
                <router-link class="btn btn-info" to="/new-order">New Order</router-link>
            </div>
            <div class="col-4 column">
                <h3>Timeline</h3>
                <a class="btn btn-info" href="/view-timelines">View Timelines</a>
                <a class="btn btn-info" href="/new-timeline">New Timeline</a>
            </div>
            <a class="btn btn-info" href="/document-types">View Timelines</a>
        </div>
        <button @click="showAlert" class="btn btn-primary mt-3">Show Alert</button>
    </div>
</template>

<script setup>
import { useAlertStore } from '@/stores/alertMessageStore'

const alertStore = useAlertStore()

const showAlert = () => {
    alertStore.show('This is a test alert!', 'success')
}
</script>

<style scoped>
a {
    margin: 2px;
}
</style>
