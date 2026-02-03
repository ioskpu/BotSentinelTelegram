import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useAlerts } from '@/hooks/useAlerts'
import { Alert } from '@/types'
import { alertsService } from '@/services/alerts.service'
import { useMutation, useQueryClient } from '@tanstack/react-query'

export default function AlertsPanel() {
  const { alerts, isLoading } = useAlerts({ pageSize: 10 })
  const [filter, setFilter] = useState<'all' | 'active' | 'triggered'>('all')
  const queryClient = useQueryClient()

  const toggleMutation = useMutation({
    mutationFn: alertsService.toggleAlert,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alerts'] })
    },
  })

  const deleteMutation = useMutation({
    mutationFn: alertsService.deleteAlert,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alerts'] })
    },
  })

  const filteredAlerts = alerts.filter(alert => {
    if (filter === 'active') return alert.isActive && !alert.isTriggered
    if (filter === 'triggered') return alert.isTriggered
    return true
  })

  const getAlertTypeIcon = (type: Alert['type']) => {
    switch (type) {
      case 'price_above':
        return <span className="text-crypto-gain">↑</span>
      case 'price_below':
        return <span className="text-crypto-loss">↓</span>
      case 'percent_change':
        return <span className="text-crypto-purple">%</span>
      case 'volume_spike':
        return <span className="text-crypto-accent">📊</span>
      default:
        return <span>🔔</span>
    }
  }

  const getAlertTypeLabel = (type: Alert['type']) => {
    switch (type) {
      case 'price_above': return 'Above'
      case 'price_below': return 'Below'
      case 'percent_change': return 'Change'
      case 'volume_spike': return 'Volume'
      default: return type
    }
  }

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold">Active Alerts</h3>
        <div className="flex items-center gap-2">
          <div className="flex bg-crypto-bg-tertiary rounded-lg p-1">
            {(['all', 'active', 'triggered'] as const).map((f) => (
              <button
                key={f}
                onClick={() => setFilter(f)}
                className={`px-3 py-1 text-xs font-medium rounded-md transition-colors ${
                  filter === f
                    ? 'bg-crypto-accent text-crypto-bg'
                    : 'text-crypto-text-secondary hover:text-crypto-text'
                }`}
              >
                {f.charAt(0).toUpperCase() + f.slice(1)}
              </button>
            ))}
          </div>
          <Link
            to="/alerts"
            className="text-crypto-accent hover:text-crypto-accent-hover text-sm font-medium"
          >
            View All →
          </Link>
        </div>
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center py-8">
          <div className="w-8 h-8 border-2 border-crypto-accent border-t-transparent rounded-full animate-spin" />
        </div>
      ) : filteredAlerts.length === 0 ? (
        <div className="text-center py-8 text-crypto-text-muted">
          <svg className="w-12 h-12 mx-auto mb-2 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
          </svg>
          <p>No {filter !== 'all' ? filter : ''} alerts found</p>
          <Link to="/alerts" className="text-crypto-accent hover:underline text-sm mt-2 inline-block">
            Create your first alert
          </Link>
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-crypto-border">
                <th className="table-header pb-3">Coin</th>
                <th className="table-header pb-3">Type</th>
                <th className="table-header pb-3 text-right">Target</th>
                <th className="table-header pb-3 text-right">Current</th>
                <th className="table-header pb-3 text-center">Status</th>
                <th className="table-header pb-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-crypto-border">
              {filteredAlerts.map((alert) => (
                <tr key={alert.id} className="hover:bg-crypto-bg-tertiary/50 transition-colors">
                  <td className="table-cell">
                    <div className="flex items-center gap-2">
                      <div className="w-8 h-8 rounded-full bg-crypto-bg-tertiary flex items-center justify-center font-mono font-bold text-xs text-crypto-accent">
                        {alert.symbol.slice(0, 3)}
                      </div>
                      <span className="font-medium">{alert.symbol}</span>
                    </div>
                  </td>
                  <td className="table-cell">
                    <div className="flex items-center gap-1">
                      {getAlertTypeIcon(alert.type)}
                      <span className="text-crypto-text-secondary text-sm">
                        {getAlertTypeLabel(alert.type)}
                      </span>
                    </div>
                  </td>
                  <td className="table-cell text-right font-mono">
                    ${alert.targetValue.toLocaleString()}
                  </td>
                  <td className="table-cell text-right font-mono text-crypto-text-secondary">
                    {alert.currentValue ? `$${alert.currentValue.toLocaleString()}` : '-'}
                  </td>
                  <td className="table-cell text-center">
                    {alert.isTriggered ? (
                      <span className="badge-gain">Triggered</span>
                    ) : alert.isActive ? (
                      <span className="badge-neutral">Active</span>
                    ) : (
                      <span className="badge bg-crypto-text-muted/20 text-crypto-text-muted">Paused</span>
                    )}
                  </td>
                  <td className="table-cell text-right">
                    <div className="flex items-center justify-end gap-1">
                      <button
                        onClick={() => toggleMutation.mutate(alert.id)}
                        disabled={toggleMutation.isPending}
                        className="p-1.5 rounded hover:bg-crypto-bg-tertiary transition-colors"
                        title={alert.isActive ? 'Pause' : 'Resume'}
                      >
                        {alert.isActive ? (
                          <svg className="w-4 h-4 text-crypto-text-secondary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 9v6m4-6v6m7-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                        ) : (
                          <svg className="w-4 h-4 text-crypto-gain" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                        )}
                      </button>
                      <button
                        onClick={() => {
                          if (confirm('Delete this alert?')) {
                            deleteMutation.mutate(alert.id)
                          }
                        }}
                        disabled={deleteMutation.isPending}
                        className="p-1.5 rounded hover:bg-crypto-loss/10 transition-colors"
                        title="Delete"
                      >
                        <svg className="w-4 h-4 text-crypto-loss" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg>
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
