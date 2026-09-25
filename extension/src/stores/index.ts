// Global state store using Zustand
import { create } from 'zustand'
import { User, Statistics, SchedulerConfig } from '../types'
import api from '../services/api'

interface AuthStore {
  user: User | null
  isLoggedIn: boolean
  isLoading: boolean
  login: (email: string, password: string) => Promise<void>
  logout: () => Promise<void>
  setUser: (user: User) => void
}

export const useAuthStore = create<AuthStore>((set) => ({
  user: null,
  isLoggedIn: false,
  isLoading: false,
  login: async (email: string, password: string) => {
    set({ isLoading: true })
    try {
      await api.login(email, password)
      const response = await api.getMe()
      set({ user: response.data, isLoggedIn: true })
    } finally {
      set({ isLoading: false })
    }
  },
  logout: async () => {
    await api.logout()
    set({ user: null, isLoggedIn: false })
  },
  setUser: (user: User) => set({ user }),
}))

interface UIStore {
  currentPage: string
  notifications: number
  setCurrentPage: (page: string) => void
  setNotifications: (count: number) => void
}

export const useUIStore = create<UIStore>((set) => ({
  currentPage: 'dashboard',
  notifications: 0,
  setCurrentPage: (page: string) => set({ currentPage: page }),
  setNotifications: (count: number) => set({ notifications: count }),
}))

interface DataStore {
  statistics: Statistics | null
  schedulerConfig: SchedulerConfig | null
  setStatistics: (stats: Statistics) => void
  setSchedulerConfig: (config: SchedulerConfig) => void
}

export const useDataStore = create<DataStore>((set) => ({
  statistics: null,
  schedulerConfig: null,
  setStatistics: (statistics: Statistics) => set({ statistics }),
  setSchedulerConfig: (schedulerConfig: SchedulerConfig) => set({ schedulerConfig }),
}))
