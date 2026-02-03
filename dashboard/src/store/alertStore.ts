import { create } from 'zustand'
import { Alert } from '../types'

interface AlertState {
  triggeredAlerts: Alert[]
  unreadCount: number
  addTriggeredAlert: (alert: Alert) => void
  markAsRead: (alertId: string) => void
  markAllAsRead: () => void
  clearTriggeredAlerts: () => void
}

export const useAlertStore = create<AlertState>((set) => ({
  triggeredAlerts: [],
  unreadCount: 0,

  addTriggeredAlert: (alert: Alert) =>
    set((state) => ({
      triggeredAlerts: [alert, ...state.triggeredAlerts].slice(0, 50),
      unreadCount: state.unreadCount + 1,
    })),

  markAsRead: (alertId: string) =>
    set((state) => ({
      triggeredAlerts: state.triggeredAlerts.map((a) =>
        a.id === alertId ? { ...a, isRead: true } : a
      ),
      unreadCount: Math.max(0, state.unreadCount - 1),
    })),

  markAllAsRead: () =>
    set((state) => ({
      triggeredAlerts: state.triggeredAlerts.map((a) => ({ ...a, isRead: true })),
      unreadCount: 0,
    })),

  clearTriggeredAlerts: () =>
    set({
      triggeredAlerts: [],
      unreadCount: 0,
    }),
}))

export default useAlertStore
