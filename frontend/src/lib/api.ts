import axios from 'axios'

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export const api = axios.create({
  baseURL: `${API_BASE}/api/v1`,
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.request.use((config) => {
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      try {
        const refreshToken = localStorage.getItem('refresh_token')
        const { data } = await axios.post(`${API_BASE}/api/v1/auth/refresh`, null, {
          headers: { Authorization: `Bearer ${refreshToken}` },
        })
        localStorage.setItem('access_token', data.access_token)
        originalRequest.headers.Authorization = `Bearer ${data.access_token}`
        return api(originalRequest)
      } catch {
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        if (typeof window !== 'undefined') {
          window.location.href = '/auth/login'
        }
      }
    }
    return Promise.reject(error)
  }
)

export const auth = {
  login: (email: string, password: string) =>
    api.post('/auth/login', { email, password }),
  register: (data: { email: string; password: string; full_name: string }) =>
    api.post('/auth/register', data),
  me: () => api.get('/auth/me'),
}

export const loads = {
  list: (params?: { page?: number; status?: string }) =>
    api.get('/loads', { params }),
  get: (id: string) => api.get(`/loads/${id}`),
  create: (data: any) => api.post('/loads', data),
  updateStatus: (id: string, status: string) =>
    api.patch(`/loads/${id}/status`, { status }),
}

export const fleet = {
  trucks: {
    list: () => api.get('/fleet/trucks'),
    get: (id: string) => api.get(`/fleet/trucks/${id}`),
    create: (data: any) => api.post('/fleet/trucks', data),
    updateLocation: (id: string, lat: number, lng: number) =>
      api.put(`/fleet/trucks/${id}/location`, { lat, lng }),
  },
  drivers: {
    list: () => api.get('/fleet/drivers'),
    create: (data: any) => api.post('/fleet/drivers', data),
  },
}

export const agents = {
  run: (agentType: string, inputData: any) =>
    api.post('/agents/run', { agent_type: agentType, input_data: inputData }),
  workflow: (name: string, data: any) =>
    api.post(`/agents/workflow/${name}`, data),
  runs: (limit?: number) => api.get('/agents/runs', { params: { limit } }),
  getRun: (id: string) => api.get(`/agents/runs/${id}`),
  pricing: (data: any) => api.post('/agents/pricing/calculate', data),
  marketIntelligence: (query: string) =>
    api.post('/agents/market-intelligence', { query }),
}

export const documents = {
  list: (params?: { load_id?: string; doc_type?: string }) =>
    api.get('/documents', { params }),
  upload: (formData: FormData) =>
    api.post('/documents/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
  process: (id: string) => api.post(`/documents/${id}/process`),
  get: (id: string) => api.get(`/documents/${id}`),
}

export const finance = {
  invoices: {
    list: () => api.get('/finance/invoices'),
    get: (id: string) => api.get(`/finance/invoices/${id}`),
    create: (data: any) => api.post('/finance/invoices', data),
  },
  payments: {
    create: (data: any) => api.post('/finance/payments', data),
  },
  payouts: {
    list: () => api.get('/finance/payouts'),
    create: (data: any) => api.post('/finance/payouts', data),
  },
  transactions: {
    list: () => api.get('/finance/transactions'),
  },
  profitAnalysis: (period?: string) =>
    api.get('/finance/profit-analysis', { params: { period } }),
}

export const communications = {
  email: (data: any) => api.post('/communications/email', data),
  whatsapp: (data: any) => api.post('/communications/whatsapp', data),
  voiceCall: (data: any) => api.post('/communications/voice/call', data),
  history: (params?: { channel?: string; limit?: number }) =>
    api.get('/communications/history', { params }),
}

export const analytics = {
  dashboard: () => api.get('/analytics/dashboard'),
  loadsTimeline: (days?: number) =>
    api.get('/analytics/loads/timeline', { params: { days } }),
  revenueTimeline: (days?: number) =>
    api.get('/analytics/revenue/timeline', { params: { days } }),
  fleetStatus: () => api.get('/analytics/fleet/status'),
}
