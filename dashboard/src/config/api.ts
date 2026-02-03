import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios'
import { useAuthStore } from '../store/authStore'

const API_URL = import.meta.env.VITE_API_URL || '/api/v1/dashboard'

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
    stats: '/alerts/stats',
  },
  prices: {
    list: '/prices/current',
    get: (symbol: string) => `/prices/${symbol}`,
    history: (symbol: string) => `/prices/history/${symbol}`,
    search: '/prices/search',
  },
  metrics: {
    marketOverview: '/metrics/market/overview',
    topMovers: '/metrics/market/top-movers',
    priceHistory: (symbol: string) => `/metrics/prices/history/${symbol}`,
    alerts: '/metrics/alerts',
    portfolio: '/metrics/portfolio',
    transactions: '/metrics/transactions',
  },
  portfolio: {
    get: '/portfolio',
    add: '/portfolio',
    update: (id: string) => `/portfolio/${id}`,
    delete: (id: string) => `/portfolio/${id}`,
  },
  dashboard: {
    stats: '/stats',
    activity: '/activity',
  },
  user: {
    profile: '/users/me',
    settings: '/users/settings',
    updateSettings: '/users/settings',
  },
} as const

export default api
