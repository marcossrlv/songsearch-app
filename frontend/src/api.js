import axios from 'axios';

const api = axios.create({
  baseURL: 'http://127.0.0.1:5001', // Base URL para todas las peticiones
});

export default api;
