<template>
    <div class="order-detail-page-wrapper">
        <TaskSidebar :tasks="tasks" :show-create-task-button="true" @create-task="showCreateTaskModal"
            @toggle-completion="toggleTaskCompletion" />
        <CommentsSidebar :order-id="orderId" @comments-updated="handleCommentsUpdated" />


        <div class="container-fluid mt-4 ">
            <div v-if="isLoading" class="text-center mt-5">
                <div class="spinner-border" style="width: 3rem; height: 3rem;" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <p class="mt-2">Loading Order Details...</p>
            </div>

            <div v-else-if="order">
                <!-- Order Summary Card -->
                <div class="card shadow-sm mb-4">
                    <div class="card-header d-flex justify-content-between align-items-center bg-light">
                        <h2 class="mb-0">Order {{ order.id }} : {{ order.name }} -> {{ order.company.name }} <button class="btn btn-sm btn-outline-info ms-2" @click="showRegistrarDetailsModal">View Registrar</button></h2>
                        <span :class="getStatusClass(order.status.name)">{{ order.status.name }}</span>
                    </div>
                    <div class="card-body">
                        <div class="row g-4">
                            <div>
                                <strong>Description:</strong>
                                <p>{{ order.description }}</p>
                            </div>
                            <div class="col-md-4">
                                <h5>Key Info</h5>
                                <p><strong>Client:</strong> {{ order.client.name }}</p>
                                <p><strong>Partner:</strong> {{ order.partner.name }}</p>
                                <p><strong>Order Type:</strong> {{ order.order_type.name }}</p>
                                <p><strong>Created On:</strong> {{ formatDate(order.date_created) }}</p>
                            </div>
                            <div class="col-md-4">
                                <h5>Financials</h5>
                                <p><strong>Fees:</strong>  {{ order.fees.toLocaleString('en-IN', { style: 'currency', currency: 'INR' }) }}</p>
                                <p><strong>Base Charges:</strong>  {{ order.base_charges.toLocaleString('en-IN', { style: 'currency', currency: 'INR' }) }}</p>
                                <p><strong>Payment Status: </strong>
                                    <span :class="order.payment_status ? 'text-success' : 'text-danger'">
                                        {{ order.payment_status ? 'Paid' : 'Unpaid' }}
                                    </span>
                                </p>
                            </div>
                            <div v-if="order.status.name !== 'Success' && order.status.name !== 'Failed'"
                                class="col-md-4 d-flex flex-column align-items-start align-items-md-end">
                                <h5>Actions</h5>
                                <button class="btn btn-secondary btn-sm mb-2" @click="showEditOrderModal">Edit
                                    Order</button>
                                <button class="btn btn-secondary btn-sm mb-2" @click="showChangeStatusModal">Change
                                    Status</button>
                                <button v-if="order.status.name === 'Received'" class="btn btn-danger btn-sm"
                                    @click="showDeleteOrderModal(order)">Delete Order</button>
                            </div>
                        </div>
                        <hr>
                        <div v-if="order.status.name == 'Success' || 'Failed'">
                            <div class="row g-4">
                                <div class="col">
                                    <p><strong>Total Receivables:</strong> {{ order.fees?.toLocaleString('en-IN', {
                                        style: 'currency',
                                        currency: 'INR'
                                    }) }}</p>
                                </div>
                                <div class="col">
                                    <span style="display: flex; gap: 8px;"><strong>Amount Received:</strong>
                                        <p> {{(order.receipts.reduce((sum, r) => sum + r.amount,
                                            0)).toLocaleString('en-IN', {
                                                style: 'currency',
                                                currency: 'INR'
                                            })}}</p>
                                    </span>
                                    <span style="display: flex; gap: 8px;"><strong>Pending Amount:</strong>
                                        <p
                                            :style="{ color: (order.fees - order.receipts.reduce((sum, r) => sum + r.amount, 0)) >= 0 ? 'green' : 'red' }">
                                            {{(order.fees - order.receipts.reduce((sum, r) => sum + r.amount,
                                                0)).toLocaleString('en-IN', {
                                                    style: 'currency',
                                                    currency: 'INR'
                                                })}}
                                        </p>
                                    </span>
                                </div>
                            </div>
                            <div v-if="order.settlements[0]">
                                <hr>
                                <h3>Order Settlement Details</h3>
                                <div class="row g-4">
                                    <div class="col">
                                        <span style="display: flex; gap: 8px;"><strong>Self share: </strong>
                                            <p>{{ (order.settlements[0].self_share).toLocaleString('en-IN', {
                                                style: 'currency',
                                                currency: 'INR'
                                            }) }}</p>
                                        </span>
                                    </div>
                                    <div class="col">
                                        <span style="display: flex; gap: 8px;"><strong>Partner share: </strong>
                                            <p>{{ (order.settlements[0].partner_share).toLocaleString('en-IN', {
                                                style: 'currency',
                                                currency: 'INR'
                                            }) }}</p>
                                        </span>
                                    </div>
                                </div>
                                <p :style="{ color: order.settlement_status ? 'green' : 'orange' }">Settlement Status:
                                    {{ order.settlement_status ? 'Settled' : 'Pending' }}</p>
                                <button class="btn" :class="order.settlement_status ? 'btn-secondary' : 'btn-primary'"
                                    @click="triggerSettlement()" :disabled="order.settlement_status">
                                    Confirm Settlement
                                </button>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="row g-4">
                    <!-- Documents Column -->
                    <div class="col-lg-6">
                        <div class="card shadow-sm">
                            <div class="card-header d-flex justify-content-between align-items-right">
                                <h5 class="mb-0">Documents</h5>
                                <button v-if="order.status.name !== 'Success' && order.status.name !== 'Failed'"
                                    class="btn btn-outline-primary btn-sm" @click="showAddRequiredDocModal">
                                    Add Required Doc
                                </button>
                            </div>
                            <div class="list-group list-group-flush">
                                <div v-for="doc in order.documents" :key="doc.id"
                                    class="list-group-item d-flex justify-content-between align-items-center">
                                    <div>
                                        <p class="mb-0"><strong>{{ doc.document_type.name }}</strong></p>
                                        <small class="text-muted">Status: {{ doc.current_status_rel.name }}</small>
                                    </div>
                                    <div style="display: flex; gap: 5px;">
                                        <button v-if="doc.file_path" class="btn btn-sm btn-info"
                                            @click="viewDocumentFile(doc.file_path)">
                                            View
                                        </button>
                                        <button v-if="order.status.name !== 'Success' && order.status.name !== 'Failed'"
                                            class="btn btn-sm btn-success" @click="showUploadModal(doc)">Upload</button>
                                        <button
                                            v-if="order.status.name !== 'Success' && order.status.name !== 'Failed' && doc.file_path"
                                            class="btn btn-sm btn-danger" @click="showDeleteDocModal(doc)">Delete</button>
                                    </div>
                                </div>
                                <div v-if="!order.documents.length" class="list-group-item text-muted">No documents are
                                    required.</div>
                            </div>
                            <div class="card-footer d-flex justify-content-end align-items-end">
                                <button v-if="order.status.name !== 'Success' && order.status.name !== 'Failed'"
                                    class="btn btn-outline-primary btn-sm" @click="showDocStatusModal">
                                    Set Documents Status
                                </button>
                            </div>
                        </div>
                    </div>

                    <!-- Ledger Column -->
                    <div class="col-lg-6">
                        <div class="card shadow-sm">
                            <div class="card-header d-flex justify-content-between align-items-center">
                                <h5 class="mb-0">Ledger</h5>
                                <div>
                                    <button class="btn btn-success btn-sm me-2" @click="showAddReceiptModal">Add
                                        Receipt</button>
                                    <button class="btn btn-warning btn-sm" @click="showAddExpenseModal">Add
                                        Expense</button>
                                </div>
                            </div>
                            <div class="card-body">
                                <h6>Receipts</h6>
                                <table class="table table-sm table-hover table-striped-columns">
                                    <tbody>
                                        <tr v-for="receipt in order.receipts" :key="receipt.id">
                                            <td scope="col">{{ receipt.description }}</td>
                                            <td scope="col" class="text-end text-success">+ {{
                                                receipt.amount.toLocaleString('en-IN', {
                                                    style: 'currency', currency:
                                                        'INR'
                                                }) }}</td>
                                            <td scope="col" style="width: 15px;"><span
                                                    style="gap: 5px; display: flex;"><button
                                                        class="btn btn-sm btn-outline-danger"
                                                        @click="showDeleteReceiptModal(receipt)">Delete</button><button
                                                        class="btn btn-sm btn-outline-warning"
                                                        @click="showEditReceiptModal(receipt)">Edit</button></span></td>
                                        </tr>
                                        <tr v-if="!order.receipts.length">
                                            <td colspan="2" class="text-muted">No receipts.</td>
                                        </tr>
                                    </tbody>
                                </table>
                                <hr>
                                <h6>Expenses</h6>
                                <table class="table table-sm table-hover">
                                    <tbody>
                                        <tr v-for="expense in order.expenses" :key="expense.id">
                                            <td>{{ expense.description }}</td>
                                            <td class="text-end text-danger">- {{ expense.amount.toLocaleString('en-IN',
                                                { style: 'currency', currency: 'INR' }) }}</td>
                                            <td scope="col" style="width: 15px;"><span
                                                    style="gap: 5px; display: flex;"><button
                                                        class="btn btn-sm btn-outline-danger"
                                                        @click="showDeleteExpenseModal(expense)">Delete</button><button
                                                        class="btn btn-sm btn-outline-warning"
                                                        @click="showEditExpenseModal(expense)">Edit</button></span></td>
                                        </tr>
                                        <tr v-if="!order.expenses.length">
                                            <td colspan="2" class="text-muted">No expenses.</td>
                                        </tr>
                                    </tbody>
                                </table>
                                <hr>
                                <div class="d-flex justify-content-between fs-5">
                                    <strong>Net Total:</strong>
                                    <strong> {{(order.receipts.reduce((sum, r) => sum + r.amount, 0) -
                                        order.expenses.reduce((sum, e) => sum + e.amount, 0)).toLocaleString('en-IN',
                                            { style: 'currency', currency: 'INR' })}}</strong>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <div v-else class="text-center mt-5">
                <h4>Order Not Found</h4>
                <p>The requested order could not be found.</p>
                <RouterLink to="/orders" class="btn btn-primary">Back to Orders</RouterLink>
            </div>
        </div>

        <!-- Create Task Modal -->
        <div ref="createTaskModalEl" class="modal fade" tabindex="-1">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Create New Task</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="mb-3">
                            <label for="task-title" class="form-label">Title</label>
                            <input type="text" id="task-title" class="form-control" v-model="newTask.title">
                        </div>
                        <div class="mb-3">
                            <label for="task-desc" class="form-label">Description</label>
                            <textarea id="task-desc" class="form-control" v-model="newTask.description"></textarea>
                        </div>
                        <div class="mb-3">
                            <label for="task-due-date" class="form-label">Due Date</label>
                            <input type="date" id="task-due-date" class="form-control" v-model="newTask.due_date">
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                        <button type="button" class="btn btn-primary" @click="confirmCreateTask">Create Task</button>
                    </div>
                </div>
            </div>
        </div>

        <!-- Modals -->
        <div ref="changeStatusModalEl" class="modal fade" tabindex="-1">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Change Order Status</h5><button type="button" class="btn-close"
                            data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body"><label for="statusSelect" class="form-label">New Status</label><select
                            id="statusSelect" class="form-select" v-model="newStatusId">
                            <option v-for="status in allOrderStatuses" :key="status.id" :value="status.id">{{
                                status.name }}
                            </option>
                        </select></div>
                    <div class="modal-footer"><button type="button" class="btn btn-secondary"
                            data-bs-dismiss="modal">Close</button><button type="button" class="btn btn-primary"
                            @click="confirmChangeStatus">Save changes</button></div>
                </div>
            </div>
        </div>

        <!-- Add required document modal -->
        <div ref="addRequiredDocModalEl" class="modal fade" tabindex="-1">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Add Required Document</h5><button type="button" class="btn-close"
                            data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div v-for="docType in availableDocsToAdd" :key="docType.id" class="form-check"><input
                                class="form-check-input" type="checkbox" :value="docType.id"
                                :id="`add-doc-${docType.id}`" v-model="docsToAdd"><label class="form-check-label"
                                :for="`add-doc-${docType.id}`">{{
                                    docType.name }}</label></div>
                        <p v-if="!availableDocsToAdd.length" class="text-muted">All possible document types are already
                            required.</p>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-primary" @click="confirmAddRequiredDocs">
                            Add Selected
                        </button>
                    </div>
                </div>
            </div>
        </div>

        <!-- Document Upload Modal -->
        <div ref="uploadModalEl" class="modal fade" tabindex="-1">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Upload: {{ docToUpload?.document_type.name }}</h5><button type="button"
                            class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body"><input class="form-control" type="file" @change="handleFileUpload"></div>
                    <div class="modal-footer"><button type="button" class="btn btn-primary"
                            @click="confirmUpload">Submit</button>
                    </div>
                </div>
            </div>
        </div>

        <!-- Delete document modal -->
        <div ref="deleteDocModalEl" class="modal fade" tabindex="-1">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Confirm Deletion</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <p>Are you sure you want to delete the document: <strong>{{ docToDelete?.document_type.name
                                }}</strong>?</p>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                        <button type="button" class="btn btn-danger" @click="confirmDeleteDoc">Delete</button>
                    </div>
                </div>
            </div>
        </div>

        <div ref="addReceiptModalEl" class="modal fade" tabindex="-1">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Add New Receipt</h5><button type="button" class="btn-close"
                            data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="mb-3"><label for="receipt-desc" class="form-label">Description</label><input
                                type="text" id="receipt-desc" class="form-control" v-model="newReceipt.description">
                        </div>
                        <div class="mb-3"><label for="receipt-amount" class="form-label">Amount</label><input
                                type="number" step="0.01" id="receipt-amount" class="form-control"
                                v-model.number="newReceipt.amount">
                        </div>
                    </div>
                    <div class="modal-footer"><button type="button" class="btn btn-primary"
                            @click="confirmAddReceipt">Save
                            Receipt</button></div>
                </div>
            </div>
        </div>
        <div ref="editReceiptModalEl" class="modal fade" tabindex="-1">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Edit Receipt</h5><button type="button" class="btn-close"
                            data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="mb-3"><label for="receipt-desc" class="form-label">Description</label><input
                                type="text" id="receipt-desc" class="form-control" v-model="editingReceipt.description">
                        </div>
                        <div class="mb-3"><label for="receipt-amount" class="form-label">Amount</label><input
                                type="number" step="0.01" id="receipt-amount" class="form-control"
                                v-model.number="editingReceipt.amount">
                        </div>
                    </div>
                    <div class="modal-footer"><button type="button" class="btn btn-primary"
                            @click="confirmEditReceipt(editingReceipt)">Save
                            Receipt</button></div>
                </div>
            </div>
        </div>
        <div ref="deleteReceiptModalEl" class="modal fade" tabindex="-1">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Delete Receipt</h5><button type="button" class="btn-close"
                            data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <p>Delete receipt: {{ deleteReceipt.description }} : {{ deleteReceipt.amount }}</p>
                    </div>
                    <div class="modal-footer"><button type="button" class="btn btn-primary"
                            @click="confirmDeleteReceipt(deleteReceipt)">Delete</button></div>
                </div>
            </div>
        </div>
        <div ref="addExpenseModalEl" class="modal fade" tabindex="-1">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Add New Expense</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="mb-3">
                            <label for="expense-desc" class="form-label">Description</label>
                            <input type="text" id="expense-desc" class="form-control" v-model="newExpense.description">
                        </div>
                        <div class="mb-3">
                            <label for="expense-amount" class="form-label">Amount</label>
                            <input type="number" step="0.01" id="expense-amount" class="form-control"
                                v-model.number="newExpense.amount">
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-primary" @click="confirmAddExpense">
                            Save Expense
                        </button>
                    </div>
                </div>
            </div>
        </div>
        <div ref="editExpenseModalEl" class="modal fade" tabindex="-1">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Edit Expense</h5><button type="button" class="btn-close"
                            data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="mb-3"><label for="expense-desc" class="form-label">Description</label><input
                                type="text" id="expense-desc" class="form-control" v-model="editingExpense.description">
                        </div>
                        <div class="mb-3"><label for="expense-amount" class="form-label">Amount</label><input
                                type="number" step="0.01" id="expense-amount" class="form-control"
                                v-model.number="editingExpense.amount">
                        </div>
                    </div>
                    <div class="modal-footer"><button type="button" class="btn btn-primary"
                            @click="confirmEditExpense(editingExpense)">Save Expense</button></div>
                </div>
            </div>
        </div>
        <div ref="deleteExpenseModalEl" class="modal fade" tabindex="-1">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Delete Expense</h5><button type="button" class="btn-close"
                            data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <p>Delete receipt: {{ deleteExpense.description }} : {{ deleteExpense.amount }}</p>
                    </div>
                    <div class="modal-footer"><button type="button" class="btn btn-primary"
                            @click="confirmDeleteExpense(deleteExpense)">Delete</button></div>
                </div>
            </div>
        </div>
        <div ref="changeDocumentStatusModalEl" class="modal fade" tabindex="-1" v-if="order">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Change Document Statuses</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div v-for="doc in documentsForStatusChange" :key="doc.id" class="row mb-3 align-items-center">
                            <div class="col-md-6">
                                <label :for="`doc-status-${doc.id}`" class="form-label">{{ doc.document_type.name
                                    }}</label>
                            </div>
                            <div class="col-md-6">
                                <select :id="`doc-status-${doc.id}`" class="form-select"
                                    v-model="doc.current_status_rel.id">
                                    <option v-for="status in allDocumentStatuses" :key="status.id" :value="status.id">{{
                                        status.name }}</option>
                                </select>
                            </div>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                        <button type="button" class="btn btn-primary" @click="confirmChangeDocumentStatus">Save
                            Changes</button>
                    </div>
                </div>
            </div>
        </div>
        <!-- Delete Confirmation Modal -->
        <div ref="deleteOrderModalEl" class="modal fade" tabindex="-1">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Confirm Deletion</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <p>Are you sure you want to delete <strong>Order #{{ orderToDelete?.id }}</strong>?</p>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                        <button type="button" class="btn btn-danger" @click="confirmDelete">Delete</button>
                    </div>
                </div>
            </div>
        </div>
        <!-- Registrar Details Modal -->
        <div ref="registrarModalEl" class="modal fade" tabindex="-1">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Registrar Details</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body" v-if="order?.company?.registrar">
                        <p><strong>Name:</strong> {{ order.company.registrar.name }}</p>
                        <p><strong>Email:</strong> {{ order.company.registrar.email }}</p>
                        <p><strong>Address:</strong> {{ order.company.registrar.address }}</p>
                        <p><strong>Link:</strong> <a :href="order.company.registrar.link" target="_blank">{{
                            order.company.registrar.link }}</a></p>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                    </div>
                </div>
            </div>
        </div>

        <!-- Edit Order Modal -->
        <div ref="editOrderModalEl" class="modal fade" tabindex="-1">
            <div class="modal-dialog" style="min-width: 40vw;">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Edit Order</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body" v-if="editOrder">
                        <div class="mb-3">
                            <label for="edit-order-name" class="form-label">Order Name</label>
                            <input type="text" id="edit-order-name" class="form-control" v-model="editOrder.name">
                        </div>
                        <div class="mb-3">
                            <label for="edit-order-description" class="form-label">Description</label>
                            <textarea id="edit-order-description" class="form-control"
                                v-model="editOrder.description"></textarea>
                        </div>
                        <div class="row">
                            <div class="col-md-6 mb-3">
                                <label for="edit-order-client" class="form-label">Client</label>
                                <select id="edit-order-client" class="form-select" v-model="editOrder.client_id">
                                    <option v-for="client in allClients" :key="client.id" :value="client.id">{{
                                        client.name }}</option>
                                </select>
                            </div>
                            <div class="col-md-6 mb-3">
                                <label for="edit-order-partner" class="form-label">Partner</label>
                                <select id="edit-order-partner" class="form-select" v-model="editOrder.partner_id">
                                    <option v-for="partner in allPartners" :key="partner.id" :value="partner.id">{{
                                        partner.name }}</option>
                                </select>
                            </div>
                        </div>
                        <div class="row">
                            <div class="col-md-6 mb-3">
                                <label for="edit-order-company" class="form-label">Company</label>
                                <select id="edit-order-company" class="form-select" v-model="editOrder.company_id">
                                    <option v-for="company in allCompanies" :key="company.id" :value="company.id">{{
                                        company.name }}</option>
                                </select>
                            </div>
                        </div>
                        <div class="mb-3">
                            <label for="edit-order-type" class="form-label">Order Type</label>
                            <select id="edit-order-type" class="form-select" v-model="editOrder.order_type_id">
                                <option v-for="orderType in allOrderTypes" :key="orderType.id" :value="orderType.id">{{
                                    orderType.name }}</option>
                            </select>
                        </div>
                        <div class="row">
                            <div class="col-md-6 mb-3">
                                <label for="edit-order-fees" class="form-label">Fees</label>
                                <input type="number" step="0.01" id="edit-order-fees" class="form-control"
                                    v-model.number="editOrder.fees">
                            </div>
                            <div class="col-md-6 mb-3">
                                <label for="edit-order-base-charges" class="form-label">Base Charges</label>
                                <input type="number" step="0.01" id="edit-order-base-charges" class="form-control"
                                    v-model.number="editOrder.base_charges">
                            </div>
                        </div>
                        <div class="row">
                            <div class="col-md-6 mb-3">
                                <label for="edit-order-share-count" class="form-label">No. of Shares</label>
                                <input type="number" step="0.01" id="edit-order-share-count" class="form-control"
                                    v-model.number="editOrder.share_count">
                            </div>
                            <div class="col-md-6 mb-3">
                                <label for="edit-order-share-price" class="form-label">Share Price</label>
                                <input type="number" step="0.01" id="edit-order-share-price" class="form-control"
                                    v-model.number="editOrder.share_price">
                            </div>
                        </div>
                        <strong>Order Value: {{ (editOrder.share_count * editOrder.share_price).toLocaleString('en-IN',
                            {
                                style: 'currency',
                                currency: 'INR'
                            }) }}</strong>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                        <button type="button" class="btn btn-primary" @click="confirmEditOrder">Save Changes</button>
                    </div>
                </div>
            </div>
        </div>
    </div>

</template>

<script setup>
import { ref, onMounted, computed, reactive, watch } from 'vue';
import { useRoute } from 'vue-router';
import { useAlertStore } from '@/stores/alertMessageStore';
import { Modal } from 'bootstrap';
import { fetchApi, fetchBatchData, fileUploadApi } from '../../utils/api';
import TaskSidebar from '@/components/TaskSidebar.vue';
import CommentsSidebar from '@/components/CommentsSidebar.vue';

const route = useRoute();
const alert = useAlertStore();
const orderId = route.params.id;

// --- STATE ---
const isLoading = ref(true);
const order = ref(null);
const allOrderStatuses = ref([]);
const allDocumentTypes = ref([]);
const allDocumentStatuses = ref([]);
const allPartners = ref([]);
const allClients = ref([]);
const allCompanies = ref([]);
const allOrderTypes = ref([]);

const tasks = ref([]);

// Modal Elements
const changeStatusModalEl = ref(null);
const addRequiredDocModalEl = ref(null);
const uploadModalEl = ref(null);
const addReceiptModalEl = ref(null);
const editReceiptModalEl = ref(null);
const deleteReceiptModalEl = ref(null);
const addExpenseModalEl = ref(null);
const editExpenseModalEl = ref(null);
const deleteExpenseModalEl = ref(null);
const createTaskModalEl = ref(null);
const deleteOrderModalEl = ref(null);
const changeDocumentStatusModalEl = ref(null);
const docStatusModalEl = ref(null);
const editOrderModalEl = ref(null);
const deleteDocModalEl = ref(null);
const registrarModalEl = ref(null);



