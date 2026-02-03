import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios'
import { useAuthStore } from '../store/authStore'

const API_URL = import.meta.env.VITE_API_URL || '/api'

export const api = axios.create({
  baseURL: API_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = useAuthStore.getState().token
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error: AxiosError) => {
    return Promise.reject(error)
  }
)

api.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      useAuthStore.getState().logout()
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export const endpoints = {
  auth: {
    login: '/auth/telegram',
    logout: '/auth/logout',
    me: '/auth/me',
    refresh: '/auth/refresh',
  },
  alerts: {
    list: '/alerts',
    create: '/alerts',
    get: (id: string) => `/alerts/${id}`,
    update: (id: string) => `/alerts/${id}`,
    delete: (id: string) => `/alerts/${id}`,
    toggle: (id: string) => `/alerts/${id}/toggle`,
  },
  prices: {
    list: '/prices',
    get: (symbol: string) => `/prices/${symbol}`,
    history: (symbol: string) => `/prices/${symbol}/history`,
    search: '/prices/search',
  },
  portfolio: {
    get: '/portfolio',
    holdings: '/portfolio/holdings',
    addHolding: '/portfolio/holdings',
    updateHolding: (id: string) => `/portfolio/holdings/${id}`,
    removeHolding: (id: string) => `/portfolio/holdings/${id}`,
  },
  dashboard: {
    stats: '/dashboard/stats',
    activity: '/dashboard/activity',
  },
  user: {
    profile: '/user/profile',
    settings: '/user/settings',
    updateSettings: '/user/settings',
  },
} as const

export default api
