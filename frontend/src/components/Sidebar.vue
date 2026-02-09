<template>
    <div :class="store.sidebarClass" class="sidebar flex-shrink-0 p-3">
        <button class="toggle-sidebar" @click="store.toggleSidebar">
            <i class="bi bi-list"></i>
            <span class="collapse-btn-text">Dash</span>
        </button>



        <!-- Navigation -->
        <nav class="mt-3">
            <router-link class="sidebar-link rounded border-0" to="/">
                <i class="bi bi-house-door"></i>
                <span class="menu-text">Dashboard</span>
            </router-link>
            
            <!-- Dashboard -->
            <div class="menu-header">
                <span class="menu-text">Main</span>
            </div>

            <!-- Partners Menu -->
            <ul class="list-unstyled ps-0">
                <li> 
                    <a href="#" class="sidebar-link rounded border-0 collapsed" role="button" @click="store.expandIfCollapsed" data-bs-toggle="collapse"
                        data-bs-target="#partners-collapse" aria-expanded="false">
                        <i class="bi bi-person-vcard"></i>
                        <span class="menu-text">Partners</span>
                        <i class="bi bi-chevron-down collapse-icon menu-text"></i>
                    </a>
                    <div class="collapse submenu" id="partners-collapse" style="">
                        <ul class="list-unstyled fw-normal small">
                            <li>
                                <router-link to="/partners" class="sidebar-link">
                                    <i class="bi bi-people-fill"></i>
                                    <span class="menu-text">All Partners</span>
                                </router-link>
                            </li>
                            <li><router-link to="/new-partner" class="sidebar-link">
                                    <i class="bi bi-person-fill-add"></i>
                                    <span class="menu-text">New Partner</span>
                                </router-link>
                            </li>
                        </ul>
                    </div>
                </li>
            </ul>

            <!-- Client Menu -->
            <ul class="list-unstyled ps-0">
                <li class="mb-1">
                    <a href="#" class="sidebar-link rounded border-0 collapsed" role="button"
                        @click="store.expandIfCollapsed" data-bs-toggle="collapse" data-bs-target="#clients-collapse"
                        aria-expanded="false">
                        <i class="bi bi-people"></i>
                        <span class="menu-text">Clients</span>
                        <i class="bi bi-chevron-down collapse-icon menu-text"></i>
                    </a>
                    <div class="collapse submenu" id="clients-collapse" style="">
                        <ul class="list-unstyled fw-normal pb-1 small">
                            <li>
                                <router-link to="/clients" class="sidebar-link">
                                    <i class="bi bi-people"></i>
                                    <span class="menu-text">Existing Clients</span>
                                </router-link>
                                
                            </li>
                            <li>
                                <router-link to="/new-client" class="sidebar-link">
                                    <i class="bi bi-person-add"></i>
                                    <span class="menu-text">New Client</span>
                                </router-link>
                            </li>
                        </ul>
                    </div>
                </li>
            </ul>

            <!-- Oders Menu -->
            <ul class="list-unstyled ps-0">
                <li class="mb-1">
                    <a href="#" class="sidebar-link rounded border-0 collapsed" role="button"
                        @click="store.expandIfCollapsed" data-bs-toggle="collapse" data-bs-target="#orders-collapse"
                        aria-expanded="false">
                        <i class="bi bi-cart-fill"></i>
                        <span class="menu-text">Orders</span>
                        <i class="bi bi-chevron-down collapse-icon menu-text"></i>
                    </a>
                    <div class="collapse submenu" id="orders-collapse" style="">
                        <ul class="list-unstyled fw-normal pb-1 small">
                            <li>
                                <router-link to="/orders" class="sidebar-link">
                                    <i class="bi bi-cart-check-fill"></i>
                                    <span class="menu-text">Active Orders</span>
                                </router-link>
                            </li>
                            <li>
                                <router-link to="/all-orders" class="sidebar-link">
                                    <i class="bi bi-cart-check-fill"></i>
                                    <span class="menu-text">All Orders</span>
                                </router-link>
                            </li>
                            <li>
                                <router-link to="/new-order" class="sidebar-link">
                                    <i class="bi bi-cart-plus-fill"></i>
                                    <span class="menu-text">New Order</span>
                                </router-link>
                            </li>
                        </ul>
                    </div>
                </li>
            </ul>
            

            <!-- Reports Menu -->
            <div class="menu-header mt-3">
                <span class="menu-text">Analytics</span>
            </div>
            
            <ul class="list-unstyled ps-0">
                <li class="mb-1">
                    <a href="#" class="sidebar-link rounded border-0 collapsed" role="button"
                        @click="store.expandIfCollapsed" data-bs-toggle="collapse" data-bs-target="#reports-collapse"
                        aria-expanded="false">
                        <i class="bi bi-graph-up"></i>
                        <span class="menu-text">Reports</span>
                        <i class="bi bi-chevron-down collapse-icon menu-text"></i>
                    </a>
                    <div class="collapse submenu" id="reports-collapse" style="">
                        <ul class="list-unstyled fw-normal pb-1 small">
                            <li>
                                <router-link to="/reports" class="sidebar-link">
                                    <i class="bi bi-circle"></i>
                                    <span class="menu-text">Revenue Reports</span>
                                </router-link>
                            </li>
                        </ul>
                    </div>
                </li>
            </ul>
            <!-- Settings Menu -->
            <div class="menu-header mt-3">
                <span class="menu-text">Settings</span>
            </div>

            <ul class="list-unstyled ps-0">
                <li class="mb-1">
                    <a href="#" class="sidebar-link rounded border-0 collapsed" role="button"
                        @click="store.expandIfCollapsed" data-bs-toggle="collapse" data-bs-target="#settings-collapse"
                        aria-expanded="false">
                        <i class="bi bi-bounding-box"></i>
                        <span class="menu-text">Manage Resources</span>
                        <i class="bi bi-chevron-down collapse-icon menu-text"></i>
                    </a>
                    <div class="collapse submenu" id="settings-collapse" style="">
                        <ul class="list-unstyled fw-normal pb-1 small">
                            <li>
                                <router-link to="/document-types" class="sidebar-link">
                                    <i class="bi bi-file-earmark-diff"></i>
                                    <span class="menu-text">Document Types</span>
                                </router-link>
                            </li>
                            <li>
                                <router-link to="/order-types" class="sidebar-link">
                                    <i class="bi bi-receipt"></i>
                                    <span class="menu-text">Order Types</span>
                                </router-link>
                            </li>
                            <li>
                                <router-link to="/order-status" class="sidebar-link">
                                    <i class="bi bi-receipt"></i>
                                    <span class="menu-text">Order Status</span>
                                </router-link>
                            </li>
                            <li>
                                <router-link to="/registrars" class="sidebar-link">
                                    <i class="bi bi-journal-text"></i>
                                    <span class="menu-text">Registrars</span>
                                </router-link>
                            </li>
                            <li>
                                <router-link to="/companies" class="sidebar-link">
                                    <i class="bi bi-buildings"></i>
                                    <span class="menu-text">Companies</span>
                                </router-link>
                            </li>
                        </ul>
                    </div>
                </li>
            </ul>
            
        </nav>
    </div>
