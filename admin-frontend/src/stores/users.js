import { defineStore } from 'pinia'
import { ref } from 'vue'
import { usersApi } from '@/api'

export const useUsersStore = defineStore('users', () => {
  const users = ref([])
  const loading = ref(false)
  const error = ref(null)

  async function fetchUsers(params = {}) {
    loading.value = true
    error.value = null
    try {
      const res = await usersApi.list(params)
      users.value = res.data
    } catch (e) {
      error.value = e.response?.data?.detail || 'Xatolik'
    } finally {
      loading.value = false
    }
  }

  async function createUser(data) {
    const res = await usersApi.create(data)
    users.value.unshift(res.data)
    return res.data
  }

  async function updateUser(id, data) {
    const res = await usersApi.update(id, data)
    const idx = users.value.findIndex(u => u.id === id)
    if (idx !== -1) users.value[idx] = res.data
    return res.data
  }

  async function deleteUser(id) {
    await usersApi.delete(id)
    users.value = users.value.filter(u => u.id !== id)
  }

  return { users, loading, error, fetchUsers, createUser, updateUser, deleteUser }
})
