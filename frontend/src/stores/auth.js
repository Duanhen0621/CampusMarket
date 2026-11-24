import { defineStore } from 'pinia'

import http from '@/api/http'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || '',
    user: JSON.parse(localStorage.getItem('user') || 'null'),
  }),

  getters: {
    isLoggedIn: (state) => Boolean(state.token),
    isAdmin: (state) => (state.user?.role ?? 0) >= 1,
    isSuperAdmin: (state) => state.user?.role === 2,
  },

  actions: {
    async login(payload) {
      const { data } = await http.post('/auth/login', payload)
      this.token = data.data.access_token
      this.user = data.data.user
      localStorage.setItem('token', this.token)
      localStorage.setItem('user', JSON.stringify(this.user))
    },

    async updateProfile(payload) {
      const { data } = await http.put('/auth/me', payload)
      this.user = data.data
      localStorage.setItem('user', JSON.stringify(this.user))
    },

    async fetchMe() {
      if (!this.token) return
      const { data } = await http.get('/auth/me')
      this.user = data.data
      localStorage.setItem('user', JSON.stringify(this.user))
    },

    logout() {
      this.token = ''
      this.user = null
      localStorage.removeItem('token')
      localStorage.removeItem('user')
    },
  },
})
