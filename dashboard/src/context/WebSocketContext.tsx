import { createContext, useContext, useEffect, useState, ReactNode, useCallback } from 'react'
import { wsService } from '@/services/websocket.service'
import { useAuthStore } from '@/store/authStore'

interface WebSocketContextType {
  isConnected: boolean
  subscribe: (event: string, handler: (data: unknown) => void) => () => void
  emit: (event: string, data?: unknown) => void
}

const WebSocketContext = createContext<WebSocketContextType | undefined>(undefined)

export function WebSocketProvider({ children }: { children: ReactNode }) {
  const [isConnected, setIsConnected] = useState(false)
  const { isAuthenticated } = useAuthStore()

  useEffect(() => {
    if (isAuthenticated) {
      wsService.connect()
      
      const unsubConnect = wsService.subscribe('connect', () => setIsConnected(true))
      const unsubDisconnect = wsService.subscribe('disconnect', () => setIsConnected(false))

      return () => {
        unsubConnect()
        unsubDisconnect()
        wsService.disconnect()
      }
    }
    return undefined
  }, [isAuthenticated])

  const subscribe = useCallback((event: string, handler: (data: unknown) => void) => {
    return wsService.subscribe(event, handler)
  }, [])

  const emit = useCallback((event: string, data?: unknown) => {
    wsService.emit(event, data)
  }, [])

  return (
    <WebSocketContext.Provider value={{ isConnected, subscribe, emit }}>
      {children}
    </WebSocketContext.Provider>
  )
}

export function useWebSocket() {
  const context = useContext(WebSocketContext)
  if (!context) {
    throw new Error('useWebSocket must be used within a WebSocketProvider')
  }
  return context
}

export default WebSocketContext
