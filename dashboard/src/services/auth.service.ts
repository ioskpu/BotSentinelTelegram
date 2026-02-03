import api, { endpoints } from '@/config/api'
import { User } from '@/types'

interface TelegramAuthData {
  id: number
  first_name: string
  last_name?: string
  username?: string
  photo_url?: string
  auth_date: number
  hash: string
}

interface LoginResponse {
  access_token: string
  refresh_token: string
  expires_in: number
}

export const authService = {
  async loginWithTelegram(data: TelegramAuthData): Promise<LoginResponse> {
    const response = await api.post(endpoints.auth.login, data)
    return response.data
  },

  async logout(): Promise<void> {
    await api.post(endpoints.auth.logout)
  },

  async getCurrentUser(): Promise<User> {
    const response = await api.get(endpoints.auth.me)
    return response.data
  },

  async refreshToken(refreshToken: string): Promise<LoginResponse> {
    const response = await api.post(endpoints.auth.refresh, { refresh_token: refreshToken })
    return response.data
  },
}

export default authService
