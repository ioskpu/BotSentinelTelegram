import { useState } from 'react'
import { useAuth } from '../../hooks/useAuth'
import { useAlertStore } from '../../store/alertStore'
import { useTheme } from '../../context/ThemeContext'
import { useWebSocket } from '../../context/WebSocketContext'

export default function Header() {
  const { user, logout } = useAuth()
  const { unreadCount, triggeredAlerts, markAllAsRead } = useAlertStore()
  const { theme, toggleTheme } = useTheme()
  const { isConnected } = useWebSocket()
  const [showNotifications, setShowNotifications] = useState(false)
  const [showUserMenu, setShowUserMenu] = useState(false)

  return (
    <header className="h-16 bg-crypto-bg-secondary border-b border-crypto-border flex items-center justify-between px-6">
      <div className="flex items-center gap-4">
        <h2 className="text-xl font-semibold text-crypto-text">Dashboard</h2>
        <div className={`flex items-center gap-1.5 px-2 py-1 rounded-full text-xs ${
          isConnected ? 'bg-crypto-gain/20 text-crypto-gain' : 'bg-crypto-loss/20 text-crypto-loss'
        }`}>
          <div className={`w-1.5 h-1.5 rounded-full ${isConnected ? 'bg-crypto-gain animate-pulse' : 'bg-crypto-loss'}`} />
          {isConnected ? 'Live' : 'Offline'}
        </div>
      </div>

      <div className="flex items-center gap-4">
        {/* Theme Toggle */}
        <button
          onClick={toggleTheme}
          className="p-2 rounded-lg hover:bg-crypto-bg-tertiary transition-colors"
          title={theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
        >
          {theme === 'dark' ? (
            <svg className="w-5 h-5 text-crypto-text-secondary hover:text-crypto-accent transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
            </svg>
          ) : (
            <svg className="w-5 h-5 text-crypto-text-secondary hover:text-crypto-purple transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
            </svg>
          )}
        </button>

        {/* Notifications */}
        <div className="relative">
          <button
            onClick={() => setShowNotifications(!showNotifications)}
            className="relative p-2 rounded-lg hover:bg-crypto-bg-tertiary transition-colors"
          >
            <svg className="w-6 h-6 text-crypto-text-secondary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
            </svg>
            {unreadCount > 0 && (
              <span className="absolute top-0 right-0 w-5 h-5 bg-crypto-loss text-white text-xs font-bold rounded-full flex items-center justify-center">
                {unreadCount > 9 ? '9+' : unreadCount}
              </span>
            )}
          </button>

          {showNotifications && (
            <div className="absolute right-0 top-12 w-80 bg-crypto-bg-secondary border border-crypto-border rounded-xl shadow-crypto-lg z-50">
              <div className="p-4 border-b border-crypto-border flex items-center justify-between">
                <h3 className="font-semibold">Notifications</h3>
                {unreadCount > 0 && (
                  <button
                    onClick={markAllAsRead}
                    className="text-xs text-crypto-accent hover:underline"
                  >
                    Mark all as read
                  </button>
                )}
              </div>
              <div className="max-h-96 overflow-y-auto">
                {triggeredAlerts.length === 0 ? (
                  <div className="p-4 text-center text-crypto-text-muted">
                    No notifications yet
                  </div>
                ) : (
                  triggeredAlerts.slice(0, 10).map((alert) => (
                    <div
                      key={alert.id}
                      className="p-4 border-b border-crypto-border hover:bg-crypto-bg-tertiary transition-colors"
                    >
                      <div className="flex items-center gap-2">
                        <span className="font-mono text-crypto-accent">{alert.symbol}</span>
                        <span className="badge-neutral">{alert.type}</span>
                      </div>
                      <p className="text-sm text-crypto-text-secondary mt-1">
                        {alert.message || `Target: $${alert.targetValue.toLocaleString()}`}
                      </p>
                      <p className="text-xs text-crypto-text-muted mt-1">
                        {new Date(alert.triggeredAt || alert.updatedAt).toLocaleString()}
                      </p>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}
        </div>

        <div className="relative">
          <button
            onClick={() => setShowUserMenu(!showUserMenu)}
            className="flex items-center gap-3 p-2 rounded-lg hover:bg-crypto-bg-tertiary transition-colors"
          >
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-crypto-accent to-crypto-gain flex items-center justify-center">
              {user?.photoUrl ? (
                <img src={user.photoUrl} alt={user.username} className="w-8 h-8 rounded-full" />
              ) : (
                <span className="text-sm font-bold text-crypto-bg">
                  {user?.firstName?.[0] || user?.username?.[0] || 'U'}
                </span>
              )}
            </div>
            <div className="text-left hidden sm:block">
              <p className="text-sm font-medium">{user?.firstName || user?.username}</p>
              <p className="text-xs text-crypto-text-muted">
                {user?.isPremium ? 'Premium' : 'Free'}
              </p>
            </div>
          </button>

          {showUserMenu && (
            <div className="absolute right-0 top-12 w-48 bg-crypto-bg-secondary border border-crypto-border rounded-xl shadow-crypto-lg z-50">
              <div className="p-2">
                <button
                  onClick={logout}
                  className="w-full flex items-center gap-2 px-4 py-2 text-left rounded-lg hover:bg-crypto-bg-tertiary text-crypto-loss transition-colors"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                  </svg>
                  Logout
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  )
}
