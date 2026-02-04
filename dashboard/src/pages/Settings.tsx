import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api, { endpoints } from '../config/api'
import { useAuth } from '../hooks/useAuth'
import { ApiResponse } from '../types'

interface UserSettings {
  notifications: {
    email: boolean
    telegram: boolean
    push: boolean
  }
  alertDefaults: {
    autoDisableOnTrigger: boolean
    repeatInterval: number | null
  }
  display: {
    currency: string
    timezone: string
    theme: 'dark' | 'light' | 'system'
  }
}

export default function Settings() {
  const { user, logout } = useAuth()
  const queryClient = useQueryClient()
  const [saved, setSaved] = useState(false)

  const { data: settings, isLoading } = useQuery({
    queryKey: ['settings'],
    queryFn: async () => {
      const response = await api.get(endpoints.user.settings)
      const data = response.data
      
      // Map Backend UserProfileResponse to Frontend UserSettings
      return {
        notifications: {
          email: data.notification_preferences?.email || false,
          telegram: data.notification_preferences?.telegram || true,
          push: data.notification_preferences?.push || true,
        },
        alertDefaults: {
          autoDisableOnTrigger: true,
          repeatInterval: null,
        },
        display: {
          currency: 'USD',
          timezone: data.timezone || 'UTC',
          theme: data.theme || 'dark',
        },
      } as UserSettings
    },
  })

  const [formData, setFormData] = useState<UserSettings | null>(null)

  const currentSettings = formData ?? settings ?? {
    notifications: { email: true, telegram: true, push: false },
    alertDefaults: { autoDisableOnTrigger: true, repeatInterval: null },
    display: { currency: 'USD', timezone: 'UTC', theme: 'dark' },
  }

  const updateMutation = useMutation({
    mutationFn: async (data: UserSettings) => {
      // Map Frontend UserSettings back to Backend UserProfileUpdate
      const backendData = {
        timezone: data.display.timezone,
        theme: data.display.theme,
        notification_preferences: {
          email: data.notifications.email,
          telegram: data.notifications.telegram,
          push: data.notifications.push,
          price_alerts: true, // defaults
          whale_alerts: true,
          portfolio_updates: true,
        }
      }
      const response = await api.put(endpoints.user.updateSettings, backendData)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['settings'] })
      setSaved(true)
      setTimeout(() => setSaved(false), 3000)
    },
  })

  const handleSave = () => {
    updateMutation.mutate(currentSettings)
  }

  const updateSetting = <T extends keyof UserSettings>(
    category: T,
    key: keyof UserSettings[T],
    value: UserSettings[T][keyof UserSettings[T]]
  ) => {
    const newSettings = {
      ...currentSettings,
      [category]: {
        ...currentSettings[category],
        [key]: value,
      },
    }
    setFormData(newSettings)
  }

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="animate-pulse">
          <div className="h-8 bg-crypto-bg-tertiary rounded w-48 mb-2" />
          <div className="h-4 bg-crypto-bg-tertiary rounded w-64" />
        </div>
        {[1, 2, 3].map((i) => (
          <div key={i} className="card animate-pulse">
            <div className="h-32 bg-crypto-bg-tertiary rounded" />
          </div>
        ))}
      </div>
    )
  }

  return (
    <div className="space-y-6 max-w-3xl">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Settings</h1>
          <p className="text-crypto-text-secondary">
            Manage your account preferences
          </p>
        </div>
        {saved && (
          <span className="badge-gain">Settings saved!</span>
        )}
      </div>

      <div className="card">
        <h3 className="text-lg font-semibold mb-4">Profile</h3>
        <div className="flex items-center gap-4 mb-6">
          <div className="w-16 h-16 rounded-full bg-gradient-to-br from-crypto-accent to-crypto-gain flex items-center justify-center">
            {user?.photo_url ? (
              <img src={user.photo_url} alt={user.username} className="w-16 h-16 rounded-full" />
            ) : (
              <span className="text-2xl font-bold text-crypto-bg">
                {user?.first_name?.[0] || user?.username?.[0] || 'U'}
              </span>
            )}
          </div>
          <div>
            <p className="text-lg font-semibold">{user?.first_name} {user?.last_name}</p>
            <p className="text-crypto-text-secondary">@{user?.username}</p>
            <span className={user?.is_premium ? 'badge-gain' : 'badge-neutral'}>
              {user?.is_premium ? 'Premium' : 'Free Plan'}
            </span>
          </div>
        </div>
        <p className="text-sm text-crypto-text-muted">
          Connected via Telegram • ID: {user?.telegram_id}
        </p>
      </div>

      <div className="card">
        <h3 className="text-lg font-semibold mb-4">Notifications</h3>
        <div className="space-y-4">
          <label className="flex items-center justify-between">
            <div>
              <p className="font-medium">Telegram Notifications</p>
              <p className="text-sm text-crypto-text-secondary">Receive alerts via Telegram bot</p>
            </div>
            <input
              type="checkbox"
              checked={currentSettings.notifications.telegram}
              onChange={(e) => updateSetting('notifications', 'telegram', e.target.checked)}
              className="w-5 h-5 rounded text-crypto-accent focus:ring-crypto-accent"
            />
          </label>

          <label className="flex items-center justify-between">
            <div>
              <p className="font-medium">Email Notifications</p>
              <p className="text-sm text-crypto-text-secondary">Receive alerts via email</p>
            </div>
            <input
              type="checkbox"
              checked={currentSettings.notifications.email}
              onChange={(e) => updateSetting('notifications', 'email', e.target.checked)}
              className="w-5 h-5 rounded text-crypto-accent focus:ring-crypto-accent"
            />
          </label>

          <label className="flex items-center justify-between">
            <div>
              <p className="font-medium">Push Notifications</p>
              <p className="text-sm text-crypto-text-secondary">Browser push notifications</p>
            </div>
            <input
              type="checkbox"
              checked={currentSettings.notifications.push}
              onChange={(e) => updateSetting('notifications', 'push', e.target.checked)}
              className="w-5 h-5 rounded text-crypto-accent focus:ring-crypto-accent"
            />
          </label>
        </div>
      </div>

      <div className="card">
        <h3 className="text-lg font-semibold mb-4">Alert Defaults</h3>
        <div className="space-y-4">
          <label className="flex items-center justify-between">
            <div>
              <p className="font-medium">Auto-disable on Trigger</p>
              <p className="text-sm text-crypto-text-secondary">Automatically disable alerts after they trigger</p>
            </div>
            <input
              type="checkbox"
              checked={currentSettings.alertDefaults.autoDisableOnTrigger}
              onChange={(e) => updateSetting('alertDefaults', 'autoDisableOnTrigger', e.target.checked)}
              className="w-5 h-5 rounded text-crypto-accent focus:ring-crypto-accent"
            />
          </label>
        </div>
      </div>

      <div className="card">
        <h3 className="text-lg font-semibold mb-4">Display</h3>
        <div className="space-y-4">
          <div>
            <label className="label">Currency</label>
            <select
              value={currentSettings.display.currency}
              onChange={(e) => updateSetting('display', 'currency', e.target.value)}
              className="input"
            >
              <option value="USD">USD ($)</option>
              <option value="EUR">EUR (€)</option>
              <option value="GBP">GBP (£)</option>
              <option value="BTC">BTC (₿)</option>
            </select>
          </div>

          <div>
            <label className="label">Timezone</label>
            <select
              value={currentSettings.display.timezone}
              onChange={(e) => updateSetting('display', 'timezone', e.target.value)}
              className="input"
            >
              <option value="UTC">UTC</option>
              <option value="America/New_York">Eastern Time</option>
              <option value="America/Los_Angeles">Pacific Time</option>
              <option value="Europe/London">London</option>
              <option value="Europe/Berlin">Berlin</option>
              <option value="Asia/Tokyo">Tokyo</option>
            </select>
          </div>
        </div>
      </div>

      <div className="flex items-center justify-between">
        <button
          onClick={logout}
          className="btn-danger"
        >
          Logout
        </button>
        <button
          onClick={handleSave}
          disabled={updateMutation.isPending}
          className="btn-primary"
        >
          {updateMutation.isPending ? 'Saving...' : 'Save Settings'}
        </button>
      </div>
    </div>
  )
}
