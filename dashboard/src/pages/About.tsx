import { Link } from 'react-router-dom'

const features = [
  {
    icon: '🔔',
    title: 'Smart Alerts',
    description: 'Set price alerts for any cryptocurrency and get notified instantly via Telegram.'
  },
  {
    icon: '📊',
    title: 'Portfolio Tracking',
    description: 'Track your crypto portfolio with real-time P&L calculations and analytics.'
  },
  {
    icon: '🐋',
    title: 'Whale Monitoring',
    description: 'Monitor large transactions and whale movements across multiple blockchains.'
  },
  {
    icon: '⚡',
    title: 'Real-time Updates',
    description: 'Get live price updates and market data streamed directly to your dashboard.'
  },
  {
    icon: '🔒',
    title: 'Secure',
    description: 'Your data is encrypted and securely stored. We never share your information.'
  },
  {
    icon: '🌐',
    title: 'Multi-chain',
    description: 'Support for Ethereum, Solana, Stellar, and more blockchain networks.'
  },
]

export default function About() {
  return (
    <div className="min-h-screen bg-crypto-bg">
      {/* Header */}
      <header className="border-b border-crypto-border">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-2">
            <div className="w-10 h-10 bg-gradient-to-br from-crypto-accent to-purple-500 rounded-xl flex items-center justify-center">
              <span className="text-xl">🛡️</span>
            </div>
            <span className="text-xl font-bold text-crypto-text">Crypto Sentinel</span>
          </Link>
          <nav className="flex items-center gap-4">
            <Link to="/login" className="text-crypto-text-secondary hover:text-crypto-text transition-colors">
              Login
            </Link>
            <Link to="/register" className="bg-crypto-accent hover:bg-crypto-accent-hover text-crypto-bg px-4 py-2 rounded-lg font-medium transition-colors">
              Get Started
            </Link>
          </nav>
        </div>
      </header>

      {/* Hero */}
      <section className="py-20 px-4">
        <div className="max-w-4xl mx-auto text-center">
          <h1 className="text-5xl font-bold text-crypto-text mb-6">
            Your Crypto Guardian
          </h1>
          <p className="text-xl text-crypto-text-secondary mb-8 max-w-2xl mx-auto">
            Monitor cryptocurrency markets, set intelligent alerts, track your portfolio, 
            and stay ahead of the market with real-time insights.
          </p>
          <div className="flex items-center justify-center gap-4">
            <Link to="/register" className="bg-crypto-accent hover:bg-crypto-accent-hover text-crypto-bg px-8 py-3 rounded-lg font-medium text-lg transition-colors">
              Start Free
            </Link>
            <a href="https://t.me/CryptoSentinelBot" target="_blank" rel="noopener noreferrer" className="border border-crypto-border hover:border-crypto-accent text-crypto-text px-8 py-3 rounded-lg font-medium text-lg transition-colors">
              Try on Telegram
            </a>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="py-20 px-4 bg-crypto-bg-secondary">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl font-bold text-crypto-text text-center mb-12">
            Powerful Features
          </h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <div key={index} className="bg-crypto-bg p-6 rounded-xl border border-crypto-border hover:border-crypto-accent transition-colors">
                <div className="text-4xl mb-4">{feature.icon}</div>
                <h3 className="text-xl font-semibold text-crypto-text mb-2">{feature.title}</h3>
                <p className="text-crypto-text-secondary">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 px-4">
        <div className="max-w-3xl mx-auto text-center">
          <h2 className="text-3xl font-bold text-crypto-text mb-4">
            Ready to Get Started?
          </h2>
          <p className="text-crypto-text-secondary mb-8">
            Join thousands of traders using Crypto Sentinel to stay informed.
          </p>
          <Link to="/register" className="inline-block bg-gradient-to-r from-crypto-accent to-purple-500 text-white px-8 py-3 rounded-lg font-medium text-lg hover:opacity-90 transition-opacity">
            Create Free Account
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-crypto-border py-8 px-4">
        <div className="max-w-6xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="text-crypto-text-muted">
            © 2024 Crypto Sentinel. All rights reserved.
          </div>
          <div className="flex items-center gap-6">
            <Link to="/terms" className="text-crypto-text-muted hover:text-crypto-text transition-colors">Terms</Link>
            <Link to="/privacy" className="text-crypto-text-muted hover:text-crypto-text transition-colors">Privacy</Link>
            <a href="https://github.com/ioskpu/BotSentinelTelegram" target="_blank" rel="noopener noreferrer" className="text-crypto-text-muted hover:text-crypto-text transition-colors">GitHub</a>
          </div>
        </div>
      </footer>
    </div>
  )
}
