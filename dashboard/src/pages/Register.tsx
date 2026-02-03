import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'

export default function Register() {
  const navigate = useNavigate()
  const [isLoading, setIsLoading] = useState(false)

  const handleTelegramAuth = () => {
    setIsLoading(true)
    // Redirect to Telegram OAuth
    const botUsername = import.meta.env.VITE_TELEGRAM_BOT_USERNAME || 'CryptoSentinelBot'
    const callbackUrl = `${window.location.origin}/auth/callback`
    window.location.href = `https://t.me/${botUsername}?start=register`
  }

  return (
    <div className="min-h-screen bg-crypto-bg flex items-center justify-center px-4">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <div className="flex justify-center mb-4">
            <div className="w-16 h-16 bg-gradient-to-br from-crypto-accent to-purple-500 rounded-2xl flex items-center justify-center">
              <svg className="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
              </svg>
            </div>
          </div>
          <h2 className="text-3xl font-bold text-crypto-text">Create Account</h2>
          <p className="mt-2 text-crypto-text-secondary">
            Join Crypto Sentinel to track your portfolio
          </p>
        </div>

        <div className="bg-crypto-bg-secondary rounded-xl p-8 border border-crypto-border">
          <button
            onClick={handleTelegramAuth}
            disabled={isLoading}
            className="w-full flex items-center justify-center gap-3 bg-[#0088cc] hover:bg-[#0077b5] text-white py-3 px-4 rounded-lg font-medium transition-colors disabled:opacity-50"
          >
            {isLoading ? (
              <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
            ) : (
              <>
                <svg className="w-6 h-6" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 0C5.373 0 0 5.373 0 12s5.373 12 12 12 12-5.373 12-12S18.627 0 12 0zm5.894 8.221l-1.97 9.28c-.145.658-.537.818-1.084.508l-3-2.21-1.446 1.394c-.16.16-.295.295-.605.295l.213-3.053 5.56-5.023c.242-.213-.054-.334-.373-.121l-6.869 4.326-2.96-.924c-.64-.203-.658-.64.135-.954l11.566-4.458c.538-.196 1.006.128.832.94z"/>
                </svg>
                Register with Telegram
              </>
            )}
          </button>

          <div className="mt-6 text-center">
            <p className="text-crypto-text-muted text-sm">
              Already have an account?{' '}
              <Link to="/login" className="text-crypto-accent hover:underline">
                Sign in
              </Link>
            </p>
          </div>
        </div>

        <div className="text-center text-sm text-crypto-text-muted">
          <p>
            By registering, you agree to our{' '}
            <Link to="/terms" className="text-crypto-accent hover:underline">Terms</Link>
            {' '}and{' '}
            <Link to="/privacy" className="text-crypto-accent hover:underline">Privacy Policy</Link>
          </p>
        </div>
      </div>
    </div>
  )
}
