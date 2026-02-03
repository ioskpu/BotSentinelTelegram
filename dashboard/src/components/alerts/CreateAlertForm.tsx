import React, { useState } from 'react'
import { useAlerts } from '../../hooks/useAlerts'
import { Alert } from '../../types'

interface CreateAlertFormProps {
  onClose: () => void
}

const alertTypes: { value: Alert['alert_type']; label: string; description: string }[] = [
  { value: 'price_above', label: 'Price Above', description: 'Notify when price goes above target' },
  { value: 'price_below', label: 'Price Below', description: 'Notify when price drops below target' },
  { value: 'percent_change', label: 'Percent Change', description: 'Notify on percentage change' },
  { value: 'volume_spike', label: 'Volume Spike', description: 'Notify on volume surge (e.g. 2x average)' },
]

const coinMap: Record<string, { id: string; symbol: string }> = {
  SOL: { id: 'solana', symbol: 'SOL' },
  XLM: { id: 'stellar', symbol: 'XLM' },
  BTC: { id: 'bitcoin', symbol: 'BTC' },
  ETH: { id: 'ethereum', symbol: 'ETH' },
  ADA: { id: 'cardano', symbol: 'ADA' },
  DOT: { id: 'polkadot', symbol: 'DOT' },
  AVAX: { id: 'avalanche-2', symbol: 'AVAX' },
  MATIC: { id: 'matic-network', symbol: 'MATIC' },
  ATOM: { id: 'cosmos', symbol: 'ATOM' },
  ALGO: { id: 'algorand', symbol: 'ALGO' },
  DOGE: { id: 'dogecoin', symbol: 'DOGE' },
  SHIB: { id: 'shiba-inu', symbol: 'SHIB' },
  PEPE: { id: 'pepe', symbol: 'PEPE' },
  UNI: { id: 'uniswap', symbol: 'UNI' },
  LINK: { id: 'chainlink', symbol: 'LINK' },
  AAVE: { id: 'aave', symbol: 'AAVE' },
  XRP: { id: 'ripple', symbol: 'XRP' },
  LTC: { id: 'litecoin', symbol: 'LTC' },
  BNB: { id: 'binancecoin', symbol: 'BNB' },
  ACU: { id: 'acurast', symbol: 'ACU' },
}

const popularSymbols = Object.keys(coinMap)

export default function CreateAlertForm({ onClose }: CreateAlertFormProps) {
  const { createAlert, isCreating } = useAlerts()
  const [formData, setFormData] = useState({
    symbol: '',
    type: 'price_above' as Alert['alert_type'],
    threshold: 0,
  })
  const [error, setError] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    const coin = coinMap[formData.symbol.toUpperCase()]
    if (!coin) {
      setError('Please select a supported coin')
      return
    }

    if (formData.threshold <= 0) {
      setError('Please enter a valid target value')
      return
    }

    try {
      await createAlert({
        coin_id: coin.id,
        coin_symbol: coin.symbol,
        alert_type: formData.type,
        threshold: formData.threshold,
      })
      onClose()
    } catch (err) {
      setError('Failed to create alert. Please try again.')
    }
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-crypto-bg-secondary border border-crypto-border rounded-xl max-w-md w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6 border-b border-crypto-border flex items-center justify-between">
          <h2 className="text-xl font-bold">Create Alert</h2>
          <button
            onClick={onClose}
            className="p-2 rounded-lg hover:bg-crypto-bg-tertiary transition-colors"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          <div>
            <label className="label">Symbol</label>
            <input
              type="text"
              value={formData.symbol}
              onChange={(e) => setFormData({ ...formData, symbol: e.target.value.toUpperCase() })}
              placeholder="BTC"
              className="input font-mono"
            />
            <div className="flex flex-wrap gap-2 mt-2">
              {popularSymbols.slice(0, 10).map((symbol) => (
                <button
                  key={symbol}
                  type="button"
                  onClick={() => setFormData({ ...formData, symbol })}
                  className={`px-2 py-1 text-xs rounded transition-colors ${
                    formData.symbol === symbol
                      ? 'bg-crypto-accent text-crypto-bg'
                      : 'bg-crypto-bg-tertiary text-crypto-text-secondary hover:bg-crypto-border'
                  }`}
                >
                  {symbol}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="label">Alert Type</label>
            <div className="space-y-2">
              {alertTypes.map((type) => (
                <label
                  key={type.value}
                  className={`flex items-start gap-3 p-3 rounded-lg border cursor-pointer transition-colors ${
                    formData.type === type.value
                      ? 'border-crypto-accent bg-crypto-accent/10'
                      : 'border-crypto-border hover:border-crypto-accent/50'
                  }`}
                >
                  <input
                    type="radio"
                    name="alertType"
                    value={type.value}
                    checked={formData.type === type.value}
                    onChange={(e) => setFormData({ ...formData, type: e.target.value as Alert['alert_type'] })}
                    className="mt-1"
                  />
                  <div>
                    <p className="font-medium">{type.label}</p>
                    <p className="text-sm text-crypto-text-secondary">{type.description}</p>
                  </div>
                </label>
              ))}
            </div>
          </div>

          <div>
            <label className="label">
              {formData.type === 'percent_change' ? 'Percentage (%)' : 
               formData.type === 'volume_spike' ? 'Multiplier (e.g. 2)' : 
               'Target Price ($)'}
            </label>
            <input
              type="number"
              value={formData.threshold || ''}
              onChange={(e) => setFormData({ ...formData, threshold: parseFloat(e.target.value) || 0 })}
              placeholder={
                formData.type === 'percent_change' ? '5' : 
                formData.type === 'volume_spike' ? '2' : 
                '50000'
              }
              step={
                formData.type === 'percent_change' ? '0.1' : 
                formData.type === 'volume_spike' ? '0.5' : 
                '0.01'
              }
              className="input font-mono"
            />
          </div>

          {error && (
            <div className="p-3 bg-crypto-loss/20 border border-crypto-loss rounded-lg text-crypto-loss text-sm">
              {error}
            </div>
          )}

          <div className="flex gap-3">
            <button
              type="button"
              onClick={onClose}
              className="btn-secondary flex-1"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isCreating}
              className="btn-primary flex-1"
            >
              {isCreating ? 'Creating...' : 'Create Alert'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
