<template>
  <div class="space-y-5 animate-fade-in">
    <!-- Header -->
    <div class="page-header">
      <div>
        <h1 class="font-display font-bold text-ink text-[22px]">Buyurtmalar</h1>
        <p class="text-ink-3 text-[13px] mt-0.5">
          Jami <span class="font-semibold text-ink tabular-nums">{{ ordersStore.orders.length }}</span> ta buyurtma
        </p>
      </div>
      <RouterLink to="/orders/new" class="btn-primary">
        <AppIcon name="add" :size="18" />
        Yangi buyurtma
      </RouterLink>
    </div>

    <!-- Filters -->
    <div class="card p-4">
      <div class="flex flex-wrap gap-3 items-end">
        <!-- Search -->
        <div class="flex-1 min-w-[180px]">
          <label class="label">Qidirish</label>
          <div class="relative">
            <AppIcon name="search" :size="17" class="absolute left-3 top-1/2 -translate-y-1/2 text-ink-4 pointer-events-none" />
            <input v-model="filters.search" @input="debouncedFetch"
              class="input pl-9" placeholder="Raqam yoki mijoz nomi..." />
          </div>
        </div>

        <!-- Status -->
        <div class="min-w-[170px]">
          <label class="label">Holat</label>
          <div class="relative">
            <select v-model="filters.status" @change="fetchData" class="input pr-8">
              <option value="">Barcha holatlar</option>
              <option v-for="s in STATUSES" :key="s.value" :value="s.value">{{ s.label }}</option>
            </select>
            <AppIcon name="expand_more" :size="17" class="absolute right-2.5 top-1/2 -translate-y-1/2 text-ink-4 pointer-events-none" />
          </div>
        </div>

        <!-- Date from -->
        <div class="min-w-[150px]">
          <label class="label">Dan</label>
          <div class="relative">
            <AppIcon name="calendar_month" :size="15" class="absolute left-3 top-1/2 -translate-y-1/2 text-ink-4 pointer-events-none" />
            <input v-model="filters.from_date" @change="fetchData" type="date" class="input pl-9" />
          </div>
        </div>

        <!-- Date to -->
        <div class="min-w-[150px]">
          <label class="label">Gacha</label>
          <div class="relative">
            <AppIcon name="calendar_month" :size="15" class="absolute left-3 top-1/2 -translate-y-1/2 text-ink-4 pointer-events-none" />
            <input v-model="filters.to_date" @change="fetchData" type="date" class="input pl-9" />
          </div>
        </div>

        <!-- Clear -->
        <button v-if="hasFilters" @click="clearFilters"
          class="btn-ghost text-red-500 hover:bg-red-50 hover:text-red-600 self-end border border-red-100">
          <AppIcon name="close" :size="16" />
          Tozalash
        </button>
      </div>
    </div>

    <!-- Table card -->
    <div class="card overflow-hidden">
      <!-- Loading -->
      <div v-if="ordersStore.loading" class="p-10 flex flex-col items-center gap-3">
        <div class="w-10 h-10 rounded-full border-[3px] border-brand-100 border-t-brand-500 animate-spin" />
        <p class="text-ink-4 text-[13px]">Yuklanmoqda...</p>
      </div>

      <!-- Empty -->
      <div v-else-if="ordersStore.orders.length === 0"
        class="py-16 flex flex-col items-center justify-center gap-4">
        <div class="icon-box w-16 h-16 icon-box-slate rounded-2xl">
          <AppIcon name="shopping_cart_off" :size="32" />
        </div>
        <div class="text-center">
          <p class="font-display font-semibold text-ink text-[15px]">Buyurtmalar topilmadi</p>
          <p class="text-ink-3 text-[13px] mt-1">Filtrlarga mos buyurtma mavjud emas</p>
        </div>
        <div class="flex gap-2 flex-wrap justify-center">
          <button v-if="hasFilters" @click="clearFilters" class="btn-secondary">
            <AppIcon name="filter_alt_off" :size="16" />
            Filtrlarni tozalash
          </button>
          <RouterLink to="/orders/new" class="btn-primary">
            <AppIcon name="add" :size="16" />
            Yangi buyurtma
          </RouterLink>
        </div>
      </div>

      <!-- Table -->
      <div v-else class="overflow-x-auto">
        <table class="tbl" style="min-width:680px;">
          <thead>
            <tr>
              <th class="tbl-th">ID</th>
              <th class="tbl-th">Mijoz</th>
              <th class="tbl-th">Holat</th>
              <th class="tbl-th">Muddat</th>
              <th class="tbl-th">Yaratilgan</th>
              <th class="tbl-th"></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="o in ordersStore.orders" :key="o.id" class="tbl-row group">
              <td class="tbl-td">
                <span class="font-mono font-bold text-brand-500 text-[13px]">{{ o.order_no }}</span>
              </td>
              <td class="tbl-td">
                <div class="flex items-center gap-2.5">
                  <div class="w-8 h-8 rounded-full bg-brand-100 text-brand-600 flex items-center justify-center font-bold text-[11px] flex-shrink-0">
                    {{ (o.client?.name || '?').charAt(0).toUpperCase() }}
                  </div>
                  <div>
                    <p class="font-semibold text-ink text-[13px]">{{ o.client?.name || '—' }}</p>
                    <p v-if="o.client?.phone" class="text-ink-4 text-[11px] font-mono">{{ o.client.phone }}</p>
                  </div>
                </div>
              </td>
              <td class="tbl-td"><StatusBadge :status="o.status" /></td>
              <td class="tbl-td">
                <div v-if="o.deadline" class="flex items-center gap-1.5">
                  <span class="w-1.5 h-1.5 rounded-full flex-shrink-0"
                    :class="isDelayed(o.deadline, o.status) ? 'bg-red-400' : 'bg-slate-300'" />
                  <span class="text-[13px] font-medium tabular-nums"
                    :class="isDelayed(o.deadline, o.status) ? 'text-red-500' : 'text-ink-3'">
                    {{ o.deadline }}
                  </span>
                </div>
                <span v-else class="text-ink-5 text-[13px]">—</span>
              </td>
              <td class="tbl-td font-mono text-ink-4 text-[12px] tabular-nums">{{ formatDate(o.created_at) }}</td>
              <td class="tbl-td">
                <div class="flex items-center justify-end gap-1">
                  <RouterLink :to="`/orders/${o.id}`" class="btn-icon" title="Ko'rish">
                    <AppIcon name="open_in_new" :size="17" />
                  </RouterLink>
                  <button v-if="['new','cancelled'].includes(o.status)"
                    @click.prevent="confirmDelete(o)"
                    class="btn-icon border-red-100 text-red-400 hover:bg-red-50 hover:text-red-600 hover:border-red-200"
                    title="O'chirish">
                    <AppIcon name="delete" :size="17" />
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

    <!-- Delete confirm modal -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="deleteTarget"
          class="fixed inset-0 z-50 flex items-center justify-center p-4 sidebar-backdrop"
          @click.self="deleteTarget = null">
          <div class="card p-6 w-full max-w-sm">
            <div class="flex items-center gap-3 mb-4">
              <div class="icon-box w-10 h-10 icon-box-red">
                <AppIcon name="delete" :size="20" />
              </div>
              <h3 class="font-display font-bold text-ink text-[16px]">Buyurtmani o'chirish</h3>
            </div>
            <p class="text-ink-3 text-[13px] mb-5">
              <strong class="text-ink">{{ deleteTarget?.order_no }}</strong> buyurtmasini o'chirishni tasdiqlaysizmi? Bu amalni qaytarib bo'lmaydi.
            </p>
            <div class="flex gap-2.5 justify-end">
              <button class="btn-secondary" @click="deleteTarget = null">Bekor</button>
              <button class="btn-danger" @click="doDelete" :disabled="deleting">
                <AppIcon v-if="deleting" name="progress_activity" :size="16" class="animate-spin" />
                O'chirish
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

      <!-- Table footer -->
      <div v-if="ordersStore.orders.length > 0"
        class="px-5 py-3 border-t border-[#E8ECF4] flex items-center justify-between bg-[#FAFBFC]">
        <span class="text-ink-4 text-[12px]">
          Jami <span class="font-semibold text-ink-2 tabular-nums">{{ ordersStore.orders.length }}</span> ta natija
        </span>
        <div class="flex items-center gap-1.5">
          <button disabled class="btn-icon opacity-40 cursor-not-allowed">
            <AppIcon name="chevron_left" :size="17" />
          </button>
          <span class="text-[12px] text-ink-3 px-2 tabular-nums">1</span>
          <button class="btn-icon cursor-pointer">
            <AppIcon name="chevron_right" :size="17" />
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { useOrdersStore } from '@/stores/orders'
import StatusBadge from '@/components/StatusBadge.vue'
import AppIcon from '@/components/AppIcon.vue'

