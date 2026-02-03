import api, { endpoints } from '@/config/api'
import { Activity } from '@/types'

export const activityService = {
  async getRecentActivity(): Promise<Activity[]> {
    const response = await api.get(endpoints.dashboard.activity)
    return response.data
  },

  async getLogs(): Promise<any[]> {
    const response = await api.get(endpoints.dashboard.activity)
    return response.data
  }
}

export default activityService
