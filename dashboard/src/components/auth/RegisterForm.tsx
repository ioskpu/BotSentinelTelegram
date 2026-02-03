import { useState } from 'react'
import { Link } from 'react-router-dom'

export default function RegisterForm() {
  const [isLoading, setIsLoading] = useState(false)
  const [step, setStep] = useState<'initial' | 'pending'>('initial')

  const handleTelegramRegister = () => {
    setIsLoading(true)
    const botUsername = import.meta.env.VITE_TELEGRAM_BOT_USERNAME || 'CryptoSentinelBot'
    window.location.href = `https://t.me/${botUsername}?start=register`
  }

  return (
    <div className="w-full max-w-md space-y-8">
      <div className="text-center">
        <div className="flex justify-center mb-6">
          <div className="w-20 h-20 bg-gradient-to-br from-crypto-purple via-crypto-accent to-crypto-blue rounded-2xl flex items-center justify-center shadow-crypto-lg">
            <svg className="w-12 h-12 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
            </svg>
          </div>
        </div>
        <h2 className="text-3xl font-bold text-gradient">Join Crypto Sentinel</h2>
        <p className="mt-2 text-crypto-text-secondary">
          Create your account and start tracking
        </p>
      </div>

      <div className="card space-y-6">
        <div className="space-y-4">
          <div className="flex items-start gap-4 p-4 bg-crypto-bg-tertiary rounded-lg">
            <div className="w-8 h-8 rounded-full bg-crypto-accent/20 flex items-center justify-center flex-shrink-0">
              <span className="text-crypto-accent font-bold">1</span>
            </div>
            <div>
              <p className="font-medium">Connect with Telegram</p>
              <p className="text-sm text-crypto-text-muted">
                Use your Telegram account for secure authentication
              </p>
            </div>
          </div>

          <div className="flex items-start gap-4 p-4 bg-crypto-bg-tertiary rounded-lg">
            <div className="w-8 h-8 rounded-full bg-crypto-purple/20 flex items-center justify-center flex-shrink-0">
              <span className="text-crypto-purple font-bold">2</span>
            </div>
            <div>
              <p className="font-medium">Set up your alerts</p>
              <p className="text-sm text-crypto-text-muted">
                Configure price alerts for your favorite coins
              </p>
            </div>
          </div>

          <div className="flex items-start gap-4 p-4 bg-crypto-bg-tertiary rounded-lg">
            <div className="w-8 h-8 rounded-full bg-crypto-gain/20 flex items-center justify-center flex-shrink-0">
              <span className="text-crypto-gain font-bold">3</span>
            </div>
            <div>
              <p className="font-medium">Get notified instantly</p>
              <p className="text-sm text-crypto-text-muted">
                Receive real-time alerts via Telegram and web
              </p>
            </div>
          </div>
        </div>

        <button
          onClick={handleTelegramRegister}
          disabled={isLoading}
          className="w-full flex items-center justify-center gap-3 bg-gradient-to-r from-crypto-accent to-crypto-purple text-white py-4 px-6 rounded-xl font-semibold transition-all duration-300 transform hover:scale-[1.02] hover:shadow-crypto-lg disabled:opacity-50"
        >
          {isLoading ? (
            <div className="w-6 h-6 border-2 border-white border-t-transparent rounded-full animate-spin" />
          ) : (
            <>
              <svg className="w-6 h-6" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 0C5.373 0 0 5.373 0 12s5.373 12 12 12 12-5.373 12-12S18.627 0 12 0zm5.894 8.221l-1.97 9.28c-.145.658-.537.818-1.084.508l-3-2.21-1.446 1.394c-.16.16-.295.295-.605.295l.213-3.053 5.56-5.023c.242-.213-.054-.334-.373-.121l-6.869 4.326-2.96-.924c-.64-.203-.658-.64.135-.954l11.566-4.458c.538-.196 1.006.128.832.94z"/>
              </svg>
              Get Started with Telegram
            </>
          )}
        </button>

        <p className="text-center text-sm text-crypto-text-muted">
          Already have an account?{' '}
          <Link to="/login" className="text-crypto-accent hover:underline font-medium">
            Sign in
          </Link>
        </p>
      </div>

      <p className="text-center text-xs text-crypto-text-muted">
        By creating an account, you agree to our{' '}
        <Link to="/terms" className="text-crypto-accent hover:underline">Terms of Service</Link>
        {' '}and{' '}
        <Link to="/privacy" className="text-crypto-accent hover:underline">Privacy Policy</Link>
      </p>
    </div>
  )
}
