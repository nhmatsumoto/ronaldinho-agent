import axios from 'axios';

// Create a configured instance of Axios
const apiClient = axios.create({
    baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api', // Uses env var or defaults to local NeuralCore
    headers: {
        'Content-Type': 'application/json',
    },
    timeout: 10000,
});

const authAuthority = import.meta.env.VITE_AUTH_AUTHORITY || "http://localhost:8080/realms/ronaldinho";
const authClientId = import.meta.env.VITE_AUTH_CLIENT_ID || "configui-client";
const storageKey = `oidc.user:${authAuthority}:${authClientId}`;

// Configure Request Interceptors
apiClient.interceptors.request.use(
    (config) => {
        const oidcStorage = sessionStorage.getItem(storageKey);
        if (oidcStorage) {
            try {
                const user = JSON.parse(oidcStorage);
                if (user && user.access_token) {
                    config.headers.Authorization = `Bearer ${user.access_token}`;
                }
            } catch (e) {
                console.error("Failed to parse OIDC session storage token", e);
            }
        }
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
