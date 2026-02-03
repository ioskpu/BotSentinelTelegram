import { io, Socket } from 'socket.io-client'
import { useAuthStore } from '../store/authStore'
import { WebSocketMessage } from '../types'

const WS_URL = import.meta.env.VITE_WS_URL || ''

type MessageHandler = (message: WebSocketMessage) => void

class WebSocketService {
  private socket: Socket | null = null
  private handlers: Map<string, Set<MessageHandler>> = new Map()
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  private reconnectDelay = 1000

  connect(): void {
    if (this.socket?.connected) return

    const token = useAuthStore.getState().token
    
    this.socket = io(WS_URL, {
      auth: { token },
      transports: ['websocket'],
      reconnection: true,
      reconnectionAttempts: this.maxReconnectAttempts,
      reconnectionDelay: this.reconnectDelay,
    })

    this.socket.on('connect', () => {
      console.log('WebSocket connected')
      this.reconnectAttempts = 0
      this.notifyHandlers('connection', {
        type: 'connection',
        data: { status: 'connected' },
        timestamp: new Date().toISOString(),
      })
    })

    this.socket.on('disconnect', (reason) => {
      console.log('WebSocket disconnected:', reason)
      this.notifyHandlers('connection', {
        type: 'connection',
        data: { status: 'disconnected', reason },
        timestamp: new Date().toISOString(),
      })
    })

    this.socket.on('price_update', (data) => {
      this.notifyHandlers('price_update', {
        type: 'price_update',
        data,
        timestamp: new Date().toISOString(),
      })
    })

    this.socket.on('alert_triggered', (data) => {
      this.notifyHandlers('alert_triggered', {
        type: 'alert_triggered',
        data,
        timestamp: new Date().toISOString(),
      })
    })

    this.socket.on('error', (error) => {
      console.error('WebSocket error:', error)
      this.notifyHandlers('error', {
        type: 'error',
        data: { error },
        timestamp: new Date().toISOString(),
      })
    })

    this.socket.on('connect_error', (error) => {
      console.error('WebSocket connection error:', error)
      this.reconnectAttempts++
      if (this.reconnectAttempts >= this.maxReconnectAttempts) {
        console.error('Max reconnection attempts reached')
      }
    })
  }

  disconnect(): void {
    if (this.socket) {
      this.socket.disconnect()
      this.socket = null
    }
  }

  subscribe(event: string, handler: MessageHandler): () => void {
    if (!this.handlers.has(event)) {
      this.handlers.set(event, new Set())
    }
    this.handlers.get(event)!.add(handler)

    return () => {
      this.handlers.get(event)?.delete(handler)
    }
  }

  private notifyHandlers(event: string, message: WebSocketMessage): void {
    this.handlers.get(event)?.forEach((handler) => handler(message))
    this.handlers.get('*')?.forEach((handler) => handler(message))
  }

  subscribeToPrices(symbols: string[]): void {
    if (this.socket?.connected) {
      this.socket.emit('subscribe_prices', { symbols })
    }
  }

  unsubscribeFromPrices(symbols: string[]): void {
    if (this.socket?.connected) {
      this.socket.emit('unsubscribe_prices', { symbols })
    }
  }

  isConnected(): boolean {
    return this.socket?.connected ?? false
  }
}

export const wsService = new WebSocketService()
export default wsService
