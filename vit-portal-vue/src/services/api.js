import axios from 'axios';
import { useAuthStore } from '@/stores/auth';
import { useLoadingStore } from '@/stores/loading';

const apiClient = axios.create({
  // Untuk development dengan Vite proxy: cocokkan URL ke proxy prefix (path relatif)
  // di .env.local (misal VITE_ODOO_URL=/web) atau default fallback '/web'.
  baseURL: import.meta.env.VITE_ODOO_URL || '/web',
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
});

let loadingTimer = null;

apiClient.interceptors.request.use(config => {
  const authStore = useAuthStore();
  const loadingStore = useLoadingStore();

  // Set a timer to show the loading screen after 3 seconds
  loadingTimer = setTimeout(() => {
    loadingStore.setLoading(true);
  }, 3000);

  if (authStore.sessionId) {
    // Odoo uses session_id in the request data, not headers
    // config.headers.Authorization = `Bearer ${authStore.sessionId}`;
  }
  return config;
}, error => {
  clearTimeout(loadingTimer);
  const loadingStore = useLoadingStore();
  loadingStore.setLoading(false);
  return Promise.reject(error);
});

apiClient.interceptors.response.use(response => {
  clearTimeout(loadingTimer);
  const loadingStore = useLoadingStore();
  loadingStore.setLoading(false);
  return response;
}, error => {
  clearTimeout(loadingTimer);
  const loadingStore = useLoadingStore();
  loadingStore.setLoading(false);
  return Promise.reject(error);
});

export default apiClient;