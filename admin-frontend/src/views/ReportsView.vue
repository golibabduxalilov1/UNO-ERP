<template>
  <div class="space-y-5 animate-fade-in">
    <!-- Header -->
    <div>
      <h1 class="font-display font-bold text-ink text-[22px]">Hisobotlar</h1>
      <p class="text-ink-3 text-[13px] mt-0.5">Ishchilar ishlashi va kechikkan buyurtmalar tahlili</p>
    </div>

    <!-- Tabs -->
    <div class="flex gap-1 p-1 rounded-xl bg-[#F3F4F6] w-fit">
      <button
        v-for="tab in tabs" :key="tab.key"
        @click="activeTab = tab.key"
        class="flex items-center gap-2 px-4 py-2 rounded-lg text-[13px] font-semibold transition-all duration-150 cursor-pointer"
        :class="activeTab === tab.key
          ? 'bg-white text-brand-600 border border-[#E8ECF4]'
          : 'text-ink-3 hover:text-ink'"
      >
        <AppIcon :name="tab.icon" :size="16" />
        {{ tab.label }}
      </button>
    </div>

    <!-- Monthly report -->
    <template v-if="activeTab === 'monthly'">
      <div class="card p-4 flex items-end gap-3 flex-wrap">
        <div>
          <label class="label">Oy va yil</label>
          <input v-model="monthYear" type="month" class="input w-44" />
        </div>
        <button @click="fetchMonthly" class="btn-primary">
          <AppIcon name="refresh" :size="17" />
          Ko'rish
        </button>
      </div>

      <div class="card overflow-hidden">
        <div v-if="reportsStore.loading" class="p-10 flex flex-col items-center gap-3">
          <div class="w-10 h-10 rounded-full border-[3px] border-brand-100 border-t-brand-500 animate-spin" />
          <p class="text-ink-4 text-[13px]">Yuklanmoqda...</p>
        </div>
        <div v-else-if="reportsStore.monthly.length === 0"
          class="py-16 flex flex-col items-center gap-4">
          <div class="icon-box w-16 h-16 icon-box-slate rounded-2xl">
            <AppIcon name="bar_chart" :size="32" />
          </div>
          <div class="text-center">
            <p class="font-display font-semibold text-ink text-[15px]">Ma'lumot topilmadi</p>
            <p class="text-ink-3 text-[13px] mt-1">Bu oy uchun hisobot mavjud emas</p>
          </div>
          <button @click="fetchMonthly" class="btn-secondary">
            <AppIcon name="refresh" :size="16" />
            Yangilash
          </button>
        </div>
        <div v-else class="overflow-x-auto">
          <table class="tbl" style="min-width:520px;">
            <thead>
              <tr>
                <th class="tbl-th">#</th>
                <th class="tbl-th">Ishchi</th>
                <th class="tbl-th">Rol</th>
                <th class="tbl-th">Bajarilgan bosqichlar</th>
                <th class="tbl-th text-right">Amallar</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(w, idx) in reportsStore.monthly" :key="w.user_id" class="tbl-row group">
                <td class="tbl-td font-mono text-ink-4 text-[12px] tabular-nums">{{ idx + 1 }}</td>
                <td class="tbl-td">
                  <div class="flex items-center gap-2.5">
                    <div class="w-8 h-8 rounded-full bg-brand-100 text-brand-600 flex items-center justify-center font-bold text-[12px] flex-shrink-0">
                      {{ w.full_name?.charAt(0) || '?' }}
                    </div>
                    <span class="font-semibold text-ink text-[13px]">{{ w.full_name }}</span>
                  </div>
                </td>
                <td class="tbl-td">
                  <span class="badge" style="background:#EFF4FF;border:1px solid #C4D8FD;color:#1234A8;">
                    {{ ROLE_LABELS[w.role] || w.role }}
                  </span>
                </td>
                <td class="tbl-td">
                  <div class="flex items-center gap-3">
                    <span class="font-display font-bold text-brand-500 text-[20px] tabular-nums">{{ w.total_count }}</span>
                    <div class="flex-1 max-w-[120px] h-2 rounded-full bg-[#EFF4FF] overflow-hidden">
                      <div class="h-full rounded-full bg-brand-400 transition-all duration-500"
                        :style="{ width: `${Math.min((w.total_count / maxCount) * 100, 100)}%` }" />
                    </div>
                  </div>
                </td>
                <td class="tbl-td text-right">
                  <button @click="showWorkerDetail(w)"
                    class="btn-icon" title="Batafsil">
                    <AppIcon name="visibility" :size="17" />
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </template>

    <!-- Delayed orders -->
    <template v-if="activeTab === 'delayed'">
      <div class="flex items-center justify-between flex-wrap gap-3">
        <div class="flex items-center gap-2 px-3 py-2 rounded-lg"
          style="background:#FEF2F2;border:1px solid #FECACA;">
          <span class="w-2 h-2 rounded-full bg-red-400" />
          <span class="text-red-600 text-[13px] font-semibold tabular-nums">
            {{ reportsStore.delayed.length }} ta kechikkan buyurtma
          </span>
        </div>
        <button @click="reportsStore.fetchDelayed()" class="btn-secondary">
          <AppIcon name="refresh" :size="17" />
          Yangilash
        </button>
      </div>

      <div class="card overflow-hidden">
        <div v-if="reportsStore.loading" class="p-10 flex flex-col items-center gap-3">
          <div class="w-10 h-10 rounded-full border-[3px] border-brand-100 border-t-brand-500 animate-spin" />
        </div>
        <div v-else-if="reportsStore.delayed.length === 0"
          class="py-16 flex flex-col items-center gap-4">
          <div class="icon-box w-16 h-16 icon-box-green rounded-2xl">
            <AppIcon name="check_circle" :size="32" />
          </div>
          <div class="text-center">
            <p class="font-display font-semibold text-green-700 text-[15px]">Kechikkan buyurtmalar yo'q!</p>
            <p class="text-ink-3 text-[13px] mt-1">Barcha buyurtmalar vaqtida bajarilmoqda</p>
          </div>
        </div>
        <div v-else class="overflow-x-auto">
          <table class="tbl" style="min-width:560px;">
            <thead>
              <tr>
                <th class="tbl-th">Raqam</th>
                <th class="tbl-th">Mijoz</th>
                <th class="tbl-th">Holat</th>
                <th class="tbl-th">Muddat</th>
                <th class="tbl-th">Kechikish</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="o in reportsStore.delayed" :key="o.order_id" class="tbl-row">
                <td class="tbl-td">
                  <RouterLink :to="`/orders/${o.order_id}`"
                    class="font-mono font-bold text-red-500 hover:text-red-600 text-[13px]">
                    {{ o.order_no }}
                  </RouterLink>
                </td>
                <td class="tbl-td font-medium text-ink text-[13px]">{{ o.client_name }}</td>
                <td class="tbl-td"><StatusBadge :status="o.status" /></td>
                <td class="tbl-td font-mono text-red-400 text-[13px] tabular-nums">{{ o.deadline }}</td>
                <td class="tbl-td">
                  <span class="badge" style="background:#FEF2F2;border:1px solid #FECACA;color:#991B1B;">
                    <span class="w-1.5 h-1.5 rounded-full bg-red-400" />
                    +{{ o.days_delayed }} kun kech
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </template>

    <!-- Worker detail modal -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="workerDetail"
          class="fixed inset-0 z-50 flex items-center justify-center p-4 sidebar-backdrop"
          @click.self="workerDetail = null">
          <div class="card p-6 w-full max-w-lg max-h-[80vh] flex flex-col">
            <div class="flex items-center justify-between mb-5">
              <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-full bg-brand-100 text-brand-600 flex items-center justify-center font-bold flex-shrink-0">
                  {{ workerDetail.full_name?.charAt(0) || '?' }}
                </div>
                <div>
                  <p class="font-display font-bold text-ink text-[15px]">{{ workerDetail.full_name }}</p>
                  <p class="text-ink-4 text-[12px] tabular-nums">{{ workerDetail.total_count }} ta bosqich bajarilgan</p>
                </div>
              </div>
              <button @click="workerDetail = null" class="btn-icon">
                <AppIcon name="close" :size="18" />
              </button>
            </div>
            <div class="overflow-y-auto flex-1">
              <table class="tbl">
                <thead>
                  <tr>
                    <th class="tbl-th">Buyurtma</th>
                    <th class="tbl-th">Bosqich</th>
                    <th class="tbl-th">Davomiyligi</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="s in workerDetail.stages" :key="s.stage_id" class="tbl-row">
                    <td class="tbl-td font-mono text-brand-500 text-[12px] tabular-nums">#{{ s.order_id }}</td>
                    <td class="tbl-td">
                      <span class="badge" style="background:#EFF4FF;border:1px solid #C4D8FD;color:#1234A8;font-size:11px;">
                        {{ STAGE_LABELS[s.stage] || s.stage }}
                      </span>
                    </td>
                    <td class="tbl-td text-ink-3 text-[12px] tabular-nums">
                      {{ s.duration_minutes ? `${s.duration_minutes} daqiqa` : '—' }}
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import { useReportsStore } from '@/stores/reports'
import StatusBadge from '@/components/StatusBadge.vue'
import AppIcon from '@/components/AppIcon.vue'

const reportsStore = useReportsStore()
const activeTab    = ref('monthly')
const workerDetail = ref(null)
const now          = new Date()
const monthYear    = ref(`${now.getFullYear()}-${String(now.getMonth()+1).padStart(2,'0')}`)

const tabs = [
  { key: 'monthly', icon: 'bar_chart', label: 'Oylik hisobot' },
  { key: 'delayed', icon: 'alarm_on',  label: 'Kechikkanlar' },
]

const ROLE_LABELS  = { admin:'Admin', manager:'Menejer', brigadir:'Brigadir', nachalnik:'Nachalnik', operator:'Operator', cutter:'Kesuvchi', driller:'Teshuvchi', driver:'Haydovchi', director:'Direktor' }
const STAGE_LABELS = { cutting:'Kesish', drilling:'Teshish', assembling:"Yig'ish", quality_check:'Sifat nazorati' }

const maxCount = computed(() => Math.max(...reportsStore.monthly.map(w => w.total_count), 1))

function fetchMonthly() {
  const [year, month] = monthYear.value.split('-')
  reportsStore.fetchMonthly({ year, month })
}

function showWorkerDetail(worker) { workerDetail.value = worker }

onMounted(() => { fetchMonthly(); reportsStore.fetchDelayed() })
</script>
