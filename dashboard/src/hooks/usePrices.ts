import { useQuery } from '@tanstack/react-query'
import { useEffect, useState, useCallback } from 'react'
import { wsService } from '../services/websocket.service'
import { Price } from '../types'
import { metricsService } from '../services/metrics.service'

export function usePrices(symbols?: string[]) {
  const [realtimePrices, setRealtimePrices] = useState<Map<string, Price>>(new Map())

  const {
    data: initialPrices,
    isLoading,
    error,
    refetch,
  } = useQuery({
    queryKey: ['prices', symbols],
    queryFn: () => metricsService.getCurrentPrices(symbols),
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
    const handlePriceUpdate = (message: any) => {
      const priceUpdate = message.data as Price
      // Convert to snake_case if coming from WS
      const formattedPrice: Price = {
        ...priceUpdate,
        current_price: priceUpdate.current_price || (priceUpdate as any).price,
        price_change_percentage_24h: priceUpdate.price_change_percentage_24h || (priceUpdate as any).change_percent_24h
      }
      setRealtimePrices((prev) => {
        const newMap = new Map(prev)
        newMap.set(formattedPrice.symbol, formattedPrice)
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
      const prices = await metricsService.getCurrentPrices([symbol])
      return prices[0] || null
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

    const handlePriceUpdate = (message: any) => {
      const priceUpdate = message.data as Price
      if (priceUpdate.symbol === symbol) {
        // Convert to snake_case
        const formattedPrice: Price = {
          ...priceUpdate,
          current_price: priceUpdate.current_price || (priceUpdate as any).price,
          price_change_percentage_24h: priceUpdate.price_change_percentage_24h || (priceUpdate as any).change_percent_24h
        }
        setRealtimePrice(formattedPrice)
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
  timeframe: string = '7d'
) {
  return useQuery({
    queryKey: ['priceHistory', symbol, timeframe],
    queryFn: () => metricsService.getPriceHistory(symbol, parseInt(timeframe)),
    enabled: !!symbol,
    staleTime: 1000 * 60,
  })
}

export function useSearchPrices(query: string) {
  return useQuery({
    queryKey: ['searchPrices', query],
    queryFn: async () => {
      // For now, use metricsService if it has search, or api directly
      const response = await metricsService.getCurrentPrices() // Placeholder if no search
      return response.filter(p => 
        p.symbol.toLowerCase().includes(query.toLowerCase()) || 
        p.name?.toLowerCase().includes(query.toLowerCase())
      )
    },
    enabled: query.length >= 2,
    staleTime: 1000 * 60,
  })
}

export default usePrices