const ordersStore  = useOrdersStore()
const deleteTarget = ref(null)
const deleting     = ref(false)

function confirmDelete(order) { deleteTarget.value = order }
async function doDelete() {
  deleting.value = true
  try {
    await ordersStore.deleteOrder(deleteTarget.value.id)
    deleteTarget.value = null
  } catch (e) { alert(e.response?.data?.detail || 'Xatolik') }
  finally { deleting.value = false }
}
const filters     = reactive({ search: '', status: '', from_date: '', to_date: '' })
const hasFilters  = computed(() => Object.values(filters).some(v => v))

const STATUSES = [
  { value: 'new',           label: 'Yangi' },
  { value: 'cutting',       label: 'Kesishda' },
  { value: 'drilling',      label: 'Teshishda' },
  { value: 'assembling',    label: "Yig'ishda" },
  { value: 'quality_check', label: 'Sifat nazorati' },
  { value: 'ready',         label: 'Tayyor' },
  { value: 'delivered',     label: 'Yetkazildi' },
  { value: 'cancelled',     label: 'Bekor' },
]

let debounceTimer = null
function debouncedFetch() {
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(fetchData, 400)
}

function fetchData() {
  const p = {}
  if (filters.search)    p.search    = filters.search
  if (filters.status)    p.status    = filters.status
  if (filters.from_date) p.from_date = filters.from_date
  if (filters.to_date)   p.to_date   = filters.to_date
  ordersStore.fetchOrders(p)
}

function clearFilters() {
  Object.keys(filters).forEach(k => (filters[k] = ''))
  fetchData()
}

function formatDate(dt) {
  if (!dt) return '—'
  return new Date(dt).toLocaleDateString('uz-UZ')
}

function isDelayed(deadline, status) {
  if (!deadline || ['delivered', 'cancelled'].includes(status)) return false
  return new Date(deadline) < new Date()
}

onMounted(fetchData)
</script>