const editingReceipt = ref({});
const deleteReceipt = ref({});
const editingExpense = ref({});
const deleteExpense = ref({});
const orderToDelete = ref({});
const editOrder = ref(null);
const docToDelete = ref(null);







// Modal-specific State
// const newTask = reactive({ title: '', description: '', due_date: '' });
const newTask = ref({
    title: "",
    description: "",
    due_date: ""
})

// Modal Instances
let modals = {};

// Modal-specific State
const newStatusId = ref(null);
const docsToAdd = ref([]);
const docToUpload = ref(null);
const uploadedFile = ref(null);
const newReceipt = reactive({ description: '', amount: null });
const newExpense = reactive({ description: '', amount: null });
const documentsForStatusChange = ref([]);


// --- DATA FETCHING ---
const fetchOrderDetails = async () => {
    try {
        const response = await fetchApi(`/api/orders/${orderId}`);
        if (!response.ok) throw new Error('Failed to fetch order details.');
        order.value = await response.json();
        console.log(order.value)
    } catch (e) {
        order.value = null;
        alert.show(e.message, 'error');
    } finally {
        // isLoading.value = false;
    }
};

const fetchTasks = async () => {
    try {
        const response = await fetchApi(`/api/orders/${orderId}/tasks`);
        if (!response.ok) throw new Error('Failed to fetch tasks.');
        tasks.value = await response.json();
        console.log(tasks.value)
    } catch (e) {
        alert.show(e.message, 'warning');
    }
};


