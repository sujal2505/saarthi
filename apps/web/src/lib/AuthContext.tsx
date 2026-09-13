import React, { createContext, useContext, useState, useCallback } from 'react'
import type { Customer, Language } from '@/types'
import { MOCK_DASHBOARD } from '@/data/mockData'
import { demoLogin, getDashboard, updateCustomer } from '@/lib/api'

interface AuthState {
  isAuthenticated: boolean
  customer: Customer | null
  language: Language
  customerId: string
  profilePhoto: string
}

interface AuthContextType extends AuthState {
  login: (phone: string, language: Language) => Promise<void>
  logout: () => void
  setLanguage: (lang: Language) => void
  switchCustomer: (customerId: string) => Promise<void>
  updateProfile: (profile: Omit<Customer, 'id'>) => Promise<void>
  setProfilePhoto: (photo: string) => void
}

const AuthContext = createContext<AuthContextType | null>(null)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [state, setState] = useState<AuthState>({
    isAuthenticated: false,
    customer: null,
    language: 'en',
    customerId: 'cust_001',
    profilePhoto: '',
  })

  const login = useCallback(async (phone: string, language: Language) => {
    try {
      const res = await demoLogin(phone, language)
      const targetId = res.customer_id || 'cust_001'
      const dash = await getDashboard(targetId)
      setState({
        isAuthenticated: true,
        customer: dash.customer || MOCK_DASHBOARD.customer,
        language,
        customerId: targetId,
        profilePhoto: localStorage.getItem(`saarthi-profile-photo-${targetId}`) || '',
      })
    } catch {
      // Fallback
      setState({
        isAuthenticated: true,
        customer: MOCK_DASHBOARD.customer,
        language,
        customerId: 'cust_001',
        profilePhoto: localStorage.getItem('saarthi-profile-photo-cust_001') || '',
      })
    }
  }, [])

  const switchCustomer = useCallback(async (targetId: string) => {
    try {
      const dash = await getDashboard(targetId)
      setState(prev => ({
        ...prev,
        customer: dash.customer,
        customerId: targetId,
        profilePhoto: localStorage.getItem(`saarthi-profile-photo-${targetId}`) || '',
      }))
    } catch {
      setState(prev => ({
        ...prev,
        customerId: targetId,
        profilePhoto: localStorage.getItem(`saarthi-profile-photo-${targetId}`) || '',
      }))
    }
  }, [])

  const logout = useCallback(() => {
    setState({ isAuthenticated: false, customer: null, language: 'en', customerId: 'cust_001', profilePhoto: '' })
  }, [])

  const setLanguage = useCallback((lang: Language) => {
    setState(prev => ({ ...prev, language: lang }))
  }, [])

  const updateProfile = useCallback(async (profile: Omit<Customer, 'id'>) => {
    const updated = await updateCustomer(state.customerId, profile)
    setState(prev => ({
      ...prev,
      customer: updated,
      language: updated.preferred_language,
    }))
  }, [state.customerId])

  const setProfilePhoto = useCallback((photo: string) => {
    localStorage.setItem(`saarthi-profile-photo-${state.customerId}`, photo)
    setState(prev => ({ ...prev, profilePhoto: photo }))
  }, [state.customerId])

  return (
    <AuthContext.Provider value={{ ...state, login, logout, setLanguage, switchCustomer, updateProfile, setProfilePhoto }}>
      {children}
    </AuthContext.Provider>
  )
}

// oxlint-disable-next-line react/only-export-components
export function useAuth(): AuthContextType {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
