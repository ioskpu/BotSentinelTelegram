import { useAuthStore } from '../store/authStore'
import { WebSocketMessage } from '../types'

type MessageHandler = (message: WebSocketMessage) => void

class WebSocketService {
  private socket: WebSocket | null = null
  private handlers: Map<string, Set<MessageHandler>> = new Map()
  private reconnectAttempts = 0
  private maxReconnectAttempts = 10
  private reconnectInterval = 3000
  private heartbeatInterval: number | null = null

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
    }
  }

  private handleMessage(message: any): void {
    if (message.type === 'auth_success') {
      console.log('WebSocket authenticated successfully')
    }
    
    this.notifyHandlers(message.type, message)
  }

  private scheduleReconnect(): void {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++
      setTimeout(() => this.connect(), this.reconnectInterval)
    }
  }

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

  private notifyHandlers(event: string, message: WebSocketMessage): void {
    this.handlers.get(event)?.forEach(handler => handler(message))
    this.handlers.get('*')?.forEach(handler => handler(message))
  }

  subscribeToPrices(symbols: string[]): void {
    if (this.socket?.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify({
        type: 'subscribe',
        channel: 'prices',
        symbols
      }))
    }
  }

  unsubscribeFromPrices(symbols: string[]): void {
    if (this.socket?.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify({
        type: 'unsubscribe',
        channel: 'prices',
        symbols
      }))
    }
  }
}

export const wsService = new WebSocketService()
export default wsService