const fetchData = async () => {

    const [
        statusRes, 
        docTypesRes, 
        docStatusesRes, 
        partnersRes, 
        clientsRes, 
        companiesRes, 
        orderTypesRes, 
        tasksRes, 
        orderRes
    ] = await fetchBatchData([
        '/api/order-status',
        '/api/document-types',
        '/api/document-status',
        '/api/partners',
        '/api/clients',
        '/api/companies',
        '/api/order-types',
        `/api/orders/${orderId}/tasks`,
        `/api/orders/${orderId}`
    ])
    
    allOrderStatuses.value = statusRes || []
    allDocumentTypes.value = docTypesRes || []
    allDocumentStatuses.value = docStatusesRes || []
    allPartners.value = partnersRes || []
    allClients.value = clientsRes || []
    allCompanies.value = companiesRes || []
    allOrderTypes.value = orderTypesRes || []
    tasks.value = tasksRes || []
    order.value = orderRes || []
};

// --- LIFECYCLE ---
onMounted(async () => {
    isLoading.value = true
    await Promise.all([fetchData()]);
    // Initialize Modals
    modals.changeStatus = new Modal(changeStatusModalEl.value);
    modals.addRequiredDoc = new Modal(addRequiredDocModalEl.value);
    modals.upload = new Modal(uploadModalEl.value);
    modals.addReceipt = new Modal(addReceiptModalEl.value);
    modals.editReceipt = new Modal(editReceiptModalEl.value);
    modals.deleteReceipt = new Modal(deleteReceiptModalEl.value);
    modals.addExpense = new Modal(addExpenseModalEl.value);
    modals.editExpense = new Modal(editExpenseModalEl.value);
    modals.deleteExpense = new Modal(deleteExpenseModalEl.value);
    modals.createTask = new Modal(createTaskModalEl.value);
    modals.deleteOrder = new Modal(deleteOrderModalEl.value);
    modals.docStatus = new Modal(changeDocumentStatusModalEl.value);
    modals.editOrder = new Modal(editOrderModalEl.value);
    modals.deleteDoc = new Modal(deleteDocModalEl.value);
    modals.registrar = new Modal(registrarModalEl.value);

    isLoading.value = false
});

