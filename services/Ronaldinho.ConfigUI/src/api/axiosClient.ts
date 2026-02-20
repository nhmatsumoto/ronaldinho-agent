import axios from 'axios';

// Create a configured instance of Axios
const apiClient = axios.create({
    baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api', // Uses env var or defaults to local NeuralCore
    headers: {
        'Content-Type': 'application/json',
    },
    timeout: 10000,
});

// Configure Request Interceptors
apiClient.interceptors.request.use(
    (config) => {
        // You could inject auth tokens here before the request is sent
        // const token = localStorage.getItem('token');
        // if (token) {
        //   config.headers.Authorization = `Bearer ${token}`
        // }
        return config;
    },
    (error) => Promise.reject(error)
);

// Configure Response Interceptors
apiClient.interceptors.response.use(
    (response) => {
        // Any status code that lie within the range of 2xx cause this function to trigger
        return response;
    },
    (error) => {
        // Any status codes that falls outside the range of 2xx cause this function to trigger
        console.error('API Error:', error.response || error.message);

        // Check for specific error codes
        if (error.response?.status === 401) {
            // Handle unauthorized errors (e.g., redirect to login)
            console.warn('Unauthorized access. Please login.');
        }

        return Promise.reject(error);
    }
);

export default apiClient;
