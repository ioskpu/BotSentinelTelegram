import { io, Socket } from 'socket.io-client'
import { useAuthStore } from '@/store/authStore'

type MessageHandler = (data: unknown) => void

class WebSocketService {
  private socket: Socket | null = null
  private handlers: Map<string, Set<MessageHandler>> = new Map()
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5

  connect(): void {
    if (this.socket?.connected) return

    const wsUrl = import.meta.env.VITE_WS_URL || window.location.origin
    
    this.socket = io(wsUrl, {
      path: '/ws',
      transports: ['websocket', 'polling'],
      autoConnect: true,
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionDelayMax: 5000,
      reconnectionAttempts: this.maxReconnectAttempts,
    })

    this.socket.on('connect', () => {
      console.log('WebSocket connected')
      this.reconnectAttempts = 0
      this.authenticate()
    })

    this.socket.on('disconnect', (reason) => {
      console.log('WebSocket disconnected:', reason)
    })

    this.socket.on('error', (error) => {
      console.error('WebSocket error:', error)
    })

    this.socket.onAny((event, data) => {
      this.notifyHandlers(event, data)
    })
  }

  private authenticate(): void {
    const token = useAuthStore.getState().token
    if (token && this.socket) {
      this.socket.emit('auth', { token })
    }
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

  private notifyHandlers(event: string, data: unknown): void {
    this.handlers.get(event)?.forEach(handler => handler(data))
    this.handlers.get('*')?.forEach(handler => handler({ event, data }))
  }

  emit(event: string, data?: unknown): void {
    if (this.socket?.connected) {
      this.socket.emit(event, data)
    }
  }

  isConnected(): boolean {
    return this.socket?.connected ?? false
  }
}

export const wsService = new WebSocketService()
export default wsService
