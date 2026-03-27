// src/services/api.js
import axios from 'axios'
 
const api = axios.create({
  // Em desenvolvimento local: 'http://127.0.0.1:8000/api/'
  // Com Docker + Nginx: '/api/'  (o Nginx faz o proxy)
  baseURL: import.meta.env.VITE_API_URL || '/api/',
  headers: { 'Content-Type': 'application/json' },
})
 
export default api