const showRegistrarDetailsModal = () => {
    modals.registrar.show();
};

// --- COMPUTED PROPERTIES ---




const availableDocsToAdd = computed(() => {
    if (!order.value) return [];
    const requiredIds = new Set(order.value.documents.map(d => d.document_type.id));
    return allDocumentTypes.value.filter(d => !requiredIds.has(d.id));
});



watch(() => editOrder.value?.order_type_id, (newOrderTypeId, oldOrderTypeId) => {
    if (!editOrder.value || oldOrderTypeId === undefined || newOrderTypeId === oldOrderTypeId) {
        return;
    }

    const oldOrderType = allOrderTypes.value.find(ot => ot.id === oldOrderTypeId);
    const newOrderType = allOrderTypes.value.find(ot => ot.id === newOrderTypeId);

    if (!oldOrderType || !newOrderType) return;

    const oldRequiredDocTypeIds = new Set(oldOrderType.required_documents.map(d => d.id));
    const newRequiredDocTypeIds = new Set(newOrderType.required_documents.map(d => d.id));

    // Filter out old, un-uploaded documents
    const documentsToKeep = editOrder.value.documents.filter(doc => {
        // Keep if it's already uploaded
        if (doc.file_path) {
            return true;
        }
        // Keep if it was NOT a required doc for the old order type (i.e., it was manually added)
        if (!oldRequiredDocTypeIds.has(doc.document_type.id)) {
            return true;
        }
        // Otherwise, it was a required doc for the old type and is not uploaded, so don't keep it.
        return false;
    });

    const currentDocTypeIds = new Set(documentsToKeep.map(d => d.document_type.id));

    // Add new required documents that are not already present
    newRequiredDocTypeIds.forEach(newDocTypeId => {
        if (!currentDocTypeIds.has(newDocTypeId)) {
            const docType = allDocumentTypes.value.find(d => d.id === newDocTypeId);
            if (docType) {
                // This is a simplified structure for a new order_document.
                // The backend should handle creating the full object.
                // The important part is the document_type_id.
                documentsToKeep.push({
                    document_type: docType,
                    document_type_id: docType.id,
                    current_status_rel: { name: 'Pending', id: 1 }, // Assuming 'Pending' status
                    file_path: null,
                    id: null // It's a new, unsaved document
                });
            }
        }
    });

    editOrder.value.documents = documentsToKeep;
});



