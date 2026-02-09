<template>
    <div>
        <div class="comments-sidebar-toggle" @click="isCommentsSidebarOpen = !isCommentsSidebarOpen">
            <i class="bi bi-chat-left-text"></i> Comments
        </div>

        <div class="comments-sidebar" :class="{ 'is-open': isCommentsSidebarOpen }">
            <div class="sidebar-header">
                <h3>Order Comments</h3>
                <button class="btn-close" @click="isCommentsSidebarOpen = false"></button>
            </div>
            <div class="sidebar-content">
                <div class="text-center mb-3">
                    <button class="btn btn-sm btn-success w-100" @click="showNewCommentModal">Add Comment</button>
                </div>
                <hr>

                <div v-if="paginatedComments.length > 0">
                    <div v-for="comment in paginatedComments" :key="comment.id">
                        <div class="justify-content-between align-content-center d-flex">
                            <p>{{ comment.comment_text }}</p>
                            <button v-if="comment.file_path" class="btn btn-sm btn-outline-info"
                                @click="viewCommentFile(comment.file_path)" style="max-height: 32px;">
                                View Attachment
                            </button>
                        </div>
                        <div class="d-flex justify-content-end align-items-end" style="gap: 5px;">
                            <button class="btn btn-outline-danger btn-sm"
                                @click="showDeleteCommentModal(comment)">
                                Delete
                            </button>
                            <button class="btn btn-outline-warning btn-sm"
                                @click="showEditCommentModal(comment)">
                                Edit
                            </button>
                        </div>
                        <hr>
                    </div>
                    <div class="d-flex justify-content-between">
                        <button class="btn btn-sm btn-outline-secondary" @click="prevPage" :disabled="currentCommentPage === 1">Previous</button>
                        <span>Page {{ currentCommentPage }} of {{ totalPages }}</span>
                        <button class="btn btn-sm btn-outline-secondary" @click="nextPage" :disabled="currentCommentPage === totalPages">Next</button>
                    </div>
                </div>
                <div v-else>
                    <p>No Comments for this order</p>
                </div>
            </div>
        </div>
        <div class="comments-sidebar-overlay" v-if="isCommentsSidebarOpen" @click="isCommentsSidebarOpen = false"></div>
    </div>

    <!-- Modals (moved from OrderDetail.vue) -->
    <!-- New Comment Modal -->
    <div ref="newCommentModalEl" class="modal fade" tabindex="-1">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">New Comment</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <div class="mb-3">
                        <label for="comment" class="form-label">Comment</label>
                        <textarea class="form-control" id="comment" rows="3" v-model="commentText"></textarea>
                    </div>
                    <input class="form-control" type="file" @change="handleCommentFileUpload">
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-primary" @click="confirmNewComment">Submit</button>
                </div>
            </div>
        </div>
    </div>

    <!-- Edit Comment Modal -->
    <div class="modal fade" id="editCommentModal" tabindex="-1" aria-labelledby="editCommentModalLabel"
        aria-hidden="true" ref="editCommentModal">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title" id="editCommentModalLabel">Edit Comment</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body">
                    <form @submit.prevent="updateComment">
                        <div class="mb-3">
                            <label for="editCommentText" class="form-label">Comment</label>
                            <textarea class="form-control" id="editCommentText" rows="3"
                                v-model="commentToEdit.comment_text"></textarea>
                        </div>
                        <div class="mb-3">
                            <label for="editCommentFile" class="form-label">Replace Attachment</label>
                            <input class="form-control" type="file" id="editCommentFile" @change="handleEditedCommentFileChange">
                            <small v-if="commentToEdit.file_path" class="form-text text-muted">Current file: {{
                                commentToEdit.file_path }}</small>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                            <button type="submit" class="btn btn-primary">Save changes</button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>

    <!-- Delete Comment Confirmation Modal -->
    <div class="modal fade" id="deleteCommentModal" tabindex="-1" aria-labelledby="deleteCommentModalLabel"
        aria-hidden="true" ref="deleteCommentModal">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title" id="deleteCommentModalLabel">Confirm Deletion</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body">
                    Are you sure you want to delete this comment? This action cannot be undone.
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                    <button type="button" class="btn btn-danger" @click="deleteComment">Delete</button>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useAlertStore } from '@/stores/alertMessageStore';
import { Modal } from 'bootstrap';
import {fetchApi} from '../../utils/api'; // Assuming @/utils/api exists from project structure

const props = defineProps({
    orderId: {
        type: [String, Number],
        required: true
    },
    // We'll expose a function to the parent to trigger re-fetching comments
    // Or, we can let the sidebar manage its own comments data
    // For simplicity, let's make it manage its own data initially and emit an event when comments are updated.
});

// Emits for parent communication
const emit = defineEmits(['comments-updated']);

const alert = useAlertStore();

const isCommentsSidebarOpen = ref(false);
const allComments = ref([]);
const currentCommentPage = ref(1);
const pageSize = 5; // Adjust as needed

// Modals
const newCommentModalEl = ref(null);
const editCommentModal = ref(null);
const deleteCommentModal = ref(null);

let modals = {}; // Bootstrap modal instances

const commentText = ref('');
const commentFile = ref(null);
const commentToEdit = ref({});
const editedCommentFile = ref(null);
const commentToDelete = ref({});

