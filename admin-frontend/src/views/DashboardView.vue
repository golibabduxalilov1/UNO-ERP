<template>
  <div class="space-y-6 animate-fade-in">
    <!-- Page header -->
    <div class="page-header">
      <div>
        <h1 class="font-display font-bold text-ink text-[22px]">Umumiy ko'rinish</h1>
        <p class="text-ink-3 text-[13px] mt-0.5">{{ todayLabel }} · Barcha muhim ko'rsatkichlar</p>
      </div>
      <RouterLink to="/orders/new" class="btn-primary">
        <AppIcon name="add" :size="18" />
        Yangi buyurtma
      </RouterLink>
    </div>

    <!-- Stat cards -->
    <div class="grid grid-cols-1 lg:grid-cols-4 gap-4">
      <div v-for="card in statCards" :key="card.key"
        class="stat-card"
        :class="card.accent"
      >
        <div class="flex items-center justify-between mb-4">
          <div class="icon-box w-10 h-10" :class="card.iconBox">
            <AppIcon :name="card.icon" :size="20" />
          </div>
          <span class="badge text-[11px]" :class="card.trendClass">
            {{ card.trend }}
          </span>
        </div>
        <div>
          <p class="font-display font-bold text-ink text-[28px] leading-none tabular-nums">
            <span v-if="reportsStore.loading" class="inline-block w-14 h-7 skeleton align-middle" />
            <AnimatedCounter v-else :target="reportsStore.dashboard?.[card.key] ?? 0" />
          </p>
          <p class="text-ink-3 text-[12px] font-medium mt-1.5">{{ card.label }}</p>
        </div>
      </div>
    </div>

    <!-- Mid section: Chart + Delayed -->
    <div class="grid grid-cols-1 lg:grid-cols-5 gap-5">
      <!-- Chart -->
      <div class="card p-5 lg:col-span-3">
        <div class="flex items-center justify-between mb-5">
          <div>
            <h3 class="font-display font-semibold text-ink text-[15px]">Holat taqsimoti</h3>
            <p class="text-ink-4 text-[12px] mt-0.5">Buyurtmalar statuslari bo'yicha</p>
          </div>
          <div class="icon-box w-9 h-9 icon-box-blue">
            <AppIcon name="donut_large" :size="18" />
          </div>
        </div>
        <div v-if="reportsStore.loading" class="h-52 flex items-center justify-center">
          <div class="flex flex-col items-center gap-3">
            <div class="w-10 h-10 rounded-full border-[3px] border-brand-100 border-t-brand-500 animate-spin" />
            <p class="text-ink-4 text-[12px]">Yuklanmoqda...</p>
          </div>
        </div>
        <div v-else-if="chartData" class="relative h-52">
          <Doughnut :data="chartData" :options="chartOptions" />
        </div>
        <div v-else class="h-52 flex flex-col items-center justify-center gap-3">
          <div class="icon-box w-14 h-14 icon-box-slate">
            <AppIcon name="bar_chart" :size="28" />
          </div>
          <p class="text-ink-4 text-[13px]">Ma'lumot mavjud emas</p>
        </div>
      </div>

      <!-- Delayed -->
      <div class="card lg:col-span-2 flex flex-col">
        <div class="flex items-center justify-between p-5 pb-3">
          <div class="flex items-center gap-2">
            <span class="w-2 h-2 rounded-full bg-red-400" />
            <h3 class="font-display font-semibold text-[14px] text-red-600">Kechikkanlar</h3>
          </div>
          <RouterLink to="/reports"
            class="text-[12px] font-semibold text-brand-500 hover:text-brand-600 transition-colors">
            Barchasi →
          </RouterLink>
        </div>

        <div class="flex-1 px-3 pb-4 space-y-2">
          <div v-if="reportsStore.loading" class="space-y-2 p-2">
            <div v-for="n in 3" :key="n" class="h-14 skeleton rounded-lg" />
          </div>
          <div v-else-if="delayed.length === 0"
            class="h-40 flex flex-col items-center justify-center gap-2">
            <div class="icon-box w-12 h-12 icon-box-green">
              <AppIcon name="check_circle" :size="22" />
            </div>
            <p class="text-[13px] font-medium text-ink-3">Kechikkan buyurtma yo'q!</p>
          </div>
          <RouterLink
            v-else
            v-for="o in delayed.slice(0, 4)" :key="o.order_id"
            :to="`/orders/${o.order_id}`"
            class="flex items-center justify-between p-3 rounded-lg hover:bg-red-50 transition-colors cursor-pointer group"
            style="border:1px solid #FEE2E2;"
          >
            <div class="flex items-center gap-2.5">
              <div class="w-1 h-8 rounded-full bg-red-300 flex-shrink-0" />
              <div>
                <p class="font-mono font-bold text-red-500 text-[13px] group-hover:text-red-600">{{ o.order_no }}</p>
                <p class="text-ink-4 text-[11px] mt-0.5">{{ o.client_name }}</p>
              </div>
            </div>
            <div class="text-right">
              <p class="font-bold text-red-400 text-[13px]">+{{ o.days_delayed }} kun</p>
              <p class="text-ink-4 text-[11px]">kechikkan</p>
            </div>
          </RouterLink>
        </div>
      </div>
    </div>

    <!-- Recent orders table -->
    <div class="card overflow-hidden">
      <div class="flex items-center justify-between px-5 py-4 border-b border-[#E8ECF4]">
        <div class="flex items-center gap-3">
          <div class="icon-box w-9 h-9 icon-box-violet">
            <AppIcon name="receipt_long" :size="18" />
          </div>
          <div>
            <h3 class="font-display font-semibold text-ink text-[14px]">So'nggi buyurtmalar</h3>
            <p class="text-ink-4 text-[11px]">Oxirgi 8 ta buyurtma</p>
          </div>
        </div>
        <RouterLink to="/orders" class="btn-secondary py-1.5 px-3 text-[12px]">
          Barchasini ko'rish
          <AppIcon name="arrow_forward" :size="15" />
        </RouterLink>
      </div>

      <div class="overflow-x-auto">
        <table class="tbl">
          <thead>
            <tr>
              <th class="tbl-th">Raqam</th>
              <th class="tbl-th">Mijoz</th>
              <th class="tbl-th">Holat</th>
              <th class="tbl-th">Muddat</th>
              <th class="tbl-th">Sana</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="ordersStore.loading">
              <td colspan="5" class="tbl-td text-center py-12">
                <div class="inline-block w-8 h-8 rounded-full border-2 border-brand-100 border-t-brand-500 animate-spin" />
              </td>
            </tr>
            <tr v-for="o in ordersStore.orders.slice(0, 8)" :key="o.id" class="tbl-row">
              <td class="tbl-td">
                <RouterLink :to="`/orders/${o.id}`"
                  class="font-mono font-bold text-brand-500 hover:text-brand-600 transition-colors text-[13px]">
                  {{ o.order_no }}
                </RouterLink>
              </td>
              <td class="tbl-td">
                <div class="flex items-center gap-2.5">
                  <div class="w-7 h-7 rounded-full bg-brand-100 text-brand-600 flex items-center justify-center font-bold text-[11px] flex-shrink-0">
                    {{ (o.client?.name || '?').charAt(0).toUpperCase() }}
                  </div>
                  <span class="font-medium text-ink text-[13px]">{{ o.client?.name || '—' }}</span>
                </div>
              </td>
              <td class="tbl-td"><StatusBadge :status="o.status" /></td>
              <td class="tbl-td">
                <span v-if="o.deadline" class="font-medium text-[13px] tabular-nums"
                  :class="isDelayed(o.deadline, o.status) ? 'text-red-500 font-semibold' : 'text-ink-3'">
                  {{ o.deadline }}
                </span>
                <span v-else class="text-ink-5">—</span>
              </td>
              <td class="tbl-td font-mono text-ink-4 text-[12px] tabular-nums">{{ formatDate(o.created_at) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, defineComponent, ref, watch } from 'vue'
import { RouterLink } from 'vue-router'
import { Doughnut } from 'vue-chartjs'
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js'
import { useReportsStore } from '@/stores/reports'
import { useOrdersStore } from '@/stores/orders'
import StatusBadge from '@/components/StatusBadge.vue'
import AppIcon from '@/components/AppIcon.vue'

ChartJS.register(ArcElement, Tooltip, Legend)

const reportsStore = useReportsStore()
const ordersStore  = useOrdersStore()
const delayed      = computed(() => reportsStore.delayed || [])

const todayLabel = computed(() =>
  new Date().toLocaleDateString('uz-UZ', { weekday: 'long', day: 'numeric', month: 'long' })
)

const AnimatedCounter = defineComponent({
  props: { target: { type: Number, default: 0 } },
  setup(props) {
    const current = ref(0)
    watch(() => props.target, (val) => {
      const start = current.value
      const diff  = val - start
      const t0    = performance.now()
      function step(now) {
        const p = Math.min((now - t0) / 700, 1)
        current.value = Math.round(start + diff * (1 - Math.pow(1 - p, 3)))
        if (p < 1) requestAnimationFrame(step)
      }
      requestAnimationFrame(step)
    }, { immediate: true })
    return () => current.value
  },
})

function formatTrend(val) {
  if (val === null || val === undefined) return null
  const abs = Math.abs(val)
  const arrow = val > 0 ? '↑' : val < 0 ? '↓' : '→'
  return `${arrow} ${abs}%`
}

const statCards = computed(() => {
  const d = reportsStore.dashboard
  const totalTrend = formatTrend(d?.total_orders_trend)
  const delayedTrend = formatTrend(d?.delayed_trend)

  return [
    {
      key: 'total_orders', label: 'Jami buyurtmalar', icon: 'inventory_2',
      accent: 'stat-card-blue', iconBox: 'icon-box-blue',
      trendClass: totalTrend
        ? (d.total_orders_trend > 0 ? 'trend-up' : d.total_orders_trend < 0 ? 'trend-down' : 'trend-flat')
        : 'trend-flat',
      trend: totalTrend ?? 'Oy',
    },
    {
      key: 'today_new', label: "Bugun qo'shilgan", icon: 'add_shopping_cart',
      accent: 'stat-card-green', iconBox: 'icon-box-green',
      trendClass: 'trend-flat', trend: 'Bugun',
    },
    {
      key: 'in_progress', label: 'Jarayonda', icon: 'pending_actions',
      accent: 'stat-card-amber', iconBox: 'icon-box-amber',
      trendClass: 'trend-flat', trend: 'Aktiv',
    },
    {
      key: 'delayed', label: 'Kechikkan', icon: 'warning',
      accent: 'stat-card-red', iconBox: 'icon-box-red',
      trendClass: delayedTrend
        ? (d.delayed_trend > 0 ? 'trend-down' : d.delayed_trend < 0 ? 'trend-up' : 'trend-flat')
        : 'trend-flat',
      trend: delayedTrend ?? '—',
    },
  ]
})

const STATUS_LABELS = {
  new: 'Yangi', cutting: 'Kesishda', drilling: 'Teshishda',
  assembling: "Yig'ishda", pending_nachalnik: 'Nachalnik tasdiqida',
  ready: 'Tayyor', delivered: 'Yetkazildi', cancelled: 'Bekor',
}
const STATUS_COLORS = {
  new: '#366EF9', cutting: '#F59E0B', drilling: '#F97316',
  assembling: '#EAB308', pending_nachalnik: '#8B5CF6',
  ready: '#10B981', delivered: '#6B7280', cancelled: '#EF4444',
}

const chartData = computed(() => {
  const byStatus = reportsStore.dashboard?.by_status
  if (!byStatus || !Object.keys(byStatus).length) return null
  const keys = Object.keys(byStatus)
  return {
    labels: keys.map(k => STATUS_LABELS[k] || k),
    datasets: [{
      data: keys.map(k => byStatus[k]),
      backgroundColor: keys.map(k => STATUS_COLORS[k] || '#9CA3AF'),
      borderWidth: 3,
      borderColor: '#ffffff',
      hoverBorderColor: '#ffffff',
      hoverOffset: 4,
    }],
  }
})

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'right',
      labels: {
        color: '#6B7280', font: { size: 11, family: 'Inter' },
        padding: 14, boxWidth: 10, usePointStyle: true, pointStyleWidth: 10,
      },
    },
    tooltip: {
      backgroundColor: '#1A2035',
      titleColor: '#F9FAFB',
      bodyColor: '#9CA3AF',
      padding: 12,
      cornerRadius: 8,
    },
  },
  cutout: '70%',
}

function formatDate(dt) {
  if (!dt) return '—'
  return new Date(dt).toLocaleDateString('uz-UZ')
}

function isDelayed(deadline, status) {
  if (!deadline || ['delivered', 'cancelled'].includes(status)) return false
  return new Date(deadline) < new Date()
}

onMounted(async () => {
  await Promise.all([
    reportsStore.fetchDashboard(),
    ordersStore.fetchOrders({ limit: 10 }),
    reportsStore.fetchDelayed(),
  ])
})
</script>