// --- UI HELPERS ---
const formatDate = (dateString, options) => new Date(dateString).toLocaleDateString(undefined, options);
const getFileUrl = (filePath) => {
    const baseUrl = "http://localhost:8080";
    return `${baseUrl}/api/uploads/${filePath}`;
}

const getStatusClass = (statusName) => {
    const baseClass = 'badge';
    switch (statusName?.toLowerCase()) {
        case 'completed': return `${baseClass} bg-success`;
        case 'in progress': return `${baseClass} bg-primary`;
        case 'pending': return `${baseClass} bg-secondary`;
        case 'received': return `${baseClass} bg-info`;
        default: return `${baseClass} bg-dark`;
    }
};

const handleCommentsUpdated = () => {
    // Optionally re-fetch order details or update a comment count in OrderDetail.vue
    // For now, we'll just log that comments were updated.
    console.log('Comments updated in CommentsSidebar.');
    // If OrderDetail needs to react to comment changes, add logic here.
};

// --- API-CONNECTED MODAL LOGIC ---






const showCreateTaskModal = () => {
    newTask.value = {
        title: "",
        description: "",
        due_date: ""
    }
    modals.createTask.show();
};

const confirmCreateTask = async () => {
    if (!newTask.value.title || !newTask.value.due_date) {
        return alert.show('Title and Due Date are required.', 'warning');
    }
    try {
        const response = await fetchApi(`/api/orders/${orderId}/tasks`, {
            method: 'POST',
            body: JSON.stringify(newTask.value)
        });
        if (!response.ok) throw new Error((await response.json()).message);
        await fetchTasks(); // Refresh task list
        modals.createTask.hide();
        alert.show('Task created successfully!', 'success');
    } catch (e) {
        alert.show(e.message, 'danger');
    }
};

