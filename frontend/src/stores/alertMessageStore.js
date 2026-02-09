import { defineStore } from 'pinia'

export const useAlertStore = defineStore('alert', {
    state: () => ({
        message: '',
        type: 'success', // success | error | warning | info
        visible: false,
        timeoutId: null,
    }),

    actions: {
        show(message, type = 'success', duration = 5000) {
            this.message = message
            this.type = type
            const audio = new Audio('/notification.mp3')
            audio.play().catch(e => console.error("Error playing sound: ", e));

            this.visible = true

            if (this.timeoutId) {
                clearTimeout(this.timeoutId)
            }

            this.timeoutId = setTimeout(() => {
                this.clear()
            }, duration)
        },

        clear() {
            this.visible = false
            this.message = ''
            this.timeoutId = null
        },
    },
})
