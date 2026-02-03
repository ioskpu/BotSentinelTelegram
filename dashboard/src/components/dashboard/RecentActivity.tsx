import { useQuery } from '@tanstack/react-query'
import api, { endpoints } from '../../config/api'
import { Activity, ApiResponse } from '../../types'

const activityIcons: Record<Activity['type'], JSX.Element> = {
  alert_triggered: (
    <svg className="w-5 h-5 text-crypto-gain" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
    </svg>
  ),
  alert_created: (
    <svg className="w-5 h-5 text-crypto-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
    </svg>
  ),
  trade: (
    <svg className="w-5 h-5 text-crypto-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
    </svg>
  ),
  deposit: (
    <svg className="w-5 h-5 text-crypto-gain" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m0 0l-4-4m4 4l4-4" />
    </svg>
  ),
  withdrawal: (
    <svg className="w-5 h-5 text-crypto-loss" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 20V4m0 0l-4 4m4-4l4 4" />
    </svg>
  ),
}

export default function RecentActivity() {
  const { data: activities, isLoading } = useQuery({
    queryKey: ['activity'],
    queryFn: async () => {
      const response = await api.get<ApiResponse<Activity[]>>(endpoints.dashboard.activity)
      return response.data.data
    },
  })

  if (isLoading) {
    return (
      <div className="card">
        <h3 className="text-lg font-semibold mb-4">Recent Activity</h3>
        <div className="space-y-4">
          {[1, 2, 3, 4, 5].map((i) => (
            <div key={i} className="flex items-center gap-4 animate-pulse">
              <div className="w-10 h-10 rounded-full bg-crypto-bg-tertiary" />
              <div className="flex-1 space-y-2">
                <div className="h-4 bg-crypto-bg-tertiary rounded w-3/4" />
                <div className="h-3 bg-crypto-bg-tertiary rounded w-1/2" />
              </div>
            </div>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="card">
      <h3 className="text-lg font-semibold mb-4">Recent Activity</h3>
      {!activities || activities.length === 0 ? (
        <div className="text-center py-8 text-crypto-text-muted">
          No recent activity
        </div>
      ) : (
        <div className="space-y-4">
          {activities.slice(0, 10).map((activity) => (
            <div
              key={activity.id}
              className="flex items-start gap-4 p-3 rounded-lg hover:bg-crypto-bg-tertiary transition-colors"
            >
              <div className="p-2 rounded-lg bg-crypto-bg-tertiary">
                {activityIcons[activity.type]}
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <p className="font-medium truncate">{activity.title}</p>
                  {activity.symbol && (
                    <span className="font-mono text-sm text-crypto-accent">{activity.symbol}</span>
                  )}
                </div>
                <p className="text-sm text-crypto-text-secondary truncate">
                  {activity.description}
                </p>
                <p className="text-xs text-crypto-text-muted mt-1">
                  {new Date(activity.timestamp).toLocaleString()}
                </p>
              </div>
              {activity.value !== undefined && (
                <div className="text-right">
                  <p className="font-mono font-semibold">
                    ${activity.value.toLocaleString()}
                  </p>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
