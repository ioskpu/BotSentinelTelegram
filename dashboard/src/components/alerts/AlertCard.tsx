import React from 'react'
import { Alert } from '../../types'

interface AlertCardProps {
  alert: Alert
  onToggle: () => void
  onDelete: () => void
  isDeleting?: boolean
}

const typeLabels: Record<Alert['alert_type'], string> = {
  price_above: 'Price Above',
  price_below: 'Price Below',
  percent_change: 'Percent Change',
  volume_spike: 'Volume Spike',
}

const typeIcons: Record<Alert['alert_type'], React.ReactElement> = {
  price_above: (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
    </svg>
  ),
  price_below: (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 17h8m0 0V9m0 8l-8-8-4 4-6-6" />
    </svg>
  ),
  percent_change: (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z" />
    </svg>
  ),
  volume_spike: (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
    </svg>
  ),
}

export default function AlertCard({ alert, onToggle, onDelete, isDeleting }: AlertCardProps) {
  const isTriggered = !!alert.triggered_at

  const formatValue = (value: number, type: Alert['alert_type']) => {
    if (type === 'percent_change') {
      return `${value > 0 ? '+' : ''}${value}%`
    }
    if (type === 'volume_spike') {
      return `${value}x`
    }
    return `$${value.toLocaleString()}`
  }

  return (
    <div className={`card transition-all ${isTriggered ? 'border-crypto-gain' : ''}`}>
      <div className="flex items-start justify-between">
        <div className="flex items-start gap-4">
          <div className={`p-3 rounded-lg ${
            isTriggered 
              ? 'bg-crypto-gain/20 text-crypto-gain' 
              : alert.is_active 
                ? 'bg-crypto-accent/20 text-crypto-accent'
                : 'bg-crypto-bg-tertiary text-crypto-text-muted'
          }`}>
            {typeIcons[alert.alert_type]}
          </div>

          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="font-mono text-lg font-bold">{alert.coin_symbol}</span>
              <span className={`badge ${
                isTriggered 
                  ? 'badge-gain' 
                  : alert.is_active 
                    ? 'badge-neutral' 
                    : 'bg-crypto-bg-tertiary text-crypto-text-muted'
              }`}>
                {isTriggered ? 'Triggered' : alert.is_active ? 'Active' : 'Paused'}
              </span>
            </div>
            
            <p className="text-sm text-crypto-text-secondary mb-2">
              {typeLabels[alert.alert_type]}: {formatValue(alert.threshold, alert.alert_type)}
            </p>

            <p className="text-xs text-crypto-text-muted mt-2">
              Created {new Date(alert.created_at).toLocaleDateString()}
              {alert.triggered_at && (
                <> • Triggered {new Date(alert.triggered_at).toLocaleString()}</>
              )}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={onToggle}
            className={`p-2 rounded-lg transition-colors ${
              alert.is_active
                ? 'bg-crypto-gain/20 text-crypto-gain hover:bg-crypto-gain/30'
                : 'bg-crypto-bg-tertiary text-crypto-text-muted hover:bg-crypto-border'
            }`}
            title={alert.is_active ? 'Pause alert' : 'Activate alert'}
          >
            {alert.is_active ? (
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 9v6m4-6v6m7-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            ) : (
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            )}
          </button>

          <button
            onClick={onDelete}
            disabled={isDeleting}
            className="p-2 rounded-lg bg-crypto-loss/20 text-crypto-loss hover:bg-crypto-loss/30 transition-colors disabled:opacity-50"
            title="Delete alert"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  )
}