</template>

<script setup>
import { ref } from 'vue';
import { useSidebarStore } from '@/stores/sidebarStore';

const store = useSidebarStore();

</script>

<style scoped>
.sidebar {
    min-height: 100vh;
    transition: width 0.3s ease;
    background-color: #212529;
    overflow: hidden;
    white-space: nowrap;
    color: antiquewhite;
}

.sidebar.collapsed {
    width: 80px;
}

.sidebar.expanded {
    width: 280px;
}

.sidebar.collapsed .menu-text,
.sidebar.collapsed .collapse-btn-text {
    display: none;
}

.sidebar.collapsed .submenu {
    display: none !important;
}

.sidebar-link {
    color: rgba(255, 255, 255, 0.75);
    text-decoration: none;
    padding: 0.25rem 0.25rem;
    display: flex;
    align-items: center;
    transition: all 0.2s;
}

.sidebar-link:hover {
    background-color: rgba(255, 255, 255, 0.1);
    color: #fff;
    cursor: pointer;
}

.sidebar-link i {
    width: 24px;
    margin-right: 0.5rem;
    font-size: 1.2rem;
}

.sidebar.collapsed .sidebar-link i {
    margin-right: 0;
}

.sidebar.collapsed .sidebar-link {
    justify-content: center;
}

.submenu a{
    padding: 0.75rem 2rem !important;
    font-size: 13px !important;
    font-weight: 500;
    background-color: rgba(0, 0, 0, 0.2);
    overflow: hidden;
}

.submenu i{
    font-size: 14px !important;
}


/* .submenu .sidebar-link {
    padding-left: 3rem;
    font-size: 0.9rem;
} */


.toggle-sidebar {
    background-color: #212529;
    /* background-color: rgba(255, 255, 255, 0.1); */
    border: none;
    color: #fff;
    width: 100%;
    padding: 1rem;
    display: flex;
    align-items: center;
    justify-content: flex-start;
    transition: all 0.2s;
}

.toggle-sidebar:hover {
    background-color: rgba(255, 255, 255, 0.2);
}

.toggle-sidebar i {
    width: 24px;
    margin-right: 0.75rem;
    font-size: 1.2rem;
}

.sidebar.collapsed .toggle-sidebar {
    justify-content: center;
}

.sidebar.collapsed .toggle-sidebar i {
    margin-right: 0;
}

.content {
    flex: 1;
    padding: 2rem;
    transition: margin-left 0.3s;
}

.menu-header {
    color: rgba(255, 255, 255, 0.5);
    font-size: 0.75rem;
    text-transform: uppercase;
    padding: 1rem 1rem 0.5rem;
    letter-spacing: 0.05em;
}

.sidebar.collapsed .menu-header {
    text-align: center;
    padding: 1rem 0 0.5rem;
}

.collapse-icon {
    margin-left: auto;
    transition: transform 0.3s;
}

.sidebar-link[aria-expanded="true"] .collapse-icon {
    transform: rotate(180deg);
}

.alert {
    transition: opacity 0.5s ease-in-out;
}


.scrollarea {
    overflow-y: auto;
}
</style>
