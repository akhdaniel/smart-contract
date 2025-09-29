import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_ODOO_URL,
});

export default api;