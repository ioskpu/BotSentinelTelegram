import { Outlet } from 'react-router-dom'
import { useEffect } from 'react'
import Sidebar from './Sidebar'
import Header from './Header'
import wsService from '../../config/websocket'
import { useAuthStore } from '../../store/authStore'

export default function Layout() {
  const { isAuthenticated } = useAuthStore()

  useEffect(() => {
    if (isAuthenticated) {
      wsService.connect()
    }

    return () => {
      wsService.disconnect()
    }
  }, [isAuthenticated])

  return (
    <div className="min-h-screen bg-crypto-bg">
      <Sidebar />
      <div className="ml-64">
        <Header />
        <main className="p-6">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
