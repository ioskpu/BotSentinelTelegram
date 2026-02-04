export interface User {
  telegram_id: number
  username?: string
  first_name: string
  last_name?: string
  photo_url?: string
  created_at: string
  last_login: string
  is_premium?: boolean
}

export interface Alert {
  id: string
  coin_id: string
  coin_symbol: string
  alert_type: 'price_above' | 'price_below' | 'percent_change' | 'volume_spike'
  threshold: number
  is_active: boolean
  created_at: string
  triggered_at?: string
}

export interface CreateAlertRequest {
  coin_id: string
  coin_symbol: string
  alert_type: Alert['alert_type']
  threshold: number
}

export interface Price {
  symbol: string
  name: string
  price: number
  change24h: number
  changePercent24h: number
  volume24h: number
  marketCap: number
  high24h: number
  low24h: number
  lastUpdated: string
  sparkline?: number[]
}

export interface PriceHistory {
  symbol: string
  prices: {
    timestamp: string
    price: number
    volume: number
  }[]
  timeframe: '1h' | '24h' | '7d' | '30d' | '1y'
}

export interface Portfolio {
  id: string
  coin_id: string
  coin_symbol: string
  coin_name: string
  amount: number
  buy_price?: number
  buy_date?: string
  notes?: string
  current_price?: number
  current_value?: number
  profit_loss?: number
  profit_loss_percent?: number
  created_at: string
  updated_at: string
}

export interface PortfolioSummary {
  total_value: number
  total_invested: number
  total_profit_loss: number
  total_profit_loss_percent: number
  positions_count: number
  positions: Portfolio[]
  holdings?: PortfolioHolding[]
}

export interface CreatePositionRequest {
  coin_id: string
  coin_symbol: string
  coin_name: string
  amount: number
  buy_price?: number
  buy_date?: string
  notes?: string
}

export interface PortfolioHolding {
  symbol: string
  name: string
  amount: number
  avgBuyPrice: number
  currentPrice: number
  value: number
  profitLoss: number
  profitLossPercent: number
  allocation: number
}

export interface Activity {
  id: string
  type: 'alert_triggered' | 'alert_created' | 'trade' | 'deposit' | 'withdrawal'
  title: string
  description: string
  symbol?: string
  value?: number
  timestamp: string
}

export interface DashboardStats {
  totalAlerts: number
  activeAlerts: number
  triggeredToday: number
  portfolioValue: number
  portfolioChange24h: number
  portfolioChangePercent24h: number
  topGainer: {
    symbol: string
    changePercent: number
  }
  topLoser: {
    symbol: string
    changePercent: number
  }
}

export interface WebSocketMessage {
  type: 'price_update' | 'alert_triggered' | 'connection' | 'error'
  data: unknown
  timestamp: string
}

export interface ApiResponse<T> {
  success: boolean
  data: T
  message?: string
  error?: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  pageSize: number
  hasMore: boolean
}
