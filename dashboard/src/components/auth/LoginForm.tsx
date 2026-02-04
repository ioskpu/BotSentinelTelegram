import { useState } from 'react'
import { Link } from 'react-router-dom'

interface FormErrors {
  general?: string
}

export default function LoginForm() {
  const [isLoading, setIsLoading] = useState(false)
  const [errors, setErrors] = useState<FormErrors>({})

  const handleTelegramLogin = async () => {
    setIsLoading(true)
    setErrors({})

    try {
      // In production, this would be handled by Telegram Login Widget
      const botUsername = import.meta.env.VITE_TELEGRAM_BOT_USERNAME || 'CryptoSentinelBot'
      window.location.href = `https://t.me/${botUsername}?start=login`
    } catch (error) {
      setErrors({ general: 'Failed to initiate Telegram login' })
      setIsLoading(false)
    }
  }

  return (
    <div className="w-full max-w-md space-y-8">
      <div className="text-center">
        <div className="flex justify-center mb-6">
          <div className="w-20 h-20 bg-gradient-to-br from-crypto-accent via-crypto-purple to-crypto-gain rounded-2xl flex items-center justify-center shadow-crypto-lg animate-glow">
            <svg className="w-12 h-12 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </div>
        </div>
        <h2 className="text-3xl font-bold text-gradient">Welcome Back</h2>
        <p className="mt-2 text-crypto-text-secondary">
          Sign in to access your crypto dashboard
        </p>
      </div>

      {errors.general && (
        <div className="bg-crypto-loss/10 border border-crypto-loss/30 rounded-lg p-4">
          <p className="text-crypto-loss text-sm">{errors.general}</p>
        </div>
      )}

      <div className="card space-y-6">
        <button
          onClick={handleTelegramLogin}
          disabled={isLoading}
          className="w-full flex items-center justify-center gap-3 bg-[#0088cc] hover:bg-[#0077b5] text-white py-4 px-6 rounded-xl font-semibold transition-all duration-300 transform hover:scale-[1.02] disabled:opacity-50 disabled:transform-none"
        >
          {isLoading ? (
            <div className="w-6 h-6 border-2 border-white border-t-transparent rounded-full animate-spin" />
          ) : (
            <>
              <svg className="w-6 h-6" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 0C5.373 0 0 5.373 0 12s5.373 12 12 12 12-5.373 12-12S18.627 0 12 0zm5.894 8.221l-1.97 9.28c-.145.658-.537.818-1.084.508l-3-2.21-1.446 1.394c-.16.16-.295.295-.605.295l.213-3.053 5.56-5.023c.242-.213-.054-.334-.373-.121l-6.869 4.326-2.96-.924c-.64-.203-.658-.64.135-.954l11.566-4.458c.538-.196 1.006.128.832.94z"/>
              </svg>
              Sign in with Telegram
            </>
          )}
        </button>

        <div className="relative">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t border-crypto-border" />
          </div>
          <div className="relative flex justify-center text-sm">
            <span className="px-4 bg-crypto-bg-secondary text-crypto-text-muted">
              Secure authentication
            </span>
          </div>
        </div>

        <div className="text-center text-sm">
          <p className="text-crypto-text-muted">
            Don't have an account?{' '}
            <Link to="/register" className="text-crypto-accent hover:text-crypto-accent-hover font-medium transition-colors">
              Create one
            </Link>
          </p>
        </div>
      </div>

      <div className="flex items-center justify-center gap-2 text-xs text-crypto-text-muted">
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
        </svg>
        <span>End-to-end encrypted</span>
      </div>
    </div>
  )
}
