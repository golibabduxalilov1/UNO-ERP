<template>
  <div class="space-y-5 animate-fade-in">
    <!-- Loading -->
    <div v-if="ordersStore.loading" class="card p-10 flex flex-col items-center gap-3">
      <div class="w-10 h-10 rounded-full border-[3px] border-brand-100 border-t-brand-500 animate-spin" />
      <p class="text-ink-4 text-[13px]">Yuklanmoqda...</p>
    </div>

    <template v-else-if="order">
      <!-- Header card -->
      <div class="card p-5">
        <div class="flex flex-wrap items-start justify-between gap-4">
          <div>
            <div class="flex flex-wrap items-center gap-2.5 mb-2">
              <span class="font-mono font-bold text-ink text-[22px] tabular-nums">{{ order.order_no }}</span>
              <StatusBadge :status="order.status" />
              <span v-if="isDelayed"
                class="badge"
                style="background:#FEF2F2;border:1px solid #FECACA;color:#991B1B;">
                <AppIcon name="warning" :size="13" class="text-red-400" />
                Kechikkan
              </span>
            </div>
            <p class="text-ink-3 text-[13px]">
              Yaratilgan: {{ formatDate(order.created_at) }}
              <span v-if="order.creator"> — {{ order.creator.full_name }}</span>
            </p>
          </div>
          <div class="flex gap-2 flex-wrap">
            <RouterLink to="/orders" class="btn-secondary">
              <AppIcon name="arrow_back" :size="17" />
              Orqaga
            </RouterLink>
            <button v-if="canCancel" @click="showCancelModal = true" class="btn-danger">
              <AppIcon name="cancel" :size="17" />
              Bekor qilish
            </button>
            <button v-if="canDelete" @click="showDeleteModal = true"
              class="btn-icon border-red-200 text-red-400 hover:bg-red-50 hover:text-red-600 hover:border-red-300">
              <AppIcon name="delete" :size="17" />
            </button>
          </div>
        </div>
      </div>

      <!-- Info cards -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <!-- Client -->
        <div class="card p-5">
          <div class="flex items-center gap-2 mb-4">
            <div class="icon-box w-8 h-8 icon-box-cyan">
              <AppIcon name="person" :size="17" />
            </div>
            <h3 class="font-semibold text-ink text-[14px]">Mijoz ma'lumotlari</h3>
          </div>
          <dl class="space-y-3">
            <div class="flex justify-between items-center py-1.5 border-b border-[#F3F4F6]">
              <dt class="text-ink-3 text-[13px]">Ism</dt>
              <dd class="font-semibold text-ink text-[13px]">{{ order.client?.name || '—' }}</dd>
            </div>
            <div class="flex justify-between items-center py-1.5 border-b border-[#F3F4F6]">
              <dt class="text-ink-3 text-[13px]">Telefon</dt>
              <dd class="font-mono text-brand-500 text-[13px]">{{ order.client?.phone || '—' }}</dd>
            </div>
            <div class="flex justify-between items-start gap-4 py-1.5">
              <dt class="text-ink-3 text-[13px]">Manzil</dt>
              <dd class="text-ink-2 text-[13px] text-right max-w-[200px]">{{ order.client?.address || '—' }}</dd>
            </div>
          </dl>
        </div>

        <!-- Order params -->
        <div class="card p-5">
          <div class="flex items-center gap-2 mb-4">
            <div class="icon-box w-8 h-8 icon-box-blue">
              <AppIcon name="chair" :size="17" />
            </div>
            <h3 class="font-semibold text-ink text-[14px]">Mebel parametrlari</h3>
          </div>
          <dl v-if="order.detail" class="space-y-3">
            <div class="flex justify-between items-center py-1.5 border-b border-[#F3F4F6]">
              <dt class="text-ink-3 text-[13px]">Turi</dt>
              <dd class="font-semibold text-ink text-[13px] capitalize">{{ order.detail.furniture_type }}</dd>
            </div>
            <div class="flex justify-between items-center py-1.5 border-b border-[#F3F4F6]">
              <dt class="text-ink-3 text-[13px]">O'lcham</dt>
              <dd class="font-mono font-bold text-brand-500 text-[12px] tabular-nums">
                {{ order.detail.height_mm }}×{{ order.detail.width_mm }}×{{ order.detail.depth_mm }} mm
              </dd>
            </div>
            <div class="flex justify-between items-center py-1.5 border-b border-[#F3F4F6]">
              <dt class="text-ink-3 text-[13px]">Material</dt>
              <dd class="text-ink-2 text-[13px]">{{ order.detail.material }}</dd>
            </div>
            <div v-if="order.detail.color" class="flex justify-between items-center py-1.5 border-b border-[#F3F4F6]">
              <dt class="text-ink-3 text-[13px]">Rang</dt>
              <dd class="text-ink-2 text-[13px]">{{ order.detail.color }}</dd>
            </div>
            <div v-if="order.detail.notes" class="py-1.5">
              <dt class="text-ink-3 text-[13px] mb-1">Izoh</dt>
              <dd class="text-[13px] p-2.5 rounded-lg" style="background:#FFFBEB;color:#92400E;border:1px solid #FDE68A;">{{ order.detail.notes }}</dd>
            </div>
            <div class="flex justify-between items-center py-1.5">
              <dt class="text-ink-3 text-[13px]">Muddat</dt>
              <dd class="font-semibold text-[13px] tabular-nums" :class="isDelayed ? 'text-red-500' : 'text-ink'">
                {{ order.deadline || 'Belgilanmagan' }}
              </dd>
            </div>
          </dl>
        </div>
      </div>

      <!-- Timeline -->
      <div class="card p-5">
        <div class="flex items-center gap-2 mb-5">
          <div class="icon-box w-8 h-8 icon-box-violet">
            <AppIcon name="timeline" :size="17" />
          </div>
          <h3 class="font-semibold text-ink text-[14px]">Bosqichlar tarixi</h3>
        </div>
        <div v-if="timelineItems.length === 0" class="flex flex-col items-center py-10 gap-3">
          <div class="icon-box w-14 h-14 icon-box-slate rounded-2xl">
            <AppIcon name="assignment" :size="28" />
          </div>
          <p class="text-ink-3 text-[13px]">Hali hech qanday bosqich boshlanmagan</p>
        </div>
        <Timeline v-else :items="timelineItems" />
      </div>
    </template>

    <!-- Not found -->
    <div v-else class="card flex flex-col items-center py-20 gap-4">
      <div class="icon-box w-16 h-16 icon-box-slate rounded-2xl">
        <AppIcon name="error_outline" :size="32" />
      </div>
      <div class="text-center">
        <p class="font-display font-semibold text-ink text-[15px]">Buyurtma topilmadi</p>
        <p class="text-ink-3 text-[13px] mt-1">Berilgan ID bo'yicha buyurtma mavjud emas</p>
      </div>
      <RouterLink to="/orders" class="btn-secondary">
        <AppIcon name="arrow_back" :size="16" />
        Buyurtmalarga qaytish
      </RouterLink>
    </div>

    <ConfirmModal
      v-model="showCancelModal"
      title="Buyurtmani bekor qilish"
      message="Bu amalni qaytarib bo'lmaydi. Buyurtmani bekor qilmoqchimisiz?"
      confirm-text="Ha, bekor qilish"
      :dangerous="true"
      @confirm="cancelOrder"
    />
    <ConfirmModal
      v-model="showDeleteModal"
      title="Buyurtmani o'chirish"
      message="Buyurtma butunlay o'chiriladi. Bu amalni qaytarib bo'lmaydi!"
      confirm-text="Ha, o'chirish"
      :dangerous="true"
      @confirm="deleteOrder"
    />
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import { useOrdersStore } from '@/stores/orders'
import StatusBadge from '@/components/StatusBadge.vue'
import Timeline from '@/components/Timeline.vue'
import ConfirmModal from '@/components/ConfirmModal.vue'
import AppIcon from '@/components/AppIcon.vue'

const route       = useRoute()
const router      = useRouter()
const ordersStore = useOrdersStore()
const showCancelModal = ref(false)
const showDeleteModal = ref(false)

const order     = computed(() => ordersStore.currentOrder)
const canCancel = computed(() => order.value && !['delivered','cancelled'].includes(order.value.status))
const canDelete = computed(() => order.value && ['new','cancelled'].includes(order.value.status))
const isDelayed = computed(() => {
  if (!order.value?.deadline) return false
  if (['delivered','cancelled'].includes(order.value?.status)) return false
  return new Date(order.value.deadline) < new Date()
})

const STAGE_LABELS = { cutting:'Kesish', drilling:'Teshish', assembling:"Yig'ish/Montaj", quality_check:'Sifat nazorati' }

const timelineItems = computed(() => {
  if (!order.value?.stages) return []
  const items = []
  for (const s of order.value.stages) {
    const sl     = STAGE_LABELS[s.stage] || s.stage
    const worker = s.worker?.full_name || "Noma'lum"
    if (s.started_at)            items.push({ title:`${sl} boshlandi`,    subtitle:`Ishchi: ${worker}`, time:formatDate(s.started_at),            status:'in_progress' })
    if (s.finished_at)           items.push({ title:`${sl} yakunlandi`,   subtitle:`Ishchi: ${worker}`, time:formatDate(s.finished_at),           status:'pending_brigadir' })
    if (s.brigadir_confirmed_at) items.push({ title:'Brigadir tasdiqladi', subtitle:s.brigadir?.full_name, time:formatDate(s.brigadir_confirmed_at), status:'pending_nachalnik' })
    if (s.brigadir_reject_reason) items.push({ title:'Brigadir rad etdi', reason:s.brigadir_reject_reason, time:formatDate(s.brigadir_confirmed_at), status:'rejected' })
    if (s.nachalnik_confirmed_at) items.push({ title:'Nachalnik tasdiqladi', subtitle:s.nachalnik?.full_name, time:formatDate(s.nachalnik_confirmed_at), status:'confirmed' })
    if (s.nachalnik_reject_reason) items.push({ title:'Nachalnik rad etdi', reason:s.nachalnik_reject_reason, time:formatDate(s.nachalnik_confirmed_at), status:'rejected' })
  }
  if (order.value.delivery) {
    items.push({ title:'Yetkazib berildi', subtitle:order.value.delivery.driver_name, time:formatDate(order.value.delivery.delivered_at), status:'delivered' })
  }
  return items
})

function formatDate(dt) { if (!dt) return '—'; return new Date(dt).toLocaleString('uz-UZ') }

async function cancelOrder() {
  await ordersStore.updateOrder(order.value.id, { status:'cancelled' })
}

async function deleteOrder() {
  await ordersStore.deleteOrder(order.value.id)
  router.push('/orders')
}

onMounted(() => ordersStore.fetchOrder(route.params.id))
</script>
