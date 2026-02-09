<template>
    <transition name="fade">
        <!-- <div v-if="alertStore.visible" class="alert-container"> -->
            <!-- <div class="backdrop" :class="alertStore.type"></div> -->
            <div v-if="alertStore.visible" class="alert-box alert" :class="alertStore.type">
                <i class="bi bi-exclamation-diamond-fill"></i> {{ alertStore.message }}
            </div>
        <!-- </div> -->
    </transition>
</template>

<script setup>
import { useAlertStore } from '@/stores/alertMessageStore'

const alertStore = useAlertStore()
</script>

<style scoped>
/* .alert-container {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: 999;
    display: flex;
    justify-content: center;
    align-items: flex-start;
} */

/* .backdrop {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    backdrop-filter: blur(5px);
}

.backdrop.success {
    background-color: rgba(84, 88, 0, 0.45);
}

.backdrop.error {
    background-color: rgba(101, 12, 0, 0.45);
}

.backdrop.warning {
    background-color: rgba(75, 70, 0, 0.45);
}

.backdrop.info {
    background-color: rgba(0, 65, 88, 0.45);
} */

.alert-box {
    text-align: center;
    font-weight: bold;
    /* margin-top: 100px; */
    position: fixed;
    top: 15px;
    right: 20px;
    z-index: 9999; /* Increased z-index to be above the comments sidebar */
    color: white;
    padding: 15px 20px;
    border-radius: 8px;
    border: 0px solid white;
    font-size: 16px;
    box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.4);
    opacity: 1;
    transition: opacity 0.5s ease-in-out;
    /* min-width: 50vw; */
}

.alert-box.success {
    background: linear-gradient(45deg, #b1ca57, #6caf1f);
}
.alert-box.error {
    background: linear-gradient(45deg, #ff416c, #ff4b2b);
}
.alert-box.danger {
    background: linear-gradient(45deg, #ff416c, #ff4b2b);
}
.alert-box.warning {
    background: linear-gradient(45deg, #b49c4c, #837617);
}
.alert-box.info {
    background: linear-gradient(45deg, #4db2b7, #177e83);
}

.fade-enter-active,
.fade-leave-active {
    transition: opacity 0.5s;
}

.fade-enter,
.fade-leave-to {
    opacity: 0;
}
</style>