import { useState } from 'react'
import { useAlerts } from '../../hooks/useAlerts'
import AlertCard from './AlertCard'
import CreateAlertForm from './CreateAlertForm'

interface AlertListProps {
  showCreateButton?: boolean
  limit?: number
}

export default function AlertList({ showCreateButton = true, limit }: AlertListProps) {
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [filter, setFilter] = useState<'all' | 'active' | 'triggered'>('all')
  
  const { alerts, isLoading, deleteAlert, toggleAlert, isDeleting } = useAlerts({
    isActive: filter === 'active' ? true : filter === 'triggered' ? false : undefined,
    pageSize: limit,
  })

  const filteredAlerts = alerts.filter((alert) => {
    if (filter === 'active') return alert.isActive && !alert.isTriggered
    if (filter === 'triggered') return alert.isTriggered
    return true
  })

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <button
            onClick={() => setFilter('all')}
            className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
              filter === 'all'
                ? 'bg-crypto-accent text-crypto-bg'
                : 'text-crypto-text-secondary hover:bg-crypto-bg-tertiary'
            }`}
          >
            All
          </button>
          <button
            onClick={() => setFilter('active')}
            className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
              filter === 'active'
                ? 'bg-crypto-accent text-crypto-bg'
                : 'text-crypto-text-secondary hover:bg-crypto-bg-tertiary'
            }`}
          >
            Active
          </button>
          <button
            onClick={() => setFilter('triggered')}
            className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
              filter === 'triggered'
                ? 'bg-crypto-accent text-crypto-bg'
                : 'text-crypto-text-secondary hover:bg-crypto-bg-tertiary'
            }`}
          >
            Triggered
          </button>
        </div>

        {showCreateButton && (
          <button
            onClick={() => setShowCreateForm(true)}
            className="btn-primary flex items-center gap-2"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            Create Alert
          </button>
        )}
      </div>

      {isLoading ? (
        <div className="space-y-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="card animate-pulse">
              <div className="h-20 bg-crypto-bg-tertiary rounded-lg" />
            </div>
          ))}
        </div>
      ) : filteredAlerts.length === 0 ? (
        <div className="card text-center py-12">
          <svg className="w-16 h-16 mx-auto text-crypto-text-muted mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
          </svg>
          <h3 className="text-lg font-semibold mb-2">No alerts found</h3>
          <p className="text-crypto-text-secondary mb-4">
            Create your first alert to get notified of price changes
          </p>
          <button
            onClick={() => setShowCreateForm(true)}
            className="btn-primary"
          >
            Create Alert
          </button>
        </div>
      ) : (
        <div className="space-y-4">
          {filteredAlerts.map((alert) => (
            <AlertCard
              key={alert.id}
              alert={alert}
              onToggle={() => toggleAlert(alert.id)}
              onDelete={() => deleteAlert(alert.id)}
              isDeleting={isDeleting}
            />
          ))}
        </div>
      )}

      {showCreateForm && (
        <CreateAlertForm onClose={() => setShowCreateForm(false)} />
      )}
    </div>
  )
}
