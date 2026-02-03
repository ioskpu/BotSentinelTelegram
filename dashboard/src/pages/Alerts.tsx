import AlertList from '../components/alerts/AlertList'
import AlertsChart from '../components/charts/AlertsChart'
import { useAlerts } from '../hooks/useAlerts'

export default function Alerts() {
  const { alerts, total } = useAlerts({ pageSize: 100 })

  const activeCount = alerts.filter((a) => a.is_active && !a.triggered_at).length
  const triggeredCount = alerts.filter((a) => !!a.triggered_at).length

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Alerts</h1>
          <p className="text-crypto-text-secondary">
            Manage your price alerts and notifications
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="stat-label">Total Alerts</p>
              <p className="stat-value text-crypto-accent">{total}</p>
            </div>
            <div className="p-3 rounded-lg bg-crypto-accent/20">
              <svg className="w-6 h-6 text-crypto-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
              </svg>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="stat-label">Active</p>
              <p className="stat-value text-crypto-gain">{activeCount}</p>
            </div>
            <div className="p-3 rounded-lg bg-crypto-gain/20">
              <svg className="w-6 h-6 text-crypto-gain" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="stat-label">Triggered</p>
              <p className="stat-value text-crypto-loss">{triggeredCount}</p>
            </div>
            <div className="p-3 rounded-lg bg-crypto-loss/20">
              <svg className="w-6 h-6 text-crypto-loss" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <div className="card">
            <h3 className="text-lg font-semibold mb-4">Your Alerts</h3>
            <AlertList />
          </div>
        </div>

        <div className="space-y-6">
          <AlertsChart alerts={alerts} type="pie" height={200} />
          <AlertsChart alerts={alerts} type="bar" height={200} />
        </div>
      </div>
    </div>
  )
}
