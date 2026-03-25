import axios from 'axios';
import { useAuthStore } from '@/stores/auth';
import { useLoadingStore } from '@/stores/loading';

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_ODOO_URL,
  headers: {
    'Content-Type': 'application/json',
  }
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