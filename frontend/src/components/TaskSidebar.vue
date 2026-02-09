<template>
    <div>
        <div class="task-sidebar-toggle" @click="isTaskSidebarOpen = !isTaskSidebarOpen">
            <i class="bi bi-calendar-check"></i> Tasks
        </div>

        <div class="task-sidebar" :class="{ 'is-open': isTaskSidebarOpen }">
            <div class="sidebar-header">
                <h3>Order Tasks</h3>
                <button class="btn-close" @click="isTaskSidebarOpen = false"></button>
            </div>
            <div class="sidebar-content">
                <div v-if="showCreateTaskButton" class="text-center mb-3">
                    <button class="btn btn-primary w-100" @click="$emit('create-task')">Create New Task</button>
                </div>

                <div v-if="showGrouping" class="mb-3">
                    <label for="group-by-select" class="form-label">Group By</label>
                    <select id="group-by-select" class="form-select" v-model="groupBy">
                        <option value="date">Date</option>
                        <option value="order">Order</option>
                    </select>
                </div>
                <hr>

                <div v-if="tasks.length > 0">
                    <div v-for="(group, groupName) in groupedTasks" :key="groupName" class="mb-4">
                        <h6 class="text-muted">{{ groupName }}</h6>
                        <ul class="list-unstyled">
                            <li v-for="task in group" :key="task.id" class="task-item"
                                :class="{ 'is-completed': task.is_completed }">
                                <div class="form-check">
                                    <input class="form-check-input" type="checkbox" :checked="task.is_completed"
                                        @change="$emit('toggle-completion', task)">
                                    <label class="form-check-label">{{ task.title }}</label>
                                </div>
                                <p v-if="task.description" class="task-description">{{ task.description }}</p>
                                <div class="d-flex justify-content-between align-items-center mt-2">
                                    <small v-if="showOrderName && task.order" class="text-muted">Order: {{ task.order.name
                                        }}</small>
                                    <RouterLink class="btn btn-sm btn-outline-primary" :to="{ name: 'order-details', params: {id: task.order_id} }">Go To Order</RouterLink>
                                </div>
                            </li>
                        </ul>
                    </div>
                </div>
                <div v-else class="text-center text-muted mt-4">
                    <p>No tasks found.</p>
                </div>
            </div>
        </div>
        <div class="task-sidebar-overlay" v-if="isTaskSidebarOpen" @click="isTaskSidebarOpen = false"></div>
    </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';

const props = defineProps({
    tasks: {
        type: Array,
        required: true
    },
    showCreateTaskButton: {
        type: Boolean,
        default: false
    },
    showOrderName: {
        type: Boolean,
        default: false
    },
    showGrouping: {
        type: Boolean,
        default: false
    }
});

defineEmits(['create-task', 'toggle-completion']);

const router = useRouter();
const isTaskSidebarOpen = ref(false);
const groupBy = ref('date');

const formatDate = (dateString) => new Date(dateString).toLocaleDateString(undefined, { weekday: 'long', month: 'long', day: 'numeric' });

const groupedTasks = computed(() => {
    const grouped = {};
    if (groupBy.value === 'date') {
        props.tasks.forEach(task => {
            const dateStr = formatDate(task.due_date);
            if (!grouped[dateStr]) {
                grouped[dateStr] = [];
            }
            grouped[dateStr].push(task);
        });
    } else if (groupBy.value === 'order') {
        props.tasks.forEach(task => {
            const orderName = task.order ? `Order #${task.order.id}: ${task.order.name}` : 'No Order';
            if (!grouped[orderName]) {
                grouped[orderName] = [];
            }
            grouped[orderName].push(task);
        });
    }
    return grouped;
});

</script>

<style scoped>
.task-sidebar-toggle {
    position: fixed;
    top: 50%;
    right: 0;
    transform: translateY(-50%) rotate(270deg);
    transform-origin: bottom right;
    background-color: #0d6efd;
    color: white;
    padding: 8px 15px;
    cursor: pointer;
    z-index: 1051;
    border-top-left-radius: 5px;
    border-top-right-radius: 5px;
    font-size: 1rem;
    writing-mode: horizontal-tb;
    display: flex;
    align-items: center;
    gap: 5px;
}

.task-sidebar {
    position: fixed;
    top: 0;
    right: 0;
    width: 380px;
    height: 100%;
    background: #fff;
    box-shadow: -5px 0 15px rgba(0, 0, 0, 0.1);
    transform: translateX(100%);
    transition: transform 0.3s ease-in-out;
    z-index: 1052;
    display: flex;
    flex-direction: column;
}

.task-sidebar.is-open {
    transform: translateX(0);
}

.task-sidebar-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.5);
    z-index: 1050;
}

.sidebar-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem;
    border-bottom: 1px solid #dee2e6;
}

.sidebar-content {
    padding: 1rem;
    overflow-y: auto;
    flex-grow: 1;
}

.task-item {
    background: #f8f9fa;
    padding: 10px;
    border-radius: 5px;
    margin-bottom: 10px;
}

.task-item.is-completed {
    text-decoration: line-through;
    opacity: 0.7;
}

.task-description {
    font-size: 0.85rem;
    color: #6c757d;
    margin-left: 2rem;
    margin-top: 5px;
    margin-bottom: 0;
}

.btn {
    min-width: 70px;
}
</style>
