import { useState, useEffect } from 'react'
import { useWebSocket } from '@/context/WebSocketContext'
import { Skeleton } from '@/components/ui/Skeleton'

interface FeedEvent {
  id: string
  type: 'whale' | 'price' | 'alert' | 'trade'
  title: string
  description: string
  value?: string
  chain?: string
  timestamp: Date
  icon: string
  color: string
}

export default function LiveFeed() {
  const { subscribe, isConnected } = useWebSocket()
  const [events, setEvents] = useState<FeedEvent[]>([])
  const [isPaused, setIsPaused] = useState(false)
  const [isInitialLoading, setIsInitialLoading] = useState(true)

  useEffect(() => {
    // Initial loading simulation
    const timer = setTimeout(() => setIsInitialLoading(false), 1000)
    return () => clearTimeout(timer)
  }, [])

  useEffect(() => {
    // Subscribe to various events
    const unsubPrice = subscribe('price_update', (data) => {
      if (isPaused) return
      const priceData = data as { symbol: string; price: number; change: number }
      if (Math.abs(priceData.change) > 2) {
        addEvent({
          type: 'price',
          title: `${priceData.symbol} ${priceData.change > 0 ? '📈' : '📉'}`,
          description: `Price ${priceData.change > 0 ? 'surged' : 'dropped'} ${Math.abs(priceData.change).toFixed(2)}%`,
          value: `$${priceData.price.toLocaleString()}`,
          icon: priceData.change > 0 ? '↑' : '↓',
          color: priceData.change > 0 ? 'crypto-gain' : 'crypto-loss',
        })
      }
    })

    const unsubWhale = subscribe('whale_alert', (data) => {
      if (isPaused) return
      const whaleData = data as { symbol: string; amount: number; chain: string; type: string }
      addEvent({
        type: 'whale',
        title: `🐋 Whale ${whaleData.type}`,
        description: `${whaleData.amount.toLocaleString()} ${whaleData.symbol} moved`,
        chain: whaleData.chain,
        icon: '🐋',
        color: 'crypto-purple',
      })
    })

    const unsubAlert = subscribe('alert_triggered', (data) => {
      if (isPaused) return
      const alertData = data as { symbol: string; targetValue: number; message?: string }
      addEvent({
        type: 'alert',
        title: `🔔 Alert Triggered`,
        description: alertData.message || `${alertData.symbol} hit $${alertData.targetValue}`,
        icon: '🔔',
        color: 'crypto-accent',
      })
    })

    return () => {
      unsubPrice()
      unsubWhale()
      unsubAlert()
    }
  }, [subscribe, isPaused])

  const addEvent = (event: Omit<FeedEvent, 'id' | 'timestamp'>) => {
    const newEvent: FeedEvent = {
      ...event,
      id: crypto.randomUUID(),
      timestamp: new Date(),
    }
    setEvents(prev => [newEvent, ...prev].slice(0, 50))
  }

  // Demo events for development
  useEffect(() => {
    if (events.length === 0) {
      const demoEvents: FeedEvent[] = [
        {
          id: '1',
          type: 'whale',
          title: '🐋 Whale Transfer',
          description: '1,500 BTC moved to unknown wallet',
          chain: 'Bitcoin',
          timestamp: new Date(Date.now() - 60000),
          icon: '🐋',
          color: 'crypto-purple',
        },
        {
          id: '2',
          type: 'price',
          title: 'ETH 📈',
          description: 'Price surged 3.5% in the last hour',
          value: '$3,450',
          timestamp: new Date(Date.now() - 120000),
          icon: '↑',
          color: 'crypto-gain',
        },
        {
          id: '3',
          type: 'alert',
          title: '🔔 Alert Triggered',
          description: 'SOL crossed $150 threshold',
          timestamp: new Date(Date.now() - 180000),
          icon: '🔔',
          color: 'crypto-accent',
        },
      ]
      setEvents(demoEvents)
    }
  }, [])

  const getTimeAgo = (date: Date) => {
    const seconds = Math.floor((new Date().getTime() - date.getTime()) / 1000)
    if (seconds < 60) return `${seconds}s ago`
    const minutes = Math.floor(seconds / 60)
    if (minutes < 60) return `${minutes}m ago`
    const hours = Math.floor(minutes / 60)
    return `${hours}h ago`
  }

  return (
    <div className="card h-full flex flex-col">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <h3 className="text-lg font-semibold">Live Feed</h3>
          <div className={`flex items-center gap-1.5 px-2 py-0.5 rounded-full text-xs ${
            isConnected ? 'bg-crypto-gain/20 text-crypto-gain' : 'bg-crypto-loss/20 text-crypto-loss'
          }`}>
            <div className={`w-1.5 h-1.5 rounded-full ${isConnected ? 'bg-crypto-gain animate-pulse' : 'bg-crypto-loss'}`} />
            {isConnected ? 'Live' : 'Offline'}
          </div>
        </div>
        <button
          onClick={() => setIsPaused(!isPaused)}
          className={`p-2 rounded-lg transition-colors ${
            isPaused ? 'bg-crypto-accent/20 text-crypto-accent' : 'bg-crypto-bg-tertiary text-crypto-text-secondary hover:text-crypto-text'
          }`}
          title={isPaused ? 'Resume' : 'Pause'}
        >
          {isPaused ? (
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
              <path d="M8 5v14l11-7z" />
            </svg>
          ) : (
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
              <path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z" />
            </svg>
          )}
        </button>
      </div>

      <div className="flex-1 overflow-y-auto space-y-3 min-h-0">
        {isInitialLoading ? (
          <div className="space-y-3">
            {[1, 2, 3, 4].map(i => (
              <div key={i} className="p-3 rounded-lg bg-crypto-bg-tertiary/30 border-l-2 border-crypto-border">
                <div className="flex items-start justify-between gap-2">
                  <div className="flex-1 space-y-2">
                    <Skeleton className="h-4 w-1/2 rounded" />
                    <Skeleton className="h-3 w-3/4 rounded" />
                  </div>
                  <Skeleton className="h-4 w-12 rounded" />
                </div>
              </div>
            ))}
          </div>
        ) : events.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-crypto-text-muted">
            <svg className="w-12 h-12 mb-2 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
            <p>Waiting for events...</p>
          </div>
        ) : (
          events.map((event, index) => (
            <div
              key={event.id}
              className={`p-3 rounded-lg bg-crypto-bg-tertiary/50 border-l-2 border-${event.color} animate-fade-in`}
              style={{ animationDelay: `${index * 50}ms` }}
            >
              <div className="flex items-start justify-between gap-2">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="font-medium text-sm">{event.title}</span>
                    {event.chain && (
                      <span className="text-xs px-1.5 py-0.5 rounded bg-crypto-purple/20 text-crypto-purple">
                        {event.chain}
                      </span>
                    )}
                  </div>
                  <p className="text-sm text-crypto-text-secondary truncate">{event.description}</p>
                </div>
                <div className="text-right flex-shrink-0">
                  {event.value && (
                    <p className={`font-mono font-semibold text-sm text-${event.color}`}>
                      {event.value}
                    </p>
                  )}
                  <p className="text-xs text-crypto-text-muted">{getTimeAgo(event.timestamp)}</p>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}
