import { useAuthStore } from '@/store/authStore'
import { WebSocketMessage } from '@/types'

export type MessageHandler = (data: any) => void

class WebSocketService {
  private socket: WebSocket | null = null
  private handlers: Map<string, Set<MessageHandler>> = new Map()
  private reconnectAttempts = 0
  private maxReconnectAttempts = 10
  private reconnectInterval = 3000
  private authTimeout: number | null = null

  connect(): void {
    if (this.socket && (this.socket.readyState === WebSocket.OPEN || this.socket.readyState === WebSocket.CONNECTING)) {
      return
    }

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    let wsUrl = import.meta.env.VITE_WS_URL
    
    if (!wsUrl) {
      const apiUrl = import.meta.env.VITE_API_URL
      if (apiUrl && apiUrl.startsWith('http')) {
        // Derive WS URL from API URL
        wsUrl = apiUrl.replace(/^http/, 'ws').replace(/\/api\/v1\/dashboard\/?$/, '/ws/dashboard')
      } else {
        // Fallback to current host
        wsUrl = `${protocol}//${window.location.host}/ws/dashboard`
      }
    }
    
    console.log('Connecting to WebSocket:', wsUrl)
    this.socket = new WebSocket(wsUrl)

    this.socket.onopen = () => {
      console.log('WebSocket connected')
      this.reconnectAttempts = 0
      this.authenticate()
      this.startHeartbeat()
      
      this.notifyHandlers('connection', {
        type: 'connection',
        data: { status: 'connected' },
        timestamp: new Date().toISOString(),
      })
    }

    this.socket.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data)
        // Backend usually sends {type, data} or just the object
        this.handleMessage(message)
      } catch (error) {
        console.error('Error parsing WebSocket message:', error)
      }
    }

    this.socket.onclose = (event) => {
      console.log('WebSocket closed:', event.reason)
      this.stopHeartbeat()
      this.notifyHandlers('connection', {
        type: 'connection',
        data: { status: 'disconnected', reason: event.reason },
        timestamp: new Date().toISOString(),
      })
      this.scheduleReconnect()
    }

    this.socket.onerror = (error) => {
      console.error('WebSocket error:', error)
      this.notifyHandlers('error', {
        type: 'error',
        data: { error },
        timestamp: new Date().toISOString(),
      })
    }
  }

  private authenticate(): void {
    const token = useAuthStore.getState().token
    if (token && this.socket?.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify({
        type: 'auth',
        token: token
      }))
      
      // Timeout for auth
      this.authTimeout = window.setTimeout(() => {
        console.warn('WebSocket auth timeout')
      }, 5000)
    }
  }

  private handleMessage(message: any): void {
    const { type, data } = message
    
    if (type === 'auth_success') {
      if (this.authTimeout) clearTimeout(this.authTimeout)
      console.log('WebSocket authenticated successfully')
    }
    
    this.notifyHandlers(type, data || message)
  }

  private scheduleReconnect(): void {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++
      console.log(`Reconnecting in ${this.reconnectInterval}ms (Attempt ${this.reconnectAttempts})`)
      setTimeout(() => this.connect(), this.reconnectInterval)
    }
  }

  private heartbeatInterval: number | null = null

  private startHeartbeat(): void {
    this.heartbeatInterval = window.setInterval(() => {
      if (this.socket?.readyState === WebSocket.OPEN) {
        this.socket.send(JSON.stringify({ type: 'ping' }))
      }
    }, 30000)
  }

  private stopHeartbeat(): void {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval)
      this.heartbeatInterval = null
    }
  }

  disconnect(): void {
    if (this.socket) {
      this.socket.close()
      this.socket = null
    }
    this.stopHeartbeat()
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

  private notifyHandlers(event: string, data: unknown): void {
    const handlers = this.handlers.get(event)
    if (handlers) {
      handlers.forEach(handler => handler(data))
    }
    
    const wildcardHandlers = this.handlers.get('*')
    if (wildcardHandlers) {
      wildcardHandlers.forEach(handler => handler({ event, data }))
    }
    
    // Compatibility for Header.tsx and other connection status listeners
    if (event === 'connection') {
      const connData = data as any
      if (connData.status === 'connected') {
        this.handlers.get('connect')?.forEach(h => h(data))
      } else if (connData.status === 'disconnected') {
        this.handlers.get('disconnect')?.forEach(h => h(data))
      }
    }
  }

  emit(type: string, data?: any): void {
    if (this.socket?.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify({ type, ...data }))
    }
  }

  subscribeToPrices(symbols: string[]): void {
    this.emit('subscribe_prices', { symbols })
  }

  unsubscribeFromPrices(symbols: string[]): void {
    this.emit('unsubscribe_prices', { symbols })
  }

  isConnected(): boolean {
    return this.socket?.readyState === WebSocket.OPEN
  }
}

export const wsService = new WebSocketService()
export default wsService
