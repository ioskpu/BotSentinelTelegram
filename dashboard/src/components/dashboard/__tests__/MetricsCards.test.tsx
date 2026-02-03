import { render, screen } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import MetricsCards from '../MetricsCards'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'

// Mock del servicio de métricas
vi.mock('@/services/metrics.service', () => ({
  metricsService: {
    getMarketOverview: vi.fn().mockResolvedValue({
      total_market_cap: 2500000000000,
      total_volume_24h: 80000000000,
      btc_dominance: 52.5,
      market_cap_change_24h: 2.5
    }),
    getAlertMetrics: vi.fn().mockResolvedValue({
      active_alerts: 5,
      triggered_today: 2
    }),
    getPortfolioMetrics: vi.fn().mockResolvedValue({
      total_value: 15000,
      pnl_percentage: 5.5
    })
  }
}))

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: false,
    },
  },
})

const renderWithClient = (ui: React.ReactElement) => {
  return render(
    <QueryClientProvider client={queryClient}>
      {ui}
    </QueryClientProvider>
  )
}

describe('MetricsCards', () => {
  it('renders loading skeletons initially', () => {
    renderWithClient(<MetricsCards />)
    // Buscamos los contenedores de esqueleto (Skeleton)
    // Nota: Dependiendo de cómo esté implementado Skeleton, buscaremos una clase o rol
    expect(screen.getAllByRole('status')).toBeDefined()
  })

  it('renders metric titles', () => {
    renderWithClient(<MetricsCards />)
    expect(screen.getByText('Total Market Cap')).toBeDefined()
    expect(screen.getByText('Portfolio Value')).toBeDefined()
    expect(screen.getByText('Active Alerts')).toBeDefined()
  })
})