const toggleTaskCompletion = async (task) => {
    try {
        const response = await fetchApi(`/api/tasks/${task.id}`, {
            method: 'PUT',
            body: JSON.stringify({ is_completed: !task.is_completed })
        });
        if (!response.ok) throw new Error((await response.json()).message);
        await fetchTasks(); // Refresh task list
    } catch (e) {
        alert.show(e.message, 'danger');
    }
};

const showChangeStatusModal = () => {
    newStatusId.value = order.value.status.id;
    modals.changeStatus.show();
};
const confirmChangeStatus = async () => {
    try {
        const response = await fetchApi(`/api/orders/${orderId}`, {
            method: 'PUT',
            body: JSON.stringify({ status_id: newStatusId.value })
        });
        if (!response.ok) throw new Error((await response.json()).message);
        await fetchOrderDetails();
        modals.changeStatus.hide();
        alert.show('Order status updated!', 'success');
    } catch (e) {
        alert.show(e.message, 'error');
    }
};

const showAddRequiredDocModal = () => {
    docsToAdd.value = [];
    modals.addRequiredDoc.show();
};
const confirmAddRequiredDocs = async () => {
    const currentDocIds = order.value.order_type.required_documents.map(d => d.id);
    const newDocIds = [...docsToAdd.value];
    try {
        const response = await fetchApi(`/api/orders/${order.value.id}/add_documents`, {
            method: 'PUT',
            body: JSON.stringify({ required_document_ids: newDocIds })
        });
        if (!response.ok) throw new Error((await response.json()).message);
        await fetchOrderDetails();
        modals.addRequiredDoc.hide();
        alert.show('Required documents updated!', 'success');
    } catch (e) {
        alert.show(e.message, 'error');
    }
};

const showUploadModal = (doc) => {
    docToUpload.value = doc;
    uploadedFile.value = null;
    modals.upload.show();
};
const handleFileUpload = (event) => { uploadedFile.value = event.target.files[0]; };

const confirmUpload = async () => {
    if (!uploadedFile.value) return alert.show('Please select a file.', 'warning');
    const formData = new FormData();
    formData.append('file', uploadedFile.value);
    formData.append('document_type_id', docToUpload.value.document_type.id);
    try {
        const response = await fileUploadApi(`/api/orders/${orderId}/documents`, { method: 'POST', body: formData });
        if (!response.ok) throw new Error((await response.json()).message);
        await fetchOrderDetails();
        modals.upload.hide();
        alert.show(`Uploaded ${uploadedFile.value.name}!`, 'success');
    } catch (e) {
        alert.show(e.message, 'error');
    }
};

const showDeleteDocModal = (doc) => {
    docToDelete.value = doc;
    modals.deleteDoc.show();
};

const confirmDeleteDoc = async () => {
    if (!docToDelete.value) return;
    try {
        const response = await fetchApi(`/api/orders/${orderId}/documents/${docToDelete.value.id}`, {
            method: 'DELETE',
        });
        if (!response.ok) throw new Error((await response.json()).message || 'Failed to delete document.');
        await fetchOrderDetails(); // Refresh the order details
        modals.deleteDoc.hide();
        alert.show('Document deleted successfully!', 'success');
    } catch (e) {
        alert.show(e.message, 'danger');
    } finally {
        docToDelete.value = null;
    }
};

const showAddReceiptModal = () => {
    Object.assign(newReceipt, { description: '', amount: null });
    modals.addReceipt.show();
};
const showEditReceiptModal = (receipt) => {
    editingReceipt.value = JSON.parse(JSON.stringify(receipt));
    modals.editReceipt.show();
}
const showDeleteReceiptModal = (receipt) => {
    deleteReceipt.value = JSON.parse(JSON.stringify(receipt));
    modals.deleteReceipt.show();
}

const confirmAddReceipt = async () => {
    try {
        const response = await fetchApi(`/api/orders/${orderId}/receipts`, {
            method: 'POST', body: JSON.stringify(newReceipt)
        });
        if (!response.ok) throw new Error((await response.json()).message);
        await fetchOrderDetails();
        modals.addReceipt.hide();
        alert.show('Receipt added!', 'success');
    } catch (e) {
        alert.show(e.message, 'error');
    }
};


const confirmEditReceipt = async (editingReceipt) => {
    try {
        const response = await fetchApi(`/api/orders/${orderId}/receipts/${editingReceipt.id}`, {
            method: 'PUT',
            body: JSON.stringify(editingReceipt)
        })
        if (!response.ok) throw new Error((await response.json()).message);
        await fetchOrderDetails();
        modals.editReceipt.hide();
        alert.show('Receipt edited!', 'success');
    } catch (e) {
        alert.show(e.message, 'error');
    }
}

const confirmDeleteReceipt = async (deleteReceipt) => {
    try {
        const response = await fetchApi(`/api/orders/${orderId}/receipts/${deleteReceipt.id}`, {
            method: 'DELETE',
        })
        if (!response.ok) throw new Error((await response.json()).message);
        await fetchOrderDetails();
        modals.deleteReceipt.hide();
        alert.show('Receipt deleted!', 'success');
    } catch (e) {
        alert.show(e.message, 'error');
    }
}