const fetchComments = async () => {
    try {
        const response = await fetchApi(`/api/orders/${props.orderId}/comments`);
        if (response.ok) {
            allComments.value = await response.json();
            emit('comments-updated'); // Notify parent that comments have been updated
        } else {
            const errorData = await response.json();
            alert.show(errorData.message || 'Failed to fetch comments.', 'error');
        }
    } catch (e) {
        alert.show('An error occurred while fetching comments.', 'error');
    }
};

const paginatedComments = computed(() => {
    const start = (currentCommentPage.value - 1) * pageSize;
    const end = start + pageSize;
    return allComments.value.slice(start, end);
});

const totalPages = computed(() => {
    return Math.ceil(allComments.value.length / pageSize);
});

const nextPage = () => {
    if (currentCommentPage.value < totalPages.value) {
        currentCommentPage.value++;
    }
};

const prevPage = () => {
    if (currentCommentPage.value > 1) {
        currentCommentPage.value--;
    }
};

const getFileUrl = (filePath) => {
    const baseUrl = "http://localhost:8080"; // This should ideally be in a config
    return `${baseUrl}/api/uploads/${filePath}`;
};

// --- Comment Modals Logic ---
const showNewCommentModal = () => {
    commentText.value = '';
    commentFile.value = null;
    modals.newComment.show();
};

const handleCommentFileUpload = (event) => {
    commentFile.value = event.target.files[0];
};

const confirmNewComment = async () => {
    const formData = new FormData();
    formData.append('comment_text', commentText.value);
    if (commentFile.value) {
        formData.append('file', commentFile.value);
    }

    try {
        // Use fetchApi for consistent error handling
        const response = await fetch(`/api/orders/${props.orderId}/comments`, {
            method: 'POST',
            body: formData,
            headers: {} 
        });
        if (response.ok){
            const data = await response.json();
            alert.show(data.message, 'success');
            modals.newComment.hide();
            await fetchComments();
        } else {
            const data = await response.json();
            alert.show(data.message, 'error');
        }
        
    } catch (error) {
        console.error(error);
        // fetchApi already displays the error, so no need for alert.show here
    }
};

const showEditCommentModal = (comment) => {
    commentToEdit.value = JSON.parse(JSON.stringify(comment)); // Deep copy
    editedCommentFile.value = null; // Reset file input
    modals.editComment.show();
};

const handleEditedCommentFileChange = (event) => {
    editedCommentFile.value = event.target.files[0];
};

const updateComment = async () => {
    const formData = new FormData();
    formData.append('comment_text', commentToEdit.value.comment_text);
    if (editedCommentFile.value) {
        formData.append('file', editedCommentFile.value);
    }
    // If an existing file should be removed without replacing,
    // a separate checkbox/action would be needed. For now, if no new file is selected,
    // the existing one (if any) remains unless explicit instruction to remove.

    try {
        // Use fetchApi for consistent error handling
        const response = await fetch(`/api/orders/${props.orderId}/comments/${commentToEdit.value.id}`, {
            method: 'PUT',
            body: formData,
            headers: {} 
        });
        
        const data = await response.json();
        alert.show(data.message, 'success');
        modals.editComment.hide();
        await fetchComments();
    } catch (error) {
        console.error(error);
        // fetchApi already displays the error, so no need for alert.show here
    }
};

const showDeleteCommentModal = (comment) => {
    commentToDelete.value = comment;
    modals.deleteComment.show();
};

const deleteComment = async () => {
    try {
        const response = await fetchApi(`/api/orders/${props.orderId}/comments/${commentToDelete.value.id}`, {
            method: 'DELETE'
        });
        if (response.ok) {
            const data = await response.json();
            alert.show(data.message, 'success');
            modals.deleteComment.hide();
            await fetchComments();
        } else {
            const errorData = await response.json();
            alert.show(errorData.message || 'Failed to delete comment.', 'error');
        }
    } catch (error) {
        console.error(error);
        alert.show('An error occurred while deleting the comment.', 'error');
    }
};

const viewCommentFile = async (filePath) => {
    try {
        const response = await fetchApi(`/api/uploads/${filePath}`, { method: 'HEAD' });
        if (response.ok) {
            window.open(getFileUrl(filePath), '_blank');
        } else {
            let errorMessage = 'Comment attachment not found.';
            try {
                const errorData = await response.json();
                errorMessage = errorData.message || errorMessage;
            } catch (e) {
                // If not JSON, use default
            }
            alert.show(errorMessage, 'error');
        }
    } catch (error) {
        console.error("Error viewing comment file:", error);
    }
};

onMounted(async () => {
    await fetchComments(); // Fetch comments when sidebar mounts
    modals.newComment = new Modal(newCommentModalEl.value);
    modals.editComment = new Modal(editCommentModal.value);
    modals.deleteComment = new Modal(deleteCommentModal.value);
});
</script>

<style scoped>
.comments-sidebar-toggle {
    position: fixed;
    top: 35%;
    right: 0;
    transform: translateY(-50%) rotate(270deg);
    transform-origin: bottom right;
    background-color: #799216;
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

.comments-sidebar {
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

.comments-sidebar.is-open {
    transform: translateX(0);
}

.comments-sidebar-overlay {
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

.comments-item {
    background: #f8f9fa;
    padding: 10px;
    border-radius: 5px;
    margin-bottom: 10px;
}

.comments-item.is-completed {
    text-decoration: line-through;
    opacity: 0.7;
}

.comments-description {
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
