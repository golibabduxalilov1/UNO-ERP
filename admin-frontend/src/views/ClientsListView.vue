<template>
  <div class="space-y-5 animate-fade-in">
    <!-- Header -->
    <div class="page-header">
      <div>
        <h1 class="font-display font-bold text-ink text-[22px]">Mijozlar</h1>
        <p class="text-ink-3 text-[13px] mt-0.5">
          Jami <span class="font-semibold text-ink tabular-nums">{{ clients.length }}</span> ta mijoz
        </p>
      </div>
      <button @click="openModal()" class="btn-primary">
        <AppIcon name="person_add" :size="18" />
        Mijoz qo'shish
      </button>
    </div>

    <!-- Search -->
    <div class="card p-4">
      <div class="relative max-w-xs">
        <AppIcon name="search" :size="17" class="absolute left-3 top-1/2 -translate-y-1/2 text-ink-4 pointer-events-none" />
        <input v-model="search" @input="debouncedFetch" class="input pl-9" placeholder="Ism yoki telefon..." />
      </div>
    </div>

    <!-- Table -->
    <div class="card overflow-hidden">
      <div v-if="loading" class="p-10 flex flex-col items-center gap-3">
        <div class="w-10 h-10 rounded-full border-[3px] border-brand-100 border-t-brand-500 animate-spin" />
        <p class="text-ink-4 text-[13px]">Yuklanmoqda...</p>
      </div>

      <div v-else-if="clients.length === 0" class="py-16 flex flex-col items-center gap-4">
        <div class="icon-box w-16 h-16 icon-box-slate rounded-2xl">
          <AppIcon name="people_outline" :size="32" />
        </div>
        <div class="text-center">
          <p class="font-display font-semibold text-ink text-[15px]">Mijozlar topilmadi</p>
          <p class="text-ink-3 text-[13px] mt-1">Hali birorta mijoz qo'shilmagan</p>
        </div>
        <button @click="openModal()" class="btn-primary">
          <AppIcon name="person_add" :size="16" />
          Birinchi mijozni qo'shing
        </button>
      </div>

      <div v-else class="overflow-x-auto">
        <table class="tbl" style="min-width:520px;">
          <thead>
            <tr>
              <th class="tbl-th">Mijoz</th>
              <th class="tbl-th">Telefon</th>
              <th class="tbl-th">Manzil</th>
              <th class="tbl-th">Ro'yxatdan o'tgan</th>
              <th class="tbl-th text-right">Amallar</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="c in clients" :key="c.id" class="tbl-row group">
              <td class="tbl-td">
                <div class="flex items-center gap-2.5">
                  <div class="w-8 h-8 rounded-full bg-brand-100 text-brand-600 flex items-center justify-center font-bold text-[12px] flex-shrink-0">
                    {{ c.name?.charAt(0).toUpperCase() || '?' }}
                  </div>
                  <span class="font-semibold text-ink text-[13px]">{{ c.name }}</span>
                </div>
              </td>
              <td class="tbl-td font-mono text-brand-500 text-[13px]">{{ c.phone }}</td>
              <td class="tbl-td text-ink-3 text-[13px]">{{ c.address || '—' }}</td>
              <td class="tbl-td font-mono text-ink-4 text-[12px] tabular-nums">{{ formatDate(c.created_at) }}</td>
              <td class="tbl-td text-right">
                <div class="flex items-center justify-end gap-1">
                  <button @click="openModal(c)" class="btn-icon" title="Tahrirlash">
                    <AppIcon name="edit" :size="17" />
                  </button>
                  <button @click="confirmDelete(c)"
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
    </div>

    <!-- Delete confirm -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="deleteTarget !== null"
          class="fixed inset-0 z-50 flex items-center justify-center p-4 sidebar-backdrop"
          @click.self="deleteTarget = null">
          <div class="card p-6 w-full max-w-sm">
            <div class="flex items-center gap-3 mb-4">
              <div class="icon-box w-10 h-10 icon-box-red">
                <AppIcon name="person_remove" :size="20" />
              </div>
              <h3 class="font-display font-bold text-ink text-[16px]">Mijozni o'chirish</h3>
            </div>
            <p class="text-ink-3 text-[13px] mb-5">
              <strong class="text-ink">{{ deleteTarget?.name }}</strong> mijozini o'chirishni tasdiqlaysizmi?
              <br><span class="text-red-500 text-[12px]">Buyurtmalari bo'lsa o'chirib bo'lmaydi.</span>
            </p>
            <div v-if="deleteError" class="mb-4 p-3 rounded-lg text-[12px]"
              style="background:#FEF2F2;border:1px solid #FECACA;color:#991B1B;">{{ deleteError }}</div>
            <div class="flex gap-2.5 justify-end">
              <button class="btn-secondary" @click="deleteTarget = null; deleteError = ''">Bekor</button>
              <button class="btn-danger" @click="doDelete" :disabled="deleting">
                <AppIcon v-if="deleting" name="progress_activity" :size="16" class="animate-spin" />
                O'chirish
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- Modal -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="showModal"
          class="fixed inset-0 z-50 flex items-center justify-center p-4 sidebar-backdrop"
          @click.self="showModal = false">
          <div class="card p-6 w-full max-w-md">
            <div class="flex items-center justify-between mb-5">
              <div class="flex items-center gap-3">
                <div class="icon-box w-9 h-9 icon-box-blue">
                  <AppIcon name="person" :size="19" />
                </div>
                <h3 class="font-display font-bold text-ink text-[16px]">
                  {{ editing ? 'Mijozni tahrirlash' : 'Yangi mijoz' }}
                </h3>
              </div>
              <button @click="showModal = false" class="btn-icon">
                <AppIcon name="close" :size="18" />
              </button>
            </div>
            <form @submit.prevent="saveClient" class="space-y-4">
              <div>
                <label class="label">Ism *</label>
                <input v-model="form.name" class="input" placeholder="Ism Familiya" required />
              </div>
              <div>
                <label class="label">Telefon *</label>
                <div class="relative">
                  <AppIcon name="phone" :size="17" class="absolute left-3 top-1/2 -translate-y-1/2 text-ink-4 pointer-events-none" />
                  <input v-model="form.phone" class="input pl-9" required placeholder="+998 90 123 45 67" />
                </div>
              </div>
              <div>
                <label class="label">Manzil</label>
                <textarea v-model="form.address" class="input" rows="2" placeholder="Shahar, ko'cha..." />
              </div>
              <div v-if="formError"
                class="flex items-center gap-2 p-3 rounded-lg text-[13px]"
                style="background:#FEF2F2;border:1px solid #FECACA;color:#991B1B;">
                <AppIcon name="error" :size="17" class="flex-shrink-0 text-red-400" />
                {{ formError }}
              </div>
              <div class="flex justify-end gap-2.5 pt-2">
                <button type="button" class="btn-secondary" @click="showModal = false">Bekor</button>
                <button type="submit" class="btn-primary" :disabled="saving">
                  <AppIcon v-if="saving" name="progress_activity" :size="17" class="animate-spin" />
                  {{ saving ? 'Saqlanmoqda...' : 'Saqlash' }}
                </button>
              </div>
            </form>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { clientsApi } from '@/api'
