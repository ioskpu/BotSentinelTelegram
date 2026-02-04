import api, { endpoints } from '@/config/api'
import { Price, PriceHistory } from '@/types'

export interface MarketOverview {
  total_market_cap: number
  total_volume_24h: number
  btc_dominance: number
  eth_dominance: number
  market_cap_change_24h: number
}

export interface TopMover {
  coin_id: string
  symbol: string
  name: string
  price: number
  change_24h: number
  volume_24h: number
  image?: string
}

export const metricsService = {
  async getMarketOverview(): Promise<MarketOverview> {
    const response = await api.get(endpoints.metrics.marketOverview)
    return response.data
  },

  async getTopMovers(type: 'gainers' | 'losers' | 'volume' = 'gainers', limit = 10): Promise<TopMover[]> {
    const response = await api.get(endpoints.metrics.topMovers, {
      params: { sort: type, limit }
    })
    return response.data
  },

  async getPriceHistory(coinId: string, days = 7): Promise<PriceHistory> {
    const response = await api.get(endpoints.prices.history(coinId), {
      params: { days }
    })
    return response.data
  },

  async getCurrentPrices(symbols?: string[]): Promise<Price[]> {
    const response = await api.get(endpoints.prices.list, {
      params: symbols ? { coins: symbols.join(',') } : undefined
    })
    return response.data
  },

  async getAlertMetrics(): Promise<{
    total_alerts: number
    active_alerts: number
    triggered_today: number
    triggered_week: number
    by_type: Record<string, number>
    by_coin: { coin: string; count: number }[]
  }> {
    const response = await api.get(endpoints.metrics.alerts)
    return response.data
  },

  async getPortfolioMetrics(): Promise<{
    total_value: number
    total_invested: number
    total_pnl: number
    pnl_percentage: number
    allocation: { coin_id: string; symbol: string; value: number; percentage: number }[]
  }> {
    const response = await api.get(endpoints.metrics.portfolio)
    return response.data
  },
}

export default metricsService
