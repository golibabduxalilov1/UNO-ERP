<template>
  <div class="space-y-5 animate-fade-in">
    <!-- Header -->
    <div>
      <h1 class="font-display font-bold text-ink text-[22px]">Shikoyat tekshiruvi</h1>
      <p class="text-ink-3 text-[13px] mt-0.5">Buyurtmaning to'liq tarixi va bosqichlarini tekshirish</p>
    </div>

    <!-- Search -->
    <div class="card p-5">
      <p class="text-ink-3 text-[13px] mb-4">
        Shikoyat bo'yicha buyurtmaning tarixini ko'rish uchun raqamini kiriting.
      </p>
      <div class="flex gap-3 flex-wrap">
        <div class="relative flex-1 min-w-[200px]">
          <AppIcon name="search" :size="17" class="absolute left-3 top-1/2 -translate-y-1/2 text-ink-4 pointer-events-none" />
          <input
            v-model="orderNo"
            @keyup.enter="search"
            class="input pl-9 font-mono uppercase"
            placeholder="MBL-2024-0001"
            :disabled="loading"
          />
        </div>
        <button @click="search" class="btn-primary" :disabled="loading || !orderNo.trim()">
          <AppIcon v-if="loading" name="progress_activity" :size="17" class="animate-spin" />
          <AppIcon v-else name="manage_search" :size="17" />
          {{ loading ? 'Qidirilmoqda...' : 'Qidirish' }}
        </button>
      </div>
      <div v-if="error"
        class="flex items-center gap-2 mt-3 p-3 rounded-lg text-[13px]"
        style="background:#FEF2F2;border:1px solid #FECACA;color:#991B1B;">
        <AppIcon name="error" :size="17" class="flex-shrink-0 text-red-400" />
        {{ error }}
      </div>
    </div>

    <!-- Result -->
    <template v-if="result">
      <!-- Summary -->
      <div class="card p-5">
        <div class="flex items-start justify-between gap-4 flex-wrap">
          <div>
            <p class="font-mono font-bold text-ink text-[22px] tabular-nums">{{ result.order_no }}</p>
            <p class="text-ink-3 text-[13px] mt-1">
              Qabul qilingan: {{ formatDt(result.created_at) }}
              <span v-if="result.created_by"> — {{ result.created_by }}</span>
            </p>
          </div>
          <StatusBadge :status="result.status" />
        </div>
        <div class="flex items-center gap-2 mt-4 pt-4 border-t border-[#E8ECF4] text-[13px] text-ink-3">
          <AppIcon name="calendar_today" :size="16" class="text-ink-4" />
          Muddat:
          <span class="font-semibold text-ink ml-1">{{ result.deadline || 'Belgilanmagan' }}</span>
        </div>
      </div>

      <!-- Stages table -->
      <div class="card overflow-hidden">
        <div class="flex items-center gap-2 px-5 py-4 border-b border-[#E8ECF4]">
          <div class="icon-box w-8 h-8 icon-box-violet">
            <AppIcon name="timeline" :size="17" />
          </div>
          <h3 class="font-semibold text-ink text-[14px]">Ishlov bosqichlari</h3>
        </div>
        <div class="overflow-x-auto">
          <table class="tbl" style="min-width:680px;">
            <thead>
              <tr>
                <th class="tbl-th">Bosqich</th>
                <th class="tbl-th">Ishchi</th>
                <th class="tbl-th">Boshlangan</th>
                <th class="tbl-th">Yakunlangan</th>
                <th class="tbl-th">Brigadir</th>
                <th class="tbl-th">Nachalnik</th>
                <th class="tbl-th">Holat</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="result.stages.length === 0">
                <td colspan="7" class="tbl-td text-center py-10 text-ink-4">Bosqich yo'q</td>
              </tr>
              <tr v-for="s in result.stages" :key="s.stage" class="tbl-row">
                <td class="tbl-td font-semibold text-ink text-[13px]">{{ STAGE_LABELS[s.stage] || s.stage }}</td>
                <td class="tbl-td text-brand-500 font-medium text-[13px]">{{ s.worker_name || '—' }}</td>
                <td class="tbl-td font-mono text-ink-4 text-[12px] tabular-nums">{{ formatDt(s.started_at) }}</td>
                <td class="tbl-td font-mono text-ink-4 text-[12px] tabular-nums">{{ formatDt(s.finished_at) }}</td>
                <td class="tbl-td text-[12px]">
                  <div v-if="s.brigadir_name">
                    <p :class="s.brigadir_reject_reason ? 'text-red-500' : 'text-emerald-600'" class="font-semibold">{{ s.brigadir_name }}</p>
                    <p v-if="s.brigadir_reject_reason" class="text-red-400 mt-0.5">{{ s.brigadir_reject_reason }}</p>
                  </div>
                  <span v-else class="text-ink-5">—</span>
                </td>
                <td class="tbl-td text-[12px]">
                  <div v-if="s.nachalnik_name">
                    <p :class="s.nachalnik_reject_reason ? 'text-red-500' : 'text-emerald-600'" class="font-semibold">{{ s.nachalnik_name }}</p>
                    <p v-if="s.nachalnik_reject_reason" class="text-red-400 mt-0.5">{{ s.nachalnik_reject_reason }}</p>
                  </div>
                  <span v-else class="text-ink-5">—</span>
                </td>
                <td class="tbl-td"><StatusBadge :status="s.status" /></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Delivery -->
      <div v-if="result.delivery" class="card p-5"
        style="border-color:#A7F3D0; background:#F0FDF4;">
        <div class="flex items-center gap-2 mb-4">
          <div class="icon-box w-9 h-9 icon-box-green">
            <AppIcon name="local_shipping" :size="19" />
          </div>
          <h3 class="font-display font-semibold text-emerald-700 text-[14px]">Yetkazib berildi</h3>
        </div>
        <div class="space-y-2.5">
          <div class="flex justify-between text-[13px]">
            <span class="text-ink-3">Haydovchi</span>
            <span class="font-semibold text-ink">{{ result.delivery.driver_name }}</span>
          </div>
          <div class="flex justify-between text-[13px]">
            <span class="text-ink-3">Yetkazilgan vaqt</span>
            <span class="font-mono text-emerald-600 tabular-nums">{{ formatDt(result.delivery.delivered_at) }}</span>
          </div>
          <div v-if="result.delivery.notes" class="flex justify-between text-[13px]">
            <span class="text-ink-3">Izoh</span>
            <span class="text-ink">{{ result.delivery.notes }}</span>
          </div>
        </div>
      </div>
      <div v-else class="card p-5 flex flex-col items-center gap-2 text-center"
        style="border-style:dashed; border-color:#D1D5DB;">
        <AppIcon name="local_shipping" :size="28" class="text-ink-5" />
        <p class="text-ink-3 text-[13px]">Hali yetkazilmagan</p>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { reportsApi } from '@/api'
import StatusBadge from '@/components/StatusBadge.vue'
import AppIcon from '@/components/AppIcon.vue'

const orderNo = ref('')
const result  = ref(null)
const loading = ref(false)
const error   = ref('')

const STAGE_LABELS = { cutting:'Kesish', drilling:'Teshish', assembling:"Yig'ish/Montaj" }

async function search() {
  if (!orderNo.value.trim()) return
  loading.value = true; error.value = ''; result.value = null
  try {
    const res = await reportsApi.orderHistory(orderNo.value.trim().toUpperCase())
    result.value = res.data
  } catch (e) {
    error.value = e.response?.data?.detail || 'Buyurtma topilmadi'
  } finally { loading.value = false }
}

function formatDt(dt) { if (!dt) return '—'; return new Date(dt).toLocaleString('uz-UZ') }
</script>
