import { defineStore } from 'pinia'
import { ref } from 'vue'
import { ordersApi } from '@/api'

export const useOrdersStore = defineStore('orders', () => {
  const orders = ref([])
  const currentOrder = ref(null)
  const loading = ref(false)
  const error = ref(null)

  async function fetchOrders(params = {}) {
    loading.value = true
    error.value = null
    try {
      const res = await ordersApi.list(params)
      orders.value = res.data
    } catch (e) {
      error.value = e.response?.data?.detail || 'Xatolik yuz berdi'
    } finally {
      loading.value = false
    }
  }

  async function fetchOrder(id) {
    loading.value = true
    error.value = null
    try {
      const res = await ordersApi.get(id)
      currentOrder.value = res.data
      return res.data
    } catch (e) {
      error.value = e.response?.data?.detail || 'Buyurtma topilmadi'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function createOrder(data) {
    loading.value = true
    error.value = null
    try {
      const res = await ordersApi.create(data)
      return res.data
    } catch (e) {
      error.value = e.response?.data?.detail || 'Buyurtma yaratishda xatolik'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function fetchOrderQuiet(id) {
    try {
      const res = await ordersApi.get(id)
      return res.data
    } catch { return null }
  }

  async function updateOrder(id, data) {
    try {
      const res = await ordersApi.update(id, data)
      if (currentOrder.value?.id === id) currentOrder.value = res.data
      return res.data
    } catch (e) { throw e }
  }

  async function deleteOrder(id) {
    try {
      await ordersApi.delete(id)
      orders.value = orders.value.filter(o => o.id !== id)
      if (currentOrder.value?.id === id) currentOrder.value = null
    } catch (e) { throw e }
  }

  return { orders, currentOrder, loading, error, fetchOrders, fetchOrder, fetchOrderQuiet, createOrder, updateOrder, deleteOrder }
})
