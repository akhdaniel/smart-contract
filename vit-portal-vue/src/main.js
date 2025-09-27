import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'
import api from './services/api'
import { useAuthStore } from './stores/auth'

import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap/dist/js/bootstrap.bundle.min.js'
import './assets/main.css'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)

const authStore = useAuthStore(pinia)

api.interceptors.response.use(
  response => {
    const error = response.data.error;
    if (error && (error.message === 'Odoo Session Expired' || (error.data && error.data.message === 'Session expired'))) {
      authStore.logout();
      router.push({ name: 'login' });
      return Promise.reject(error);
    }
    return response;
  },
  error => {
    const responseError = error.response && error.response.data && error.response.data.error;
    if (responseError && (responseError.message === 'Odoo Session Expired' || (responseError.data && responseError.data.message === 'Session expired'))) {
      authStore.logout();
      router.push({ name: 'login' });
    }
    return Promise.reject(error);
  }
);

app.mount('#app')
