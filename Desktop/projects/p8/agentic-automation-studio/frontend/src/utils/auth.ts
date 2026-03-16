import { authApi } from './api'

export interface User {
  email: string
  name: string
}

export interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
}

// Token storage keys
const TOKEN_KEY = 'agentic_auth_token'
const USER_KEY = 'agentic_user'

// Get stored auth data
export const getStoredAuth = (): AuthState => {
  if (typeof window === 'undefined') {
    return { user: null, token: null, isAuthenticated: false }
  }

  const token = localStorage.getItem(TOKEN_KEY)
  const userStr = localStorage.getItem(USER_KEY)
  
  if (token && userStr) {
    try {
      const user = JSON.parse(userStr)
      return { user, token, isAuthenticated: true }
    } catch {
      return { user: null, token: null, isAuthenticated: false }
    }
  }
  
  return { user: null, token: null, isAuthenticated: false }
}

// Store auth data
export const setStoredAuth = (user: User, token: string) => {
  if (typeof window !== 'undefined') {
    localStorage.setItem(TOKEN_KEY, token)
    localStorage.setItem(USER_KEY, JSON.stringify(user))
  }
}

// Clear auth data
export const clearStoredAuth = () => {
  if (typeof window !== 'undefined') {
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(USER_KEY)
  }
}

// Login function
export const login = async (email: string, password: string): Promise<{ user: User; token: string }> => {
  const response = await authApi.login({ email, password })
  setStoredAuth(response.data.user, response.data.access_token)
  return { user: response.data.user, token: response.data.access_token }
}

// Signup function
export const signup = async (email: string, password: string, name: string): Promise<{ user: User; token: string }> => {
  const response = await authApi.signup({ email, password, name })
  setStoredAuth(response.data.user, response.data.access_token)
  return { user: response.data.user, token: response.data.access_token }
}

// Logout function
export const logout = () => {
  clearStoredAuth()
  window.location.href = '/login'
}

// Check if user is authenticated
export const isAuthenticated = (): boolean => {
  return getStoredAuth().isAuthenticated
}
