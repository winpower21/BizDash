import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import Partners from '@/views/Partners.vue'
import NewPartner from '@/views/NewPartner.vue'

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
        },
        {
            path: '/clients/:clientId',
            name: 'client-details',
        },
        {
            path: '/new-client',
            name: 'new-client',
        },
        {
            path: '/companies',
            name: 'companies',
        },
        {
            path: '/registrars',
            name: 'registrars',
        },
        {
            path: '/document-types',
            name: 'document-types',
        },
        {
            path: '/document-types',
            name: 'document-types',
        },
        {
            path: '/order-types',
            name: 'order-types',
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
