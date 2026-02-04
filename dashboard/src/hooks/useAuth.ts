import { useCallback } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import wsService from '../config/websocket'
import { toast } from '../store/toastStore'
import { authService } from '../services/auth.service'

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
  const { setAuth, logout: storeLogout, isAuthenticated } = useAuthStore()

  const { data: user, isLoading: isLoadingUser } = useQuery({
    queryKey: ['user'],
    queryFn: () => authService.getCurrentUser(),
    enabled: isAuthenticated,
    staleTime: 1000 * 60 * 5,
  })

  const loginMutation = useMutation({
    mutationFn: (authData: TelegramAuthData) => authService.loginWithTelegram(authData),
    onSuccess: async (data) => {
      console.log('Login mutation success, received data:', { ...data, access_token: '***' })
      // After login, we have the token, now fetch the user profile
      try {
        // IMPORTANT: We MUST set the token first so subsequent requests (like getCurrentUser)
        // will include the Authorization header via the axios interceptor
        useAuthStore.getState().setToken(data.access_token)
        
        console.log('Fetching user profile...')
        const userProfile = await authService.getCurrentUser()
        console.log('User profile fetched:', userProfile)
        
        setAuth(userProfile, data.access_token)
        wsService.connect()
        queryClient.setQueryData(['user'], userProfile)
        toast.success(`Welcome back, ${userProfile.first_name}!`)
        navigate('/')
      } catch (error) {
        console.error('Error fetching user after login:', error)
        toast.error('Failed to fetch user profile')
        // If we fail to get the profile, we should probably logout to be safe
        storeLogout()
      }
    },
    onError: (error) => {
      console.error('Login error:', error)
      toast.error('Login failed. Please try again.')
    }
  })

  const logoutMutation = useMutation({
    mutationFn: () => authService.logout(),
    onSuccess: () => {
      toast.info('Logged out successfully')
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
