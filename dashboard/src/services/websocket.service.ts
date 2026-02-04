import { useAuthStore } from '@/store/authStore'

type MessageHandler = (data: unknown) => void

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
    const wsUrl = import.meta.env.VITE_WS_URL || `${protocol}//${window.location.host}/ws/dashboard`
    
    console.log('Connecting to WebSocket:', wsUrl)
    this.socket = new WebSocket(wsUrl)

    this.socket.onopen = () => {
      console.log('WebSocket connected')
      this.reconnectAttempts = 0
      this.authenticate()
      this.startHeartbeat()
    }

    this.socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        this.handleMessage(data)
      } catch (error) {
        console.error('Error parsing WebSocket message:', error)
      }
    }

    this.socket.onclose = (event) => {
      console.log('WebSocket closed:', event.reason)
      this.stopHeartbeat()
      this.scheduleReconnect()
    }

    this.socket.onerror = (error) => {
      console.error('WebSocket error:', error)
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
    this.handlers.get(event)?.forEach(handler => handler(data))
    this.handlers.get('*')?.forEach(handler => handler({ event, data }))
  }

  emit(type: string, data?: any): void {
    if (this.socket?.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify({ type, ...data }))
    }
  }

  isConnected(): boolean {
    return this.socket?.readyState === WebSocket.OPEN
  }
}

export const wsService = new WebSocketService()
export default wsService
