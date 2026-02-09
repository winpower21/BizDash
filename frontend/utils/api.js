
import router from '@/router/index.js'

const API_BASE_URL = 'http://localhost:8080' // Change this to your backend URL

async function fetchApi(endpoint, options = {}) {
	try {
        
        const defaultHeaders = {
            'Content-Type': 'application/json',
        }
		const newOptions = { ...options, headers: {...defaultHeaders, ...options.headers}};

		let response = await fetch(`${API_BASE_URL}${endpoint}`, newOptions);

		if (response.status === 401) {
			console.log('Unauthorized or expired token, redirecting to home.');
			router.push({ name: 'Home' });
		}
		return response;
	} catch (error) {
		console.error('Error in fetchApi:', error);
		throw error; // Propagate error so the caller can handle it
	}
}

async function fetchBatchData(urls) {
    const response = await Promise.allSettled(
        urls.map(url => fetchApi(url, { method: 'GET' }))
    );

    const data = await Promise.all(response.map(async (res) => {
        if (res.status === 'fulfilled' && res.value.ok) {
            try {
                return await res.value.json();
            } catch (e) {
                console.error("JSON Parse Error for request:", e);
                return null;
            }
        }
        if (res.status === 'rejected') {
            console.warn('Network error:', res.reason)
        } else {
            console.warn("HTTP Error: ", res.value?.status)
        }
        return null;
    }));

    return data
}


export { fetchApi, fetchBatchData }