const showAddExpenseModal = () => {
    Object.assign(newExpense, { description: '', amount: null });
    modals.addExpense.show();
};
const showEditExpenseModal = (expense) => {
    editingExpense.value = JSON.parse(JSON.stringify(expense));
    modals.editExpense.show();
}
const showDeleteExpenseModal = (expense) => {
    deleteExpense.value = JSON.parse(JSON.stringify(expense));
    modals.deleteExpense.show();
}

const confirmAddExpense = async () => {
    try {
        const response = await fetchApi(`/api/orders/${orderId}/expenses`, {
            method: 'POST', body: JSON.stringify(newExpense)
        });
        if (!response.ok) throw new Error((await response.json()).message);
        await fetchOrderDetails();
        modals.addExpense.hide();
        alert.show('Expense added!', 'success');
    } catch (e) {
        alert.show(e.message, 'error');
    }
};

const confirmEditExpense = async (editingExpense) => {
    try {
        const response = await fetchApi(`/api/orders/${orderId}/expenses/${editingExpense.id}`, {
            method: 'PUT',
            body: JSON.stringify(editingExpense)
        })
        if (!response.ok) throw new Error((await response.json()).message);
        await fetchOrderDetails();
        modals.editExpense.hide();
        alert.show('Expense edited!', 'success');
    } catch (e) {
        alert.show(e.message, 'error');
    }
}

const confirmDeleteExpense = async (deleteExpense) => {
    try {
        const response = await fetchApi(`/api/orders/${orderId}/expenses/${deleteExpense.id}`, {
            method: 'DELETE',
        })
        if (!response.ok) throw new Error((await response.json()).message);
        await fetchOrderDetails();
        modals.deleteExpense.hide();
        alert.show('Expense deleted!', 'success');
    } catch (e) {
        alert.show(e.message, 'error');
    }
}


const triggerSettlement = async () => {
    try {
        const response = await fetchApi(`/api/orders/${orderId}/settle`, { method: 'POST' });
        if (!response.ok) throw new Error((await response.json()).message);
        await fetchOrderDetails();
        alert.show('Settlement created successfully!', 'success');
    } catch (e) {
        alert.show(e.message, 'error');
    }
};

const showDocStatusModal = () => {
    documentsForStatusChange.value = JSON.parse(JSON.stringify(order.value.documents));
    modals.docStatus.show();
}

const confirmChangeDocumentStatus = async () => {
    const documents = documentsForStatusChange.value.map(doc => ({
        document_id: doc.id,
        status_id: doc.current_status_rel.id
    }));

    try {
        const response = await fetchApi(`/api/orders/${orderId}/documents/statuses`, {
            method: 'PUT',
            body: JSON.stringify(documents)
        });
        if (!response.ok) throw new Error((await response.json()).message);
        await fetchOrderDetails();
        modals.docStatus.hide();
        alert.show('Document statuses updated!', 'success');
    } catch (e) {
        alert.show(e.message, 'error');
    }
};

const showDeleteOrderModal = (order) => {
    orderToDelete.value = JSON.parse(JSON.stringify(order))
    modals.deleteOrder.show();
}

const confirmEditOrder = async () => {
    try {
        const response = await fetchApi(`/api/orders/${orderId}`, {
            method: 'PUT',
            body: JSON.stringify(editOrder.value)
        });
        if (!response.ok) throw new Error((await response.json()).message);
        await fetchOrderDetails();
        modals.editOrder.hide();
        alert.show('Order updated successfully!', 'success');
    } catch (e) {
        alert.show(e.message, 'danger');
    }
};

const showEditOrderModal = () => {
    const orderCopy = JSON.parse(JSON.stringify(order.value));

    // Extract IDs for easier v-model binding and ensure they exist
    orderCopy.client_id = orderCopy.client?.id || null;
    orderCopy.partner_id = orderCopy.partner?.id || null;
    orderCopy.company_id = orderCopy.company?.id || null;
    orderCopy.order_type_id = orderCopy.order_type?.id || null;

    // Remove the original objects to avoid confusion in the form
    delete orderCopy.client;
    delete orderCopy.partner;
    delete orderCopy.company;
    delete orderCopy.order_type;

    editOrder.value = orderCopy;
    modals.editOrder.show();
};

const viewDocumentFile = async (filePath) => {
    try {
        // Just fetch the head to check existence without downloading
        const response = await fetchApi(`/api/uploads/${filePath}`, { method: 'HEAD' });
        if (response.ok) {
            window.open(getFileUrl(filePath), '_blank');
        } else {
            // The fetchApi utility already handles showing a generic error modal for !response.ok,
            // but for a specific case like file not found, we can provide a more tailored message
            // if the backend response includes one.
            let errorMessage = 'File not found.';
            try {
                const errorData = await response.json();
                errorMessage = errorData.message || errorMessage;
            } catch (e) {
                // If not JSON, use default
            }
            alert.show(errorMessage, 'error');
        }
    } catch (error) {
        // fetchApi already handles displaying network errors in the error modal.
        // We can optionally add a specific alert here if needed, but it might duplicate.
        // For now, let fetchApi manage the primary error display.
        console.error("Error viewing document file:", error);
    }
};

</script>

<style scoped>
.order-detail-page-wrapper {
    position: relative;
    padding-right: 50px;
    /* Space for the collapsed toggle */
}

.btn {
    min-width: 70px;
}
</style>
