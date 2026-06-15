import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

const API_BASE = 'https://api.freightgpt.ae';

const api = axios.create({
  baseURL: `${API_BASE}/api/v1`,
  timeout: 15000,
});

api.interceptors.request.use(async (config) => {
  const token = await AsyncStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      await AsyncStorage.removeItem('access_token');
      await AsyncStorage.removeItem('refresh_token');
    }
    return Promise.reject(error);
  },
);

export const authApi = {
  login: (email: string, password: string) =>
    api.post('/auth/login', { email, password }),
  me: () => api.get('/auth/me'),
};

export const tripsApi = {
  current: () => api.get('/loads', { params: { status: 'in_transit' } }),
  updateStatus: (id: string, status: string) =>
    api.patch(`/loads/${id}/status`, { status }),
};

export const documentsApi = {
  upload: (formData: FormData) =>
    api.post('/documents/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
  list: () => api.get('/documents'),
};

export const trackingApi = {
  updateLocation: (loadId: string, lat: number, lng: number) =>
    api.post(`/loads/${loadId}/tracking`, {
      latitude: lat,
      longitude: lng,
      event_type: 'location_update',
      status: 'in_transit',
    }),
};

export default api;
