// src/stores/sidebarStore.js
import { defineStore } from 'pinia'

const STORAGE_KEY = 'sidebar-state'

export const useSidebarStore = defineStore('sidebar', {
    state: () => {
        const saved = sessionStorage.getItem(STORAGE_KEY)

        return {
            isCollapsed: saved === 'false' ? false : true,
        }
    },

    getters: {
        sidebarClass: (state) =>
            state.isCollapsed ? 'collapsed' : 'expanded',
    },

    actions: {
        toggleSidebar() {
            this.isCollapsed = !this.isCollapsed
            sessionStorage.setItem(STORAGE_KEY, this.isCollapsed)
        },

        expandIfCollapsed() {
            if (this.isCollapsed) {
                this.isCollapsed = false
                sessionStorage.setItem(STORAGE_KEY, this.isCollapsed)
            }
        },
    },
})
