import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import { extractErrorMessage } from '@/utils/error'

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

api.interceptors.response.use(
  response => response,
  error => {
    const status = error?.response?.status
    const config = error?.config || {}
    const silent = config.silentError === true

    if (!silent) {
      if (status === 401) {
        ElMessage.error('登录已失效，请重新登录')
        localStorage.removeItem('token')
        localStorage.removeItem('refresh_token')
        localStorage.removeItem('userInfo')
        if (window.location.pathname !== '/login') {
          window.location.href = '/login'
        }
      } else if (status === 403) {
        ElMessage.error(extractErrorMessage(error, '当前账号没有访问该功能的权限'))
      } else if (status >= 400) {
        ElMessage.error(extractErrorMessage(error))
      }
    }

    return Promise.reject(error)
  }
)

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '')
  const userInfo = ref(JSON.parse(localStorage.getItem('userInfo') || '{}'))
  const roles = ref([])

  const isLoggedIn = computed(() => !!token.value)

  async function login(username, password) {
    const res = await api.post('/users/login', { username, password }, { silentError: true })
    token.value = res.data.token
    userInfo.value = res.data.user
    localStorage.setItem('token', res.data.token)
    localStorage.setItem('refresh_token', res.data.refresh_token)
    localStorage.setItem('userInfo', JSON.stringify(res.data.user))
    roles.value = res.data.user.roles || []
    return res.data
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
      const res = await api.post('/users/refresh', { refresh_token: localStorage.getItem('refresh_token') }, { silentError: true })
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
