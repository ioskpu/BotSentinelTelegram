import { useEffect, useRef } from 'react'
import { Navigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'

declare global {
  interface Window {
    TelegramLoginWidget: {
      dataOnauth: (user: TelegramUser) => void
    }
  }
}

interface TelegramUser {
  id: number
  first_name: string
  last_name?: string
  username?: string
  photo_url?: string
  auth_date: number
  hash: string
}

export default function Login() {
  const { isAuthenticated, login, isLoggingIn, loginError } = useAuth()
  const telegramContainerRef = useRef<HTMLDivElement>(null)

  const botUsername = import.meta.env.VITE_TELEGRAM_BOT_USERNAME || 'CryptoSentinelBot'

  useEffect(() => {
    if (!telegramContainerRef.current || isAuthenticated) return

    window.TelegramLoginWidget = {
      dataOnauth: (user: TelegramUser) => {
        console.log('Telegram auth received:', user)
        login(user)
      },
    }

    const script = document.createElement('script')
    script.src = 'https://telegram.org/js/telegram-widget.js?22'
    script.setAttribute('data-telegram-login', botUsername)
    script.setAttribute('data-size', 'large')
    script.setAttribute('data-radius', '8')
    script.setAttribute('data-onauth', 'TelegramLoginWidget.dataOnauth(user)')
    script.setAttribute('data-request-access', 'write')
    script.async = true

    telegramContainerRef.current.appendChild(script)

    return () => {
      if (telegramContainerRef.current) {
        telegramContainerRef.current.innerHTML = ''
      }
    }
  }, [botUsername, isAuthenticated, login])

  if (isAuthenticated) {
    return <Navigate to="/" replace />
  }

  return (
    <div className="min-h-screen bg-crypto-bg flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <div className="w-20 h-20 mx-auto mb-4 rounded-2xl bg-gradient-to-br from-crypto-accent to-crypto-gain flex items-center justify-center">
            <svg className="w-12 h-12 text-crypto-bg" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </div>
          <h1 className="text-3xl font-bold text-gradient mb-2">Crypto Sentinel</h1>
          <p className="text-crypto-text-secondary">
            Real-time cryptocurrency monitoring and alerts
          </p>
        </div>

        <div className="card">
          <h2 className="text-xl font-semibold text-center mb-6">Sign in to continue</h2>

          {isLoggingIn ? (
            <div className="flex flex-col items-center py-8">
              <div className="w-12 h-12 border-4 border-crypto-accent border-t-transparent rounded-full animate-spin mb-4" />
              <p className="text-crypto-text-secondary">Authenticating...</p>
            </div>
          ) : (
            <>
              <div className="flex justify-center mb-6" ref={telegramContainerRef} />

              {loginError && (
                <div className="p-3 bg-crypto-loss/20 border border-crypto-loss rounded-lg text-crypto-loss text-sm text-center mb-4">
                  Authentication failed. Please try again.
                </div>
              )}

              <div className="relative my-6">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t border-crypto-border" />
                </div>
                <div className="relative flex justify-center text-sm">
                  <span className="px-2 bg-crypto-bg-secondary text-crypto-text-muted">
                    Secure login via Telegram
                  </span>
                </div>
              </div>

              <div className="text-center text-sm text-crypto-text-secondary">
                <p className="mb-4">
                  By signing in, you agree to our Terms of Service and Privacy Policy.
                </p>
                <p>
                  Don't have a Telegram account?{' '}
                  <a
                    href="https://telegram.org"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-crypto-accent hover:underline"
                  >
                    Get Telegram
                  </a>
                </p>
              </div>
            </>
          )}
        </div>

        <div className="mt-8 grid grid-cols-3 gap-4">
          <div className="card p-4 text-center">
            <div className="text-2xl font-bold text-crypto-accent">24/7</div>
            <div className="text-xs text-crypto-text-muted">Monitoring</div>
          </div>
          <div className="card p-4 text-center">
            <div className="text-2xl font-bold text-crypto-gain">100+</div>
            <div className="text-xs text-crypto-text-muted">Coins</div>
          </div>
          <div className="card p-4 text-center">
            <div className="text-2xl font-bold text-crypto-accent">Real-time</div>
            <div className="text-xs text-crypto-text-muted">Alerts</div>
          </div>
        </div>

        <p className="text-center text-crypto-text-muted text-sm mt-8">
          © 2024 Crypto Sentinel Bot. All rights reserved.
        </p>
      </div>
    </div>
  )
}
