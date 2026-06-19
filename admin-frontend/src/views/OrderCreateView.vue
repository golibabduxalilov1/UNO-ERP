<template>
  <div class="space-y-5 animate-fade-in">

    <!-- Header -->
    <div class="page-header">
      <div class="flex items-center gap-3">
        <RouterLink to="/orders" class="btn-icon flex-shrink-0">
          <AppIcon name="arrow_back" :size="20" />
        </RouterLink>
        <div>
          <h1 class="font-display font-bold text-ink text-[22px]">Yangi buyurtma</h1>
          <p class="text-ink-3 text-[13px]">Yangi mebel buyurtmasini ro'yxatdan o'tkazish</p>
        </div>
      </div>
    </div>

    <!-- Success -->
    <div v-if="createdOrderNo" class="card p-12 text-center max-w-lg mx-auto">
      <div class="w-20 h-20 rounded-3xl bg-emerald-50 border border-emerald-100 flex items-center justify-center mx-auto mb-6">
        <AppIcon name="check_circle" :size="42" class="text-emerald-500" />
      </div>
      <p class="font-display font-bold text-ink text-[22px] mb-1">Buyurtma yaratildi!</p>
      <p class="text-ink-4 text-[13px] mb-4">Buyurtma muvaffaqiyatli ro'yxatdan o'tkazildi</p>
      <p class="font-mono font-bold text-brand-500 text-[32px] mb-8 tabular-nums">{{ createdOrderNo }}</p>
      <div class="flex gap-3 justify-center flex-wrap">
        <RouterLink :to="`/orders/${createdOrderId}`" class="btn-primary">
          <AppIcon name="visibility" :size="17" />
          Buyurtmani ko'rish
        </RouterLink>
        <button @click="resetForm" class="btn-secondary">
          <AppIcon name="add" :size="17" />
          Yangi buyurtma
        </button>
      </div>
    </div>

    <!-- Form -->
    <template v-else>
      <div class="grid grid-cols-1 xl:grid-cols-5 gap-5 items-start">

        <!-- LEFT: Mijoz -->
        <div class="xl:col-span-2 space-y-4">
          <div class="card p-5">
            <div class="flex items-center gap-2 mb-5 pb-4 border-b border-[#E8ECF4]">
              <div class="icon-box w-9 h-9 icon-box-cyan">
                <AppIcon name="person" :size="18" />
              </div>
              <div>
                <h3 class="font-semibold text-ink text-[15px]">Mijoz ma'lumotlari</h3>
                <p class="text-ink-4 text-[11px]">Mavjud mijozni qidiring yoki yangi qo'shing</p>
              </div>
            </div>

            <div class="space-y-4">
              <div>
                <label class="label">Telefon raqami</label>
                <div class="flex gap-2">
                  <input v-model="form.client_phone" @blur="searchClient"
                    class="input flex-1" placeholder="+998 90 123 45 67" />
                  <button type="button" @click="searchClient" class="btn-secondary flex-shrink-0">
                    <AppIcon name="search" :size="17" />
                  </button>
                </div>
              </div>

              <!-- Found client -->
              <div v-if="clientFound"
                class="flex items-center gap-3 p-3 rounded-xl text-[13px]"
                style="background:#ECFDF5; border:1px solid #A7F3D0;">
                <div class="w-9 h-9 rounded-full bg-emerald-100 flex items-center justify-center font-bold text-emerald-600 text-[14px] flex-shrink-0">
                  {{ clientFound.name.charAt(0).toUpperCase() }}
                </div>
                <div class="flex-1 min-w-0">
                  <p class="font-semibold text-emerald-800 truncate">{{ clientFound.name }}</p>
                  <p class="text-emerald-600 text-[11px]">Mijoz topildi</p>
                </div>
                <button type="button" @click="clientFound = null"
                  class="text-emerald-400 hover:text-emerald-600 transition-colors flex-shrink-0">
                  <AppIcon name="close" :size="16" />
                </button>
              </div>

              <template v-if="!clientFound">
                <div>
                  <label class="label">Ism familiya *</label>
                  <input v-model="form.client_name" class="input" required placeholder="Mijoz ismi" />
                </div>
                <div>
                  <label class="label">Manzil</label>
                  <input v-model="form.client_address" class="input" placeholder="Yetkazib berish manzili" />
                </div>
              </template>
            </div>
          </div>

          <!-- Deadline card -->
          <div class="card p-5">
            <div class="flex items-center gap-2 mb-4 pb-4 border-b border-[#E8ECF4]">
              <div class="icon-box w-9 h-9 icon-box-amber">
                <AppIcon name="calendar_month" :size="18" />
              </div>
              <div>
                <h3 class="font-semibold text-ink text-[15px]">Yetkazib berish</h3>
                <p class="text-ink-4 text-[11px]">Muddat va qo'shimcha izoh</p>
              </div>
            </div>
            <div class="space-y-4">
              <div>
                <label class="label">Yetkazib berish muddati</label>
                <div class="relative">
                  <AppIcon name="calendar_month" :size="17" class="absolute left-3 top-1/2 -translate-y-1/2 text-ink-4 pointer-events-none" />
                  <input v-model="form.deadline" class="input pl-9" type="date" :min="today" />
                </div>
              </div>
              <div>
                <label class="label">Izoh</label>
                <textarea v-model="form.notes" class="input" rows="1" placeholder="Qo'shimcha izoh..." />
              </div>
            </div>
          </div>
        </div>

        <!-- RIGHT: Mebel -->
        <div class="xl:col-span-3">
          <div class="card p-5">
            <div class="flex items-center gap-2 mb-5 pb-4 border-b border-[#E8ECF4]">
              <div class="icon-box w-9 h-9 icon-box-blue">
                <AppIcon name="chair" :size="18" />
              </div>
              <div>
                <h3 class="font-semibold text-ink text-[15px]">Mebel parametrlari</h3>
                <p class="text-ink-4 text-[11px]">Tur, o'lcham va material ma'lumotlari</p>
              </div>
            </div>

            <div class="space-y-5">
              <!-- Furniture type -->
              <div>
                <label class="label">Mebel turi *</label>
                <div class="grid grid-cols-4 gap-2">
                  <button
                    v-for="t in FURNITURE_TYPES" :key="t" type="button"
                    @click="form.furniture_type = t"
                    class="py-2 px-3 rounded-lg border text-[13px] font-medium transition-all"
                    :class="form.furniture_type === t
                      ? 'bg-brand-500 border-brand-500 text-white shadow-sm'
                      : 'bg-white border-[#E8ECF4] text-ink-3 hover:border-brand-300 hover:text-brand-500'"
                  >{{ t }}</button>
                </div>
                <input v-if="form.furniture_type === 'Boshqa'"
                  v-model="form.furniture_type_custom"
                  class="input mt-2" placeholder="Mebel turini kiriting..." />
              </div>

              <!-- Dimensions -->
              <div>
                <label class="label">O'lchamlar (mm) *</label>
                <div class="grid grid-cols-3 gap-3">
                  <div>
                    <div class="relative">
                      <input v-model.number="form.height_mm" class="input pr-10 text-center" type="number" min="1" required placeholder="0" />
                      <span class="absolute right-3 top-1/2 -translate-y-1/2 text-ink-4 text-[11px] font-semibold pointer-events-none">mm</span>
                    </div>
                    <p class="text-center text-[11px] text-ink-4 mt-1">Bo'yi</p>
                  </div>
                  <div>
                    <div class="relative">
                      <input v-model.number="form.width_mm" class="input pr-10 text-center" type="number" min="1" required placeholder="0" />
                      <span class="absolute right-3 top-1/2 -translate-y-1/2 text-ink-4 text-[11px] font-semibold pointer-events-none">mm</span>
                    </div>
                    <p class="text-center text-[11px] text-ink-4 mt-1">Eni</p>
                  </div>
                  <div>
                    <div class="relative">
                      <input v-model.number="form.depth_mm" class="input pr-10 text-center" type="number" min="1" required placeholder="0" />
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
                  <button
                    v-for="m in MATERIALS" :key="m" type="button"
                    @click="form.material = m"
                    class="py-1.5 px-2 rounded-lg border text-[12px] font-medium transition-all"
                    :class="form.material === m
                      ? 'bg-brand-500 border-brand-500 text-white'
                      : 'bg-white border-[#E8ECF4] text-ink-3 hover:border-brand-300 hover:text-brand-500'"
                  >{{ m }}</button>
                </div>
                <input v-if="form.material === 'Boshqa'"
                  v-model="form.material_custom"
                  class="input mt-2" placeholder="Material nomini kiriting..." />
              </div>

              <!-- Holes & Cuts -->
              <div class="grid grid-cols-1 gap-4">
                <div>
                  <label class="label">Teshish joylari</label>
                  <textarea v-model="form.holes" class="input" rows="1" placeholder="Teshish joylari tavsifi..." />
                </div>
                <div>
                  <label class="label">Kesish tafsilotlari</label>
                  <textarea v-model="form.cuts" class="input" rows="1" placeholder="Qo'shimcha kesish o'lchamlari..." />
                </div>
              </div>

              <!-- Color -->
              <div>
                <label class="label">Rang</label>
                <input v-model="form.color" class="input" placeholder="Oq, Qo'ng'ir..." />
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Error -->
      <div v-if="error"
        class="p-4 rounded-xl flex items-center gap-3 text-[13px]"
        style="background:#FEF2F2;border:1px solid #FECACA;color:#991B1B;">
        <AppIcon name="error" :size="20" class="flex-shrink-0 text-red-400" />
        {{ error }}
      </div>

      <!-- Actions -->
      <div class="flex gap-3 justify-end pb-2">
        <RouterLink to="/orders" class="btn-secondary">
          <AppIcon name="close" :size="17" />
          Bekor qilish
        </RouterLink>
        <button @click="handleSubmit" class="btn-primary" :disabled="ordersStore.loading">
          <AppIcon v-if="ordersStore.loading" name="progress_activity" :size="17" class="animate-spin" />
          <AppIcon v-else name="save" :size="17" />
          {{ ordersStore.loading ? 'Saqlanmoqda...' : 'Buyurtmani saqlash' }}
        </button>
      </div>
    </template>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { useOrdersStore } from '@/stores/orders'
