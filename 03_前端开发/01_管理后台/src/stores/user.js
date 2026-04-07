import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 10000
})

api.interceptors.request.use(config => {
  const userStore = useUserStore()
  if (userStore.token) {
    config.headers.Authorization = `Bearer ${userStore.token}`
  }
  return config
})

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '')
  const userInfo = ref(JSON.parse(localStorage.getItem('userInfo') || '{}'))
  const roles = ref([])

  const isLoggedIn = computed(() => !!token.value)

  async function login(username, password) {
    try {
      const res = await api.post('/users/login', { username, password })
      token.value = res.data.token
      userInfo.value = res.data.user
      localStorage.setItem('token', res.data.token)
      localStorage.setItem('userInfo', JSON.stringify(res.data.user))
      roles.value = res.data.user.roles || []
      return res.data
    } catch (error) {
      throw error
    }
  }

  async function logout() {
    try {
      await api.post('/users/logout')
    } finally {
      token.value = ''
      userInfo.value = {}
      roles.value = []
      localStorage.removeItem('token')
      localStorage.removeItem('userInfo')
    }
  }

  async function refreshToken() {
    try {
      const res = await api.post('/users/refresh', { refresh_token: localStorage.getItem('refresh_token') })
      token.value = res.data.access_token
      localStorage.setItem('token', res.data.access_token)
      return res.data
    } catch {
      logout()
    }
  }

  return { token, userInfo, roles, isLoggedIn, login, logout, refreshToken }
})

export { api }