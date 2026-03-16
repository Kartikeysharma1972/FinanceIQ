import axios from 'axios'
import { getStoredAuth } from './auth'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add auth token to requests
api.interceptors.request.use((config) => {
  const auth = getStoredAuth()
  if (auth.token) {
    config.headers.Authorization = `Bearer ${auth.token}`
  }
  return config
})

export const workflowsApi = {
  list: () => api.get('/api/workflows'),
  get: (id: string) => api.get(`/api/workflows/${id}`),
  create: (data: any) => api.post('/api/workflows', data),
  update: (id: string, data: any) => api.put(`/api/workflows/${id}`, data),
  delete: (id: string) => api.delete(`/api/workflows/${id}`),
  activate: (id: string) => api.post(`/api/workflows/${id}/activate`),
  pause: (id: string) => api.post(`/api/workflows/${id}/pause`),
}

export const executionsApi = {
  list: (params?: any) => api.get('/api/executions', { params }),
  get: (id: string) => api.get(`/api/executions/${id}`),
  trigger: (data: any) => api.post('/api/executions/trigger', data),
  cancel: (id: string) => api.post(`/api/executions/${id}/cancel`),
  getLogs: (id: string) => api.get(`/api/executions/${id}/logs`),
}

export const agentsApi = {
  list: () => api.get('/api/agents'),
  get: (name: string) => api.get(`/api/agents/${name}`),
  execute: (name: string, task: any) => api.post(`/api/agents/${name}/execute`, task),
}

export const toolsApi = {
  list: () => api.get('/api/tools'),
  get: (name: string) => api.get(`/api/tools/${name}`),
  execute: (data: any) => api.post('/api/tools/execute', data),
}

export const memoryApi = {
  store: (data: any) => api.post('/api/memory/store', data),
  search: (data: any) => api.post('/api/memory/search', data),
  stats: () => api.get('/api/memory/stats'),
  delete: (id: string) => api.delete(`/api/memory/${id}`),
}

export const authApi = {
  signup: (data: { email: string; password: string; name: string }) => 
    api.post('/api/auth/signup', data),
  login: (data: { email: string; password: string }) => 
    api.post('/api/auth/login', data),
  getMe: (token: string) => 
    api.get('/api/auth/me', { params: { token } }),
}

export default api
