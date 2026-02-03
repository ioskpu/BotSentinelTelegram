import api, { endpoints } from '@/config/api'
import { Portfolio, PortfolioSummary, CreatePositionRequest } from '@/types'

export const portfolioService = {
  async getPortfolio(): Promise<PortfolioSummary> {
    const response = await api.get(endpoints.portfolio.get)
    return response.data
  },

  async createPosition(data: CreatePositionRequest): Promise<Portfolio> {
    const response = await api.post(endpoints.portfolio.add, data)
    return response.data
  },

  async updatePosition(id: string, data: Partial<CreatePositionRequest>): Promise<Portfolio> {
    const response = await api.put(endpoints.portfolio.update(id), data)
    return response.data
  },

  async deletePosition(id: string): Promise<void> {
    await api.delete(endpoints.portfolio.delete(id))
  },
}

export default portfolioService
