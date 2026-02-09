import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import Partners from '@/views/Partners.vue'
import NewPartner from '@/views/NewPartner.vue'
import Clients from '@/views/Clients.vue'
import NewClient from '@/views/NewClient.vue'
import ManageResources from '@/views/ManageResources.vue'
import NewOrder from '@/views/NewOrder.vue'
import Orders from '@/views/Orders.vue'
import OrderDetail from '@/views/OrderDetail.vue'
import Reports from '@/views/Reports.vue'
import { useAlertStore } from '@/stores/alertMessageStore'
import {fetchApi} from '../../utils/api'
import AllOrders from '@/views/AllOrders.vue'

// This guard function checks if all prerequisites for creating an order exist.
const checkOrderPrerequisites = async () => {
    const prerequisites = {
        Client: '/api/clients',
        Partner: '/api/partners',
        Company: '/api/companies',
        Registrar: '/api/registrars',
        'Order Type': '/api/order-types',
        'Order Status': '/api/order-status',
    };
    const missing = [];
    for (const [name, endpoint] of Object.entries(prerequisites)) {
        try {
            const response = await fetchApi(endpoint);
            // The API returns 404 if the list is empty, which we can treat as a failed prerequisite
            if (!response.ok) {
                 missing.push(name);
                 continue;
            }
            const data = await response.json();
            if (!data || data.length === 0) {
                missing.push(name);
            }
        } catch (e) {
            missing.push(name); // Assume missing if API call fails
        }
    }
    return missing;
};


const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: [
        {
            path: '/',
            name: 'home',
            component: HomeView,
        },
        {
            path: '/partners',
            name: 'partners',
            component: Partners,
        },
        {
            path: '/new-partner',
            name: 'new-partner',
            component: NewPartner,
        },
        {
            path: '/clients',
            name: 'clients',
            component: Clients,
        },
        {
            path: '/clients/:clientId',
            name: 'client-details',
        },
        {
            path: '/new-client',
            name: 'new-client',
            component: NewClient
        },
        // {
        //     path: '/manage-resources',
        //     name: 'manage-resources',
        //     component: ManageResources
        // },
        {
            path: '/document-types',
            name: 'document-types',
            component: ManageResources
        },
        {
            path: '/order-types',
            name: 'order-types',
            component: ManageResources
        },
        {
            path: '/order-status',
            name: 'order-status',
            component: ManageResources
        },
        {
            path: '/companies',
            name: 'companies',
            component: ManageResources
        },
        {
            path: '/registrars',
            name: 'registrars',
            component: ManageResources
        },
        {
            path: '/orders',
            name: 'orders',
            component: Orders
        },
        {
            path: '/all-orders',
            name: 'allOrders',
            component: AllOrders
        },
        {
            path: '/new-order',
            name: 'new-order',
            component: NewOrder,
            beforeEnter: async (to, from, next) => {
                const alert = useAlertStore();
                const missing = await checkOrderPrerequisites();
                if (missing.length > 0) {
                    alert.show(`Cannot create a new order. Missing resources: ${missing.join(', ')}.`, 'warning');
                    next({ name: 'orders' }); // Redirect back to orders page
                } else {
                    next(); // Proceed to the new order page
                }
            },
        },
        {
            path: '/orders/:id',
            name: 'order-details',
            component: OrderDetail,
        },
        {
            path: '/reports',
            name: 'reports',
            component: Reports,
        },
    ],
})

router.beforeResolve(async (to, from) => {
    if (!document.startViewTransition) return

    return new Promise((resolve) => {
        document.startViewTransition(async () => {
            resolve() // Navigates to the new page
            await new Promise((r) => setTimeout(r, 0)) // Ensures DOM is ready
        })
    })
})

export default router
