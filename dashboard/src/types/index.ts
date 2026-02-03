export interface User {
  id: string
  telegramId: number
  username: string
  firstName?: string
  lastName?: string
  photoUrl?: string
  isPremium: boolean
  createdAt: string
  lastActiveAt: string
}

export interface Alert {
  id: string
  userId: string
  symbol: string
  type: 'price_above' | 'price_below' | 'percent_change' | 'volume_spike'
  condition: AlertCondition
  targetValue: number
  currentValue?: number
  isActive: boolean
  isTriggered: boolean
  triggeredAt?: string
  createdAt: string
  updatedAt: string
  message?: string
}

export interface AlertCondition {
  operator: 'gt' | 'lt' | 'gte' | 'lte' | 'eq'
  value: number
  timeframe?: string
}

export interface CreateAlertRequest {
  symbol: string
  type: Alert['type']
  targetValue: number
  condition?: Partial<AlertCondition>
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
  userId: string
  totalValue: number
  totalProfitLoss: number
  totalProfitLossPercent: number
  holdings: PortfolioHolding[]
  updatedAt: string
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
