import api from '@/config/api'
import { Price, PriceHistory, DashboardStats } from '@/types'

export interface MarketOverview {
  totalMarketCap: number
  totalVolume24h: number
  btcDominance: number
  ethDominance: number
  marketCapChange24h: number
}

export interface TopMover {
  coinId: string
  symbol: string
  name: string
  price: number
  change24h: number
  volume24h: number
  image?: string
}

export const metricsService = {
  async getMarketOverview(): Promise<MarketOverview> {
    const response = await api.get('/v1/metrics/market/overview')
    return response.data
  },

  async getTopMovers(type: 'gainers' | 'losers' | 'volume' = 'gainers', limit = 10): Promise<TopMover[]> {
    const response = await api.get('/v1/metrics/market/top-movers', {
      params: { sort: type, limit }
    })
    return response.data
  },

  async getPriceHistory(coinId: string, days = 7): Promise<PriceHistory> {
    const response = await api.get(`/v1/metrics/prices/history/${coinId}`, {
      params: { days }
    })
    return response.data
  },

  async getCurrentPrices(symbols?: string[]): Promise<Price[]> {
    const response = await api.get('/v1/prices/current', {
      params: symbols ? { symbols: symbols.join(',') } : undefined
    })
    return response.data
  },

  async getDashboardStats(): Promise<DashboardStats> {
    const response = await api.get('/v1/dashboard/stats')
    return response.data
  },

  async getAlertMetrics(): Promise<{
    total: number
    active: number
    triggeredToday: number
    triggeredWeek: number
    byType: Record<string, number>
    byCoin: { coin: string; count: number }[]
  }> {
    const response = await api.get('/v1/metrics/alerts')
    return response.data
  },

  async getPortfolioMetrics(): Promise<{
    totalValue: number
    totalInvested: number
    totalPnl: number
    pnlPercentage: number
    allocation: { coinId: string; symbol: string; value: number; percentage: number }[]
  }> {
    const response = await api.get('/v1/metrics/portfolio')
    return response.data
  },
}

export default metricsService
