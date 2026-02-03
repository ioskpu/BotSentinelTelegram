import { useCallback } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import api, { endpoints } from '../config/api'
import { useAuthStore } from '../store/authStore'
import { User, ApiResponse } from '../types'
import wsService from '../config/websocket'

interface TelegramAuthData {
  id: number
  first_name: string
  last_name?: string
  username?: string
  photo_url?: string
  auth_date: number
  hash: string
}

export function useAuth() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const { token, setAuth, logout: storeLogout, isAuthenticated } = useAuthStore()

  const { data: user, isLoading: isLoadingUser } = useQuery({
    queryKey: ['user'],
    queryFn: async () => {
      const response = await api.get<ApiResponse<User>>(endpoints.auth.me)
      return response.data.data
    },
    enabled: isAuthenticated,
    staleTime: 1000 * 60 * 5,
  })

  const loginMutation = useMutation({
    mutationFn: async (authData: TelegramAuthData) => {
      const response = await api.post<ApiResponse<{ user: User; token: string }>>(
        endpoints.auth.login,
        authData
      )
      return response.data.data
    },
    onSuccess: (data) => {
      setAuth(data.user, data.token)
      wsService.connect()
      queryClient.setQueryData(['user'], data.user)
      navigate('/')
    },
  })

  const logoutMutation = useMutation({
    mutationFn: async () => {
      if (token) {
        await api.post(endpoints.auth.logout)
      }
    },
    onSettled: () => {
      wsService.disconnect()
      storeLogout()
      queryClient.clear()
      navigate('/login')
    },
  })

  const login = useCallback(
    (authData: TelegramAuthData) => {
      loginMutation.mutate(authData)
    },
    [loginMutation]
  )

  const logout = useCallback(() => {
    logoutMutation.mutate()
  }, [logoutMutation])

  return {
    user,
    isAuthenticated,
    isLoading: isLoadingUser || loginMutation.isPending,
    isLoggingIn: loginMutation.isPending,
    isLoggingOut: logoutMutation.isPending,
    loginError: loginMutation.error,
    login,
    logout,
  }
}

export default useAuth
