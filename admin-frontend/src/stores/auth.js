import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/api'
import router from '@/router'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))
  const loading = ref(false)
  const error = ref(null)

  const isAuthenticated = computed(() => !!localStorage.getItem('access_token'))
  const isAdmin = computed(() => user.value?.role === 'admin')
  const isDirector = computed(() => user.value?.role === 'director')

  async function login(loginData) {
    loading.value = true
    error.value = null
    try {
      const res = await authApi.login(loginData)
      localStorage.setItem('access_token', res.data.access_token)
      localStorage.setItem('refresh_token', res.data.refresh_token)
      user.value = res.data.user
      localStorage.setItem('user', JSON.stringify(res.data.user))
      router.push('/')
    } catch (e) {
      error.value = e.response?.data?.detail || 'Login yoki parol noto\'g\'ri'
    } finally {
      loading.value = false
    }
  }

  async function fetchMe() {
    try {
      const res = await authApi.me()
      user.value = res.data
      localStorage.setItem('user', JSON.stringify(res.data))
    } catch {
      logout()
    }
  }

  function logout() {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user')
    user.value = null
    router.push('/login')
  }

  return { user, loading, error, isAuthenticated, isAdmin, isDirector, login, fetchMe, logout }
})
