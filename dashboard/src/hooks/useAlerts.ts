import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useEffect } from 'react'
import api, { endpoints } from '../config/api'
import { useAlertStore } from '../store/alertStore'
import wsService from '../config/websocket'
import { Alert, CreateAlertRequest, ApiResponse, PaginatedResponse } from '../types'

interface UseAlertsOptions {
  page?: number
  pageSize?: number
  isActive?: boolean
}

export function useAlerts(options: UseAlertsOptions = {}) {
  const { page = 1, pageSize = 20, isActive } = options
  const queryClient = useQueryClient()
  const { addTriggeredAlert } = useAlertStore()

  const {
    data: alertsData,
    isLoading,
    error,
    refetch,
  } = useQuery({
    queryKey: ['alerts', { page, pageSize, isActive }],
    queryFn: async () => {
      const params = new URLSearchParams()
      params.append('page', page.toString())
      params.append('pageSize', pageSize.toString())
      if (isActive !== undefined) {
        params.append('isActive', isActive.toString())
      }
      const response = await api.get<ApiResponse<PaginatedResponse<Alert>>>(
        `${endpoints.alerts.list}?${params.toString()}`
      )
      return response.data.data
    },
  })

  const createMutation = useMutation({
    mutationFn: async (data: CreateAlertRequest) => {
      const response = await api.post<ApiResponse<Alert>>(endpoints.alerts.create, data)
      return response.data.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alerts'] })
    },
  })

  const updateMutation = useMutation({
    mutationFn: async ({ id, data }: { id: string; data: Partial<CreateAlertRequest> }) => {
      const response = await api.put<ApiResponse<Alert>>(endpoints.alerts.update(id), data)
      return response.data.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alerts'] })
    },
  })

  const deleteMutation = useMutation({
    mutationFn: async (id: string) => {
      await api.delete(endpoints.alerts.delete(id))
      return id
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alerts'] })
    },
  })

  const toggleMutation = useMutation({
    mutationFn: async (id: string) => {
      const response = await api.post<ApiResponse<Alert>>(endpoints.alerts.toggle(id))
      return response.data.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alerts'] })
    },
  })

  useEffect(() => {
    const unsubscribe = wsService.subscribe('alert_triggered', (message) => {
      const alert = message.data as Alert
      addTriggeredAlert(alert)
      queryClient.invalidateQueries({ queryKey: ['alerts'] })
    })

    return () => {
      unsubscribe()
    }
  }, [queryClient, addTriggeredAlert])

  return {
    alerts: alertsData?.items ?? [],
    total: alertsData?.total ?? 0,
    hasMore: alertsData?.hasMore ?? false,
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
    queryFn: async () => {
      const response = await api.get<ApiResponse<Alert>>(endpoints.alerts.get(id))
      return response.data.data
    },
    enabled: !!id,
  })
}

export default useAlerts
