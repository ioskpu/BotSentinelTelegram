import api, { endpoints } from '@/config/api'
import { Alert, CreateAlertRequest, PaginatedResponse } from '@/types'

export interface AlertsFilter {
  symbol?: string
  type?: string
  isActive?: boolean
  page?: number
  limit?: number
}

export const alertsService = {
  async getAlerts(filter?: AlertsFilter): Promise<PaginatedResponse<Alert>> {
    const response = await api.get(endpoints.alerts.list, { params: filter })
    return response.data
  },

  async getAlert(id: string): Promise<Alert> {
    const response = await api.get(endpoints.alerts.get(id))
    return response.data
  },

  async createAlert(data: CreateAlertRequest): Promise<Alert> {
    const response = await api.post(endpoints.alerts.create, data)
    return response.data
  },

  async updateAlert(id: string, data: Partial<CreateAlertRequest>): Promise<Alert> {
    const response = await api.put(endpoints.alerts.update(id), data)
    return response.data
  },

  async deleteAlert(id: string): Promise<void> {
    await api.delete(endpoints.alerts.delete(id))
  },

  async toggleAlert(id: string): Promise<Alert> {
    const response = await api.post(endpoints.alerts.toggle(id))
    return response.data
  },

  async getAlertStats(): Promise<{ total: number; active: number; triggered: number }> {
    const response = await api.get(endpoints.alerts.stats)
    return response.data
  },
}

export default alertsService
