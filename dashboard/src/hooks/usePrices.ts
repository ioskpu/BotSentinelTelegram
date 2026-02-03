import { useQuery } from '@tanstack/react-query'
import { useEffect, useState, useCallback } from 'react'
import api, { endpoints } from '../config/api'
import wsService from '../config/websocket'
import { Price, PriceHistory, ApiResponse, WebSocketMessage } from '../types'

export function usePrices(symbols?: string[]) {
  const [realtimePrices, setRealtimePrices] = useState<Map<string, Price>>(new Map())

  const {
    data: initialPrices,
    isLoading,
    error,
    refetch,
  } = useQuery({
    queryKey: ['prices', symbols],
    queryFn: async () => {
      const params = symbols ? `?symbols=${symbols.join(',')}` : ''
      const response = await api.get<ApiResponse<Price[]>>(`${endpoints.prices.list}${params}`)
      return response.data.data
    },
    staleTime: 1000 * 30,
  })

  useEffect(() => {
    if (initialPrices) {
      const priceMap = new Map<string, Price>()
      initialPrices.forEach((price) => {
        priceMap.set(price.symbol, price)
      })
      setRealtimePrices(priceMap)
    }
  }, [initialPrices])

  useEffect(() => {
    const handlePriceUpdate = (message: WebSocketMessage) => {
      const priceUpdate = message.data as Price
      setRealtimePrices((prev) => {
        const newMap = new Map(prev)
        newMap.set(priceUpdate.symbol, priceUpdate)
        return newMap
      })
    }

    const unsubscribe = wsService.subscribe('price_update', handlePriceUpdate)

    if (symbols?.length) {
      wsService.subscribeToPrices(symbols)
    }

    return () => {
      unsubscribe()
      if (symbols?.length) {
        wsService.unsubscribeFromPrices(symbols)
      }
    }
  }, [symbols])

  const prices = Array.from(realtimePrices.values())

  const getPrice = useCallback(
    (symbol: string) => realtimePrices.get(symbol),
    [realtimePrices]
  )

  return {
    prices,
    getPrice,
    isLoading,
    error,
    refetch,
  }
}

export function usePrice(symbol: string) {
  const [realtimePrice, setRealtimePrice] = useState<Price | null>(null)

  const {
    data: initialPrice,
    isLoading,
    error,
  } = useQuery({
    queryKey: ['price', symbol],
    queryFn: async () => {
      const response = await api.get<ApiResponse<Price>>(endpoints.prices.get(symbol))
      return response.data.data
    },
    enabled: !!symbol,
    staleTime: 1000 * 30,
  })

  useEffect(() => {
    if (initialPrice) {
      setRealtimePrice(initialPrice)
    }
  }, [initialPrice])

  useEffect(() => {
    if (!symbol) return

    const handlePriceUpdate = (message: WebSocketMessage) => {
      const priceUpdate = message.data as Price
      if (priceUpdate.symbol === symbol) {
        setRealtimePrice(priceUpdate)
      }
    }

    const unsubscribe = wsService.subscribe('price_update', handlePriceUpdate)
    wsService.subscribeToPrices([symbol])

    return () => {
      unsubscribe()
      wsService.unsubscribeFromPrices([symbol])
    }
  }, [symbol])

  return {
    price: realtimePrice,
    isLoading,
    error,
  }
}

export function usePriceHistory(
  symbol: string,
  timeframe: PriceHistory['timeframe'] = '24h'
) {
  return useQuery({
    queryKey: ['priceHistory', symbol, timeframe],
    queryFn: async () => {
      const response = await api.get<ApiResponse<PriceHistory>>(
        `${endpoints.prices.history(symbol)}?timeframe=${timeframe}`
      )
      return response.data.data
    },
    enabled: !!symbol,
    staleTime: 1000 * 60,
  })
}

export function useSearchPrices(query: string) {
  return useQuery({
    queryKey: ['searchPrices', query],
    queryFn: async () => {
      const response = await api.get<ApiResponse<Price[]>>(
        `${endpoints.prices.search}?q=${encodeURIComponent(query)}`
      )
      return response.data.data
    },
    enabled: query.length >= 2,
    staleTime: 1000 * 60,
  })
}

export default usePrices