import AppIcon from '@/components/AppIcon.vue'

const clients     = ref([])
const loading     = ref(false)
const search      = ref('')
const showModal   = ref(false)
const editing     = ref(null)
const saving      = ref(false)
const formError   = ref('')
const form        = reactive({ name:'', phone:'', address:'' })
const deleteTarget = ref(null)
const deleting    = ref(false)
const deleteError = ref('')

function confirmDelete(client) { deleteTarget.value = client; deleteError.value = '' }
async function doDelete() {
  deleting.value = true; deleteError.value = ''
  try {
    await clientsApi.delete(deleteTarget.value.id)
    deleteTarget.value = null
    fetchClients()
  } catch (e) {
    deleteError.value = e.response?.data?.detail || 'Xatolik yuz berdi'
  } finally { deleting.value = false }
}

async function fetchClients() {
  loading.value = true
  try {
    const res = await clientsApi.list(search.value ? { search: search.value } : {})
    clients.value = res.data
  } finally { loading.value = false }
}

let timer = null
function debouncedFetch() { clearTimeout(timer); timer = setTimeout(fetchClients, 400) }

function openModal(client = null) {
  editing.value = client
  formError.value = ''
  Object.assign(form, { name: client?.name||'', phone: client?.phone||'', address: client?.address||'' })
  showModal.value = true
}

async function saveClient() {
  saving.value = true; formError.value = ''
  try {
    editing.value
      ? await clientsApi.update(editing.value.id, { name: form.name, phone: form.phone, address: form.address||null })
      : await clientsApi.create({ name: form.name, phone: form.phone, address: form.address||null })
    showModal.value = false
    fetchClients()
  } catch (e) {
    formError.value = e.response?.data?.detail || 'Xatolik'
  } finally { saving.value = false }
}

function formatDate(dt) { return dt ? new Date(dt).toLocaleDateString('uz-UZ') : '—' }

onMounted(fetchClients)
</script>
