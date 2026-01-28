
import router from '@/router/index.js'

const API_BASE_URL = 'http://localhost:8000' // Change this to your backend URL

async function fetchApi(endpoint, options = {}) {
	try {
		const defaultHeaders = {
			'Content-Type': 'application/json',
		}
		const newOptions = { ...options, headers: { ...defaultHeaders, ...options.headers } }

		let response = await fetch(`${API_BASE_URL}${endpoint}`, newOptions)

		if (response.status === 401) {
			console.log('Issue with attempt')
			router.push({ name: 'Home' })
		}
		return response
	} catch (error) {
		console.error('Error in fetchWithAuth:', error)
		throw error // Propagate error so the caller can handle it
	}
}

export default fetchApi