import { clientsApi } from '@/api'
import AppIcon from '@/components/AppIcon.vue'

const ordersStore    = useOrdersStore()
const today          = new Date().toISOString().split('T')[0]
const createdOrderNo = ref(null)
const createdOrderId = ref(null)
const clientFound    = ref(null)
const error          = ref(null)

const FURNITURE_TYPES = ['Shkaf', 'Stol', 'Stul', 'Divan', 'Krovat', 'Javon', 'Tokcha', 'Boshqa']
const MATERIALS       = ['DSP', 'MDF', 'Faner', 'Metall', 'Shisha', 'Kompozit', 'Boshqa']

const form = reactive({
  client_phone:'', client_name:'', client_address:'',
  furniture_type:'', furniture_type_custom:'',
  height_mm:null, width_mm:null, depth_mm:null,
  material:'', material_custom:'',
  color:'', holes:'', cuts:'', notes:'', deadline:'',
})

async function searchClient() {
  if (!form.client_phone.trim()) return
  clientFound.value = null
  try {
    const res   = await clientsApi.list({ search: form.client_phone.trim() })
    const match = res.data.find(c => c.phone === form.client_phone.trim())
    if (match) clientFound.value = match
  } catch { /* no match */ }
}

async function handleSubmit() {
  error.value = null
  if (!form.height_mm || !form.width_mm || !form.depth_mm) {
    error.value = "O'lchamlarni (bo'yi, eni, chuqurligi) kiriting"; return
  }
  if (!form.furniture_type) { error.value = "Mebel turini tanlang"; return }
  if (!form.material) { error.value = "Materialni tanlang"; return }
  try {
    let clientId = clientFound.value?.id
    if (!clientId) {
      if (!form.client_name.trim()) { error.value = 'Mijoz topilmadi. Ism kiritish majburiy.'; return }
      const res = await clientsApi.create({ name: form.client_name.trim(), phone: form.client_phone.trim(), address: form.client_address || null })
      clientId = res.data.id
    }
    const order = await ordersStore.createOrder({
      client_id: clientId,
      deadline:  form.deadline || null,
      detail: {
        furniture_type: form.furniture_type === 'Boshqa' ? (form.furniture_type_custom.trim() || 'Boshqa') : form.furniture_type,
        height_mm: form.height_mm, width_mm: form.width_mm, depth_mm: form.depth_mm,
        material: form.material === 'Boshqa' ? (form.material_custom.trim() || 'Boshqa') : form.material,
        color: form.color || null,
        holes: form.holes || null, cuts: form.cuts || null, notes: form.notes || null,
      },
    })
    createdOrderNo.value = order.order_no
    createdOrderId.value = order.id
  } catch (e) {
    error.value = e.response?.data?.detail || 'Xatolik yuz berdi'
  }
}

function resetForm() {
  Object.keys(form).forEach(k => (form[k] = k.endsWith('_mm') ? null : ''))
  clientFound.value = null; createdOrderNo.value = null; createdOrderId.value = null
}
</script>
