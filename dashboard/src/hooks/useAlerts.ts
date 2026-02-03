import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useEffect } from 'react'
import { useAlertStore } from '../store/alertStore'
import wsService from '../config/websocket'
import { Alert, CreateAlertRequest } from '../types'
import { toast } from '../store/toastStore'
import { alertsService } from '../services/alerts.service'

interface UseAlertsOptions {
  page?: number
  pageSize?: number
  isActive?: boolean
  symbol?: string
}

export function useAlerts(options: UseAlertsOptions = {}) {
  const { page = 1, pageSize = 20, isActive, symbol } = options
  const queryClient = useQueryClient()
  const { addTriggeredAlert } = useAlertStore()

  const {
    data: alertsData,
    isLoading,
    error,
    refetch,
  } = useQuery({
    queryKey: ['alerts', { page, pageSize, isActive, symbol }],
    queryFn: () => alertsService.getAlerts({ 
      page, 
      limit: pageSize, 
      isActive, 
      symbol 
    }),
    refetchInterval: 300000, // Background sync cada 5 minutos
  })

  const createMutation = useMutation({
    mutationFn: (data: CreateAlertRequest) => alertsService.createAlert(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alerts'] })
      toast.success('Alert created successfully')
    },
    onError: () => {
      toast.error('Failed to create alert')
    },
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<CreateAlertRequest> }) => 
      alertsService.updateAlert(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alerts'] })
      toast.success('Alert updated successfully')
    },
    onError: () => {
      toast.error('Failed to update alert')
    },
  })

  const deleteMutation = useMutation({
    mutationFn: (id: string) => alertsService.deleteAlert(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alerts'] })
      toast.success('Alert deleted successfully')
    },
    onError: () => {
      toast.error('Failed to delete alert')
    },
  })

  const toggleMutation = useMutation({
    mutationFn: (id: string) => alertsService.toggleAlert(id),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['alerts'] })
      toast.success(`Alert ${data.is_active ? 'enabled' : 'disabled'} successfully`)
    },
    onError: () => {
      toast.error('Failed to toggle alert')
    },
  })

  useEffect(() => {
    const unsubscribe = wsService.subscribe('alert_triggered', (message) => {
      const alert = message.data as Alert
      addTriggeredAlert(alert)
      toast.info(`Alert triggered: ${alert.coin_symbol} ${alert.alert_type}`, 5000)
      queryClient.invalidateQueries({ queryKey: ['alerts'] })
    })

    return () => {
      unsubscribe()
    }
  }, [queryClient, addTriggeredAlert])

  return {
    alerts: alertsData?.items || [],
    total: alertsData?.total || 0,
    hasMore: alertsData?.hasMore || false,
    isLoading,
    error,
    refetch,
    createAlert: createMutation.mutateAsync,
    updateAlert: updateMutation.mutateAsync,
    deleteAlert: deleteMutation.mutateAsync,
    toggleAlert: toggleMutation.mutateAsync,
    isCreating: createMutation.isPending,
    isUpdating: updateMutation.isPending,
    isDeleting: deleteMutation.isPending,
  }
}

export function useAlert(id: string) {
  return useQuery({
    queryKey: ['alert', id],
    queryFn: () => alertsService.getAlert(id),
    enabled: !!id,
  })
}

export default useAlerts
