<script setup>
import Sidebar from './components/Sidebar.vue';
import { RouterView } from 'vue-router';
import AlertMessage from './components/AlertMessage.vue';
</script>

<template>
    <div class="wrapper">
        <div class="sb">
            <Sidebar />
        </div>
        <div class="content">
            <AlertMessage />
            <RouterView />
        </div>
    </div>
</template>


<style scoped>
.wrapper {
    display: flex;
    width: 100vw;
    height: 100vh;
    overflow-x: hidden;
}


.sb {
    position: sticky;
    top: 0;
    align-self: flex-start;
}

.content {
    flex: 1;
    padding: 20px;
    gap: 5px;
    overflow-y: auto;
    transition: all 0.3s ease;
    min-width: 0;
}
</style>