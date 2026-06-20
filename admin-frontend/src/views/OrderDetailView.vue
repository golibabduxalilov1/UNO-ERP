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
              <StatusBadge :status="effectiveStatus" />
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
            <button @click="openEdit" class="btn-icon btn-icon--warning" title="Tahrirlash">
              <AppIcon name="edit" :size="17" />
            </button>
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
            <div v-if="order.detail.holes" class="flex justify-between items-center py-1.5 border-b border-[#F3F4F6]">
              <dt class="text-ink-3 text-[13px]">Teshish</dt>
              <dd class="text-ink-2 text-[13px] text-right max-w-[200px]">{{ order.detail.holes }}</dd>
            </div>
            <div v-if="order.detail.cuts" class="flex justify-between items-center py-1.5 border-b border-[#F3F4F6]">
              <dt class="text-ink-3 text-[13px]">Kesish</dt>
              <dd class="text-ink-2 text-[13px] text-right max-w-[200px]">{{ order.detail.cuts }}</dd>
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

    <!-- Edit Modal -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="showEditModal"
          class="fixed inset-0 z-50 flex items-center justify-center p-4 sidebar-backdrop"
          @click.self="showEditModal = false">
          <div class="card p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">

            <!-- Modal header -->
            <div class="flex items-center gap-3 mb-5">
              <div class="icon-box w-10 h-10 icon-box-amber">
                <AppIcon name="edit" :size="20" />
              </div>
              <div>
                <h3 class="font-display font-bold text-ink text-[16px]">Buyurtmani tahrirlash</h3>
                <p class="text-ink-4 text-[12px]">{{ order?.order_no }}</p>
              </div>
              <button @click="showEditModal = false" class="btn-icon ml-auto">
                <AppIcon name="close" :size="17" />
              </button>
            </div>

            <div class="space-y-5">
              <!-- Muddat -->
              <div>
                <label class="label">Yetkazib berish muddati</label>
                <div class="relative">
                  <AppIcon name="calendar_month" :size="15" class="absolute left-3 top-1/2 -translate-y-1/2 text-ink-4 pointer-events-none" />
                  <input v-model="editForm.deadline" type="date" class="input pl-9" />
                </div>
              </div>

              <!-- Mebel turi -->
              <div>
                <label class="label">Mebel turi *</label>
                <div class="grid grid-cols-4 gap-2">
                  <button v-for="t in FURNITURE_TYPES" :key="t" type="button"
                    @click="editForm.furniture_type = t"
                    class="py-2 px-3 rounded-lg border text-[13px] font-medium transition-all"
                    :class="editForm.furniture_type === t
                      ? 'bg-brand-500 border-brand-500 text-white shadow-sm'
                      : 'bg-white border-[#E8ECF4] text-ink-3 hover:border-brand-300 hover:text-brand-500'">
                    {{ t }}
                  </button>
                </div>
                <input v-if="!FURNITURE_TYPES.includes(editForm.furniture_type)"
                  v-model="editForm.furniture_type"
                  class="input mt-2" placeholder="Mebel turini kiriting..." />
              </div>

              <!-- O'lchamlar -->
              <div>
                <label class="label">O'lchamlar (mm) *</label>
                <div class="grid grid-cols-3 gap-3">
                  <div>
                    <div class="relative">
                      <input v-model.number="editForm.height_mm" class="input pr-10 text-center" type="number" min="1" placeholder="0" />
                      <span class="absolute right-3 top-1/2 -translate-y-1/2 text-ink-4 text-[11px] font-semibold pointer-events-none">mm</span>
                    </div>
                    <p class="text-center text-[11px] text-ink-4 mt-1">Bo'yi</p>
                  </div>
                  <div>
                    <div class="relative">
                      <input v-model.number="editForm.width_mm" class="input pr-10 text-center" type="number" min="1" placeholder="0" />
                      <span class="absolute right-3 top-1/2 -translate-y-1/2 text-ink-4 text-[11px] font-semibold pointer-events-none">mm</span>
                    </div>
                    <p class="text-center text-[11px] text-ink-4 mt-1">Eni</p>
                  </div>
                  <div>
                    <div class="relative">
                      <input v-model.number="editForm.depth_mm" class="input pr-10 text-center" type="number" min="1" placeholder="0" />
                      <span class="absolute right-3 top-1/2 -translate-y-1/2 text-ink-4 text-[11px] font-semibold pointer-events-none">mm</span>
                    </div>
                    <p class="text-center text-[11px] text-ink-4 mt-1">Chuqurligi</p>
                  </div>
                </div>
              </div>

              <!-- Material -->
              <div>
                <label class="label">Material *</label>
                <div class="grid grid-cols-4 gap-1.5">
                  <button v-for="m in MATERIALS" :key="m" type="button"
                    @click="editForm.material = m"
                    class="py-1.5 px-2 rounded-lg border text-[12px] font-medium transition-all"
                    :class="editForm.material === m
                      ? 'bg-brand-500 border-brand-500 text-white'
                      : 'bg-white border-[#E8ECF4] text-ink-3 hover:border-brand-300 hover:text-brand-500'">
                    {{ m }}
                  </button>
                </div>
                <input v-if="!MATERIALS.includes(editForm.material)"
                  v-model="editForm.material"
                  class="input mt-2" placeholder="Material nomini kiriting..." />
              </div>

              <!-- Rang -->
              <div>
                <label class="label">Rang</label>
                <input v-model="editForm.color" class="input" placeholder="Oq, Qo'ng'ir..." />
              </div>

              <!-- Teshish, Kesish, Izoh -->
              <div class="grid grid-cols-1 gap-3">
                <div>
                  <label class="label">Teshish joylari</label>
                  <textarea v-model="editForm.holes" class="input" rows="2" placeholder="Teshish joylari tavsifi..." />
                </div>
                <div>
                  <label class="label">Kesish tafsilotlari</label>
                  <textarea v-model="editForm.cuts" class="input" rows="2" placeholder="Qo'shimcha kesish o'lchamlari..." />
                </div>
                <div>
                  <label class="label">Izoh</label>
                  <textarea v-model="editForm.notes" class="input" rows="2" placeholder="Qo'shimcha izoh..." />
                </div>
              </div>

              <!-- Error -->
              <div v-if="editError" class="p-3 rounded-lg text-[12px]"
                style="background:#FEF2F2;border:1px solid #FECACA;color:#991B1B;">
                {{ editError }}
              </div>
            </div>

            <div class="flex gap-2.5 justify-end mt-6 pt-4 border-t border-[#E8ECF4]">
              <button class="btn-secondary" @click="showEditModal = false">Bekor</button>
              <button class="btn-primary" @click="saveEdit" :disabled="editSaving">
                <AppIcon v-if="editSaving" name="progress_activity" :size="16" class="animate-spin" />
                <AppIcon v-else name="save" :size="16" />
                {{ editSaving ? 'Saqlanmoqda...' : 'Saqlash' }}
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

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
import { computed, onMounted, reactive, ref } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import { useOrdersStore } from '@/stores/orders'
import StatusBadge from '@/components/StatusBadge.vue'
import Timeline from '@/components/Timeline.vue'
import ConfirmModal from '@/components/ConfirmModal.vue'
import AppIcon from '@/components/AppIcon.vue'
import { useToast } from '@/composables/useToast'

const toast = useToast()

const route       = useRoute()
const router      = useRouter()
const ordersStore = useOrdersStore()
const showCancelModal = ref(false)
const showDeleteModal = ref(false)
const showEditModal   = ref(false)
const editSaving      = ref(false)
const editError       = ref('')

const FURNITURE_TYPES = ['Shkaf', 'Stol', 'Stul', 'Divan', 'Krovat', 'Javon', 'Tokcha', 'Boshqa']
const MATERIALS       = ['DSP', 'MDF', 'Faner', 'Metall', 'Shisha', 'Kompozit', 'Boshqa']

const editForm = reactive({
  deadline: '', furniture_type: '',
  height_mm: null, width_mm: null, depth_mm: null,
  material: '', color: '', holes: '', cuts: '', notes: '',
})

const order = computed(() => ordersStore.currentOrder)

const effectiveStatus = computed(() => {
  if (!order.value) return ''
  const stages = order.value.stages || []
  if (stages.some(s => s.status === 'pending_nachalnik')) return 'pending_nachalnik'
  if (stages.some(s => s.status === 'pending_brigadir'))  return 'pending_brigadir'
  return order.value.status
})

const canCancel = computed(() => order.value && !['delivered', 'cancelled'].includes(order.value.status))
const canDelete = computed(() => order.value && ['new', 'cancelled'].includes(order.value.status))
const isDelayed = computed(() => {
  if (!order.value?.deadline) return false
  if (['delivered', 'cancelled'].includes(order.value?.status)) return false
  return new Date(order.value.deadline) < new Date()
})

const STAGE_LABELS = { cutting: 'Kesish', drilling: 'Teshish', assembling: "Yig'ish/Montaj" }

const timelineItems = computed(() => {
  if (!order.value?.stages) return []
  const items = []
  for (const s of order.value.stages) {
    const sl     = STAGE_LABELS[s.stage] || s.stage
    const worker = s.worker?.full_name || "Noma'lum"
    if (s.started_at)             items.push({ title: `${sl} boshlandi`,     subtitle: `Ishchi: ${worker}`,      time: formatDate(s.started_at),             status: 'in_progress' })
    if (s.finished_at)            items.push({ title: `${sl} yakunlandi`,    subtitle: `Ishchi: ${worker}`,      time: formatDate(s.finished_at),            status: 'pending_brigadir' })
    if (s.brigadir_confirmed_at)  items.push({ title: 'Brigadir tasdiqladi', subtitle: s.brigadir?.full_name,   time: formatDate(s.brigadir_confirmed_at),  status: 'pending_nachalnik' })
    if (s.brigadir_reject_reason) items.push({ title: 'Brigadir rad etdi',   reason: s.brigadir_reject_reason,  time: formatDate(s.brigadir_confirmed_at),  status: 'rejected' })
    if (s.nachalnik_confirmed_at) items.push({ title: 'Nachalnik tasdiqladi', subtitle: s.nachalnik?.full_name, time: formatDate(s.nachalnik_confirmed_at), status: 'confirmed' })
    if (s.nachalnik_reject_reason) items.push({ title: 'Nachalnik rad etdi', reason: s.nachalnik_reject_reason, time: formatDate(s.nachalnik_confirmed_at), status: 'rejected' })
  }
  if (order.value.delivery) {
    items.push({ title: 'Yetkazib berildi', subtitle: order.value.delivery.driver_name, time: formatDate(order.value.delivery.delivered_at), status: 'delivered' })
  }
  return items
})

function formatDate(dt) {
  if (!dt) return '—'
  return new Date(dt).toLocaleString('uz-UZ')
}

function openEdit() {
  const o = order.value
  editForm.deadline       = o.deadline || ''
  editForm.furniture_type = o.detail?.furniture_type || ''
  editForm.height_mm      = o.detail?.height_mm || null
  editForm.width_mm       = o.detail?.width_mm || null
  editForm.depth_mm       = o.detail?.depth_mm || null
  editForm.material       = o.detail?.material || ''
  editForm.color          = o.detail?.color || ''
  editForm.holes          = o.detail?.holes || ''
  editForm.cuts           = o.detail?.cuts || ''
  editForm.notes          = o.detail?.notes || ''
  editError.value = ''
  showEditModal.value = true
}

async function saveEdit() {
  editError.value = ''
  if (!editForm.furniture_type.trim()) { editError.value = 'Mebel turini kiriting'; return }
  if (!editForm.height_mm || !editForm.width_mm || !editForm.depth_mm) { editError.value = "O'lchamlarni kiriting"; return }
  if (!editForm.material.trim()) { editError.value = 'Materialni kiriting'; return }
  editSaving.value = true
  try {
    await ordersStore.updateOrder(order.value.id, {
      deadline:       editForm.deadline || null,
      furniture_type: editForm.furniture_type,
      height_mm:      editForm.height_mm,
      width_mm:       editForm.width_mm,
      depth_mm:       editForm.depth_mm,
      material:       editForm.material,
      color:          editForm.color  || null,
      holes:          editForm.holes  || null,
      cuts:           editForm.cuts   || null,
      notes:          editForm.notes  || null,
    })
    showEditModal.value = false
    toast.success("Buyurtma yangilandi")
  } catch (e) {
    editError.value = e.response?.data?.detail || 'Xatolik yuz berdi'
  } finally {
    editSaving.value = false
  }
}

async function cancelOrder() {
  await ordersStore.updateOrder(order.value.id, { status: 'cancelled' })
  toast.info("Buyurtma bekor qilindi")
}

async function deleteOrder() {
  await ordersStore.deleteOrder(order.value.id)
  toast.success("Buyurtma o'chirildi")
  router.push('/orders')
}

onMounted(() => ordersStore.fetchOrder(route.params.id))
</script>
