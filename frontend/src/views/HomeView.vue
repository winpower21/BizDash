<template>
    <h1>Home Page</h1>
    <div class="container text-center">
        <div class="row">
            <div class="col-4 column">
                <h3>Partners</h3>
                <router-link class="btn btn-info" to="/partners">View Partners</router-link>
                <a class="btn btn-info" href="/new-partner">Add Partner</a>
            </div>
            <div class="col-4 column">
                <h3>Clients</h3>
                <a class="btn btn-info" href="/clients">View clients</a>
                <a class="btn btn-info" href="/new-client">Add clients</a>
            </div>
            <div class="col-4 column">
                <h3>Orders</h3>
                <a class="btn btn-info" href="/view-orders">View Orders</a>
                <a class="btn btn-info" href="/new-order">New Order</a>
            </div>
            <div class="col-4 column">
                <h3>Timeline</h3>
                <a class="btn btn-info" href="/view-timelines">View Timelines</a>
                <a class="btn btn-info" href="/new-timeline">New Timeline</a>
            </div>
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
