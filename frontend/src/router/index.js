import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import Partners from '@/views/Partners.vue'
import NewPartner from '@/views/NewPartner.vue'
import Clients from '@/views/Clients.vue'
import NewClient from '@/views/NewClient.vue'
import ManageResources from '@/views/ManageResources.vue'

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
            name: 'newPartner',
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
        {
            path: '/manage-resources',
            name: 'manageResources',
            component: ManageResources
        },
        {
            path: '/document-types',
            name: 'documentTypes',
            component: ManageResources
        },
        {
            path: '/order-types',
            name: 'orderTypes',
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
        },
        {
            path: '/orders',
            name: 'orders',
        },
        {
            path: '/orders/:orderId',
            name: 'orderDetails',
        },
        {},
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
