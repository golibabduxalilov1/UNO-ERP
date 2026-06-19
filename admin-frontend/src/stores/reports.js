import { defineStore } from 'pinia'
import { ref } from 'vue'
import { reportsApi } from '@/api'

export const useReportsStore = defineStore('reports', () => {
  const dashboard = ref(null)
  const monthly = ref([])
  const delayed = ref([])
  const loading = ref(false)

  async function fetchDashboard() {
    loading.value = true
    try {
      const res = await reportsApi.dashboard()
      dashboard.value = res.data
    } finally {
      loading.value = false
    }
  }

  async function fetchMonthly(params) {
    loading.value = true
    try {
      const res = await reportsApi.monthly(params)
      monthly.value = res.data
    } finally {
      loading.value = false
    }
  }

  async function fetchDelayed() {
    loading.value = true
    try {
      const res = await reportsApi.delayed()
      delayed.value = res.data
    } finally {
      loading.value = false
    }
  }

  return { dashboard, monthly, delayed, loading, fetchDashboard, fetchMonthly, fetchDelayed }
})
