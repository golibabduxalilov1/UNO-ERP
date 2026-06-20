<template>
  <div class="space-y-5 animate-fade-in">
    <!-- Header -->
    <div class="page-header">
      <div>
        <h1 class="font-display font-bold text-ink text-[22px]">Ishchilar</h1>
        <p class="text-ink-3 text-[13px] mt-0.5">Tizim foydalanuvchilari boshqaruvi</p>
      </div>
      <button @click="openModal()" class="btn-primary">
        <AppIcon name="person_add" :size="18" />
        Ishchi qo'shish
      </button>
    </div>

    <!-- Filter -->
    <div class="card p-4 flex items-end gap-3 flex-wrap">
      <div class="min-w-[200px]">
        <label class="label">Rol bo'yicha filter</label>
        <div class="relative">
          <select v-model="filterRole" @change="fetchData" class="input pr-8">
            <option value="">Barcha rollar</option>
            <option v-for="r in ROLES" :key="r.value" :value="r.value">{{ r.label }}</option>
          </select>
          <AppIcon name="expand_more" :size="17" class="absolute right-2.5 top-1/2 -translate-y-1/2 text-ink-4 pointer-events-none" />
        </div>
      </div>
    </div>

    <!-- Table -->
    <div class="card overflow-hidden">
      <div v-if="usersStore.loading" class="p-10 flex flex-col items-center gap-3">
        <div class="w-10 h-10 rounded-full border-[3px] border-brand-100 border-t-brand-500 animate-spin" />
        <p class="text-ink-4 text-[13px]">Yuklanmoqda...</p>
      </div>

      <div v-else-if="!usersStore.users.length" class="py-16 flex flex-col items-center gap-4">
        <div class="icon-box w-16 h-16 icon-box-slate rounded-2xl">
          <AppIcon name="badge" :size="32" />
        </div>
        <div class="text-center">
          <p class="font-display font-semibold text-ink text-[15px]">Ishchilar topilmadi</p>
          <p class="text-ink-3 text-[13px] mt-1">Hali birorta ishchi qo'shilmagan</p>
        </div>
        <button @click="openModal()" class="btn-primary">
          <AppIcon name="person_add" :size="16" />
          Birinchi ishchini qo'shing
        </button>
      </div>

      <div v-else class="overflow-x-auto">
        <table class="tbl" style="min-width:600px;">
          <thead>
            <tr>
              <th class="tbl-th">Ishchi</th>
              <th class="tbl-th">Rol</th>
              <th class="tbl-th">Telegram ID</th>
              <th class="tbl-th">Telefon</th>
              <th class="tbl-th">Holat</th>
              <th class="tbl-th text-right">Amallar</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="u in usersStore.users" :key="u.id" class="tbl-row group">
              <td class="tbl-td">
                <div class="flex items-center gap-2.5">
                  <div class="w-8 h-8 rounded-full flex items-center justify-center font-bold text-[12px] text-white flex-shrink-0"
                    :style="{ background: getRoleColor(u.role) }">
                    {{ u.full_name?.charAt(0).toUpperCase() || '?' }}
                  </div>
                  <span class="font-semibold text-ink text-[13px]">{{ u.full_name }}</span>
                </div>
              </td>
              <td class="tbl-td">
                <span class="badge" :style="getRoleBadgeStyle(u.role)">
                  {{ ROLE_LABELS[u.role] || u.role }}
                </span>
              </td>
              <td class="tbl-td font-mono text-ink-4 text-[12px] tabular-nums">{{ u.telegram_id || '—' }}</td>
              <td class="tbl-td text-ink-3 text-[13px]">{{ u.phone || '—' }}</td>
              <td class="tbl-td">
                <span class="badge"
                  :style="u.is_active
                    ? 'background:#ECFDF5;border:1px solid #A7F3D0;color:#065F46;'
                    : 'background:#FEF2F2;border:1px solid #FECACA;color:#991B1B;'">
                  <span class="w-1.5 h-1.5 rounded-full"
                    :class="u.is_active ? 'bg-emerald-500' : 'bg-red-400'" />
                  {{ u.is_active ? 'Faol' : 'Nofaol' }}
                </span>
              </td>
              <td class="tbl-td text-right">
                <div class="flex items-center justify-end gap-1.5">
                  <button v-if="u.role !== 'admin' || isFirstAdmin"
                    @click="openModal(u)" class="btn-icon btn-icon--warning" title="Tahrirlash">
                    <AppIcon name="edit" :size="17" />
                  </button>
                  <button v-if="u.role !== 'admin' || isFirstAdmin"
                    @click="toggleActive(u)" class="btn-icon"
                    :class="u.is_active ? 'hover:border-red-200 hover:text-red-500 hover:bg-red-50' : 'hover:border-emerald-200 hover:text-emerald-600 hover:bg-emerald-50'"
                    :title="u.is_active ? 'Nofaol qilish' : 'Faollashtirish'">
                    <AppIcon :name="u.is_active ? 'block' : 'check_circle'" :size="17" />
                  </button>
                  <button v-if="u.role !== 'admin' || isFirstAdmin"
                    @click="confirmDeleteUser(u)"
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
        <div v-if="deleteUserTarget"
          class="fixed inset-0 z-50 flex items-center justify-center p-4 sidebar-backdrop"
          @click.self="deleteUserTarget = null">
          <div class="card p-6 w-full max-w-sm">
            <div class="flex items-center gap-3 mb-4">
              <div class="icon-box w-10 h-10 icon-box-red">
                <AppIcon name="person_remove" :size="20" />
              </div>
              <h3 class="font-display font-bold text-ink text-[16px]">Ishchini o'chirish</h3>
            </div>
            <p class="text-ink-3 text-[13px] mb-5">
              <strong class="text-ink">{{ deleteUserTarget?.full_name }}</strong> ishchisini tizimdan o'chirishni tasdiqlaysizmi?
            </p>
            <div v-if="deleteUserError" class="mb-4 p-3 rounded-lg text-[12px]"
              style="background:#FEF2F2;border:1px solid #FECACA;color:#991B1B;">{{ deleteUserError }}</div>
            <div class="flex gap-2.5 justify-end">
              <button class="btn-secondary" @click="deleteUserTarget = null; deleteUserError = ''">Bekor</button>
              <button class="btn-danger" @click="doDeleteUser" :disabled="deletingUser">
                <AppIcon v-if="deletingUser" name="progress_activity" :size="16" class="animate-spin" />
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
                  <AppIcon name="manage_accounts" :size="19" />
                </div>
                <h3 class="font-display font-bold text-ink text-[16px]">
                  {{ editingUser ? 'Ishchini tahrirlash' : 'Yangi ishchi' }}
                </h3>
              </div>
              <button @click="showModal = false" class="btn-icon">
                <AppIcon name="close" :size="18" />
              </button>
            </div>

            <form @submit.prevent="saveUser" class="space-y-4">
              <div>
                <label class="label">To'liq ismi *</label>
                <input v-model="modalForm.full_name" class="input" placeholder="Ism Familiya" required />
              </div>
              <div>
                <label class="label">Telegram ID *</label>
                <input v-model.number="modalForm.telegram_id" class="input" type="number" placeholder="123456789" required />
                <p class="text-ink-4 text-[11px] mt-1">Ishchi /start bosganda ko'rinadigan raqam</p>
              </div>
              <div>
                <label class="label">Rol *</label>
                <div class="relative">
                  <select v-model="modalForm.role" class="input pr-8" required
                    :disabled="editingUser && editingUser.id === firstAdminId">
                    <option value="">Tanlang</option>
                    <option v-for="r in ROLES" :key="r.value" :value="r.value">{{ r.label }}</option>
                  </select>
                  <AppIcon name="expand_more" :size="17" class="absolute right-2.5 top-1/2 -translate-y-1/2 text-ink-4 pointer-events-none" />
                </div>
                <p v-if="editingUser && editingUser.id === firstAdminId"
                  class="text-[11px] mt-1" style="color:#D97706;">
                  Birinchi administrator roli o'zgartirib bo'lmaydi
                </p>
              </div>
              <div class="grid grid-cols-2 gap-3">
                <div>
                  <label class="label">Telefon</label>
                  <input v-model="modalForm.phone" class="input" placeholder="+998..." />
                </div>
                <div>
                  <label class="label">Login</label>
                  <input v-model="modalForm.login" class="input" placeholder="ixtiyoriy" />
                </div>
              </div>
              <div>
                <label class="label">Parol {{ editingUser ? "(o'zgartirish uchun)" : '*' }}</label>
                <input v-model="modalForm.password" class="input" type="password"
                  placeholder="••••••••" :required="!editingUser" />
              </div>
              <div v-if="modalError"
                class="flex items-center gap-2 p-3 rounded-lg text-[13px]"
                style="background:#FEF2F2;border:1px solid #FECACA;color:#991B1B;">
                <AppIcon name="error" :size="17" class="flex-shrink-0 text-red-400" />
                {{ modalError }}
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
import { ref, reactive, computed, onMounted } from 'vue'
import { useUsersStore } from '@/stores/users'
import { useAuthStore } from '@/stores/auth'
import AppIcon from '@/components/AppIcon.vue'
import { useToast } from '@/composables/useToast'

const toast = useToast()

const usersStore  = useUsersStore()
const authStore   = useAuthStore()

const firstAdminId = computed(() => {
  const admins = usersStore.users.filter(u => u.role === 'admin')
  if (!admins.length) return null
  return Math.min(...admins.map(u => u.id))
})
const isFirstAdmin = computed(() => authStore.user?.id === firstAdminId.value)
const filterRole  = ref('')
const showModal   = ref(false)
const editingUser = ref(null)
const saving      = ref(false)
const modalError  = ref('')

const ROLES = [
  { value: 'admin',    label: 'Administrator' },
  { value: 'brigadir', label: 'Brigadir' },       { value: 'nachalnik', label: 'Nachalnik' },
  { value: 'operator', label: 'Stanok operatori'},{ value: 'cutter',    label: 'Kesuvchi' },
  { value: 'driller',  label: 'Teshuvchi' },      { value: 'driver',    label: 'Haydovchi' },
  { value: 'director', label: 'Direktor' },
]
const ROLE_LABELS = Object.fromEntries(ROLES.map(r => [r.value, r.label]))

const ROLE_COLORS = {
  admin: '#1F52E8', director: '#7C3AED',
  brigadir: '#D97706', nachalnik: '#059669', operator: '#366EF9',
  cutter: '#EA580C', driller: '#8B5CF6', driver: '#6B7280',
}
function getRoleColor(role) { return ROLE_COLORS[role] || '#9CA3AF' }

function getRoleBadgeStyle(role) {
  const map = {
    admin:    'background:#EFF4FF;border:1px solid #C4D8FD;color:#1234A8;',
    director: 'background:#F5F3FF;border:1px solid #DDD6FE;color:#5B21B6;',
    brigadir: 'background:#FFFBEB;border:1px solid #FDE68A;color:#92400E;',
    nachalnik:'background:#ECFDF5;border:1px solid #A7F3D0;color:#065F46;',
    operator: 'background:#EFF4FF;border:1px solid #C4D8FD;color:#1234A8;',
    cutter:   'background:#FFF7ED;border:1px solid #FED7AA;color:#9A3412;',
    driller:  'background:#F5F3FF;border:1px solid #DDD6FE;color:#5B21B6;',
    driver:   'background:#F3F4F6;border:1px solid #E5E7EB;color:#6B7280;',
  }
  return map[role] || 'background:#F3F4F6;border:1px solid #E5E7EB;color:#6B7280;'
}

const modalForm = reactive({ full_name:'', telegram_id:'', role:'', phone:'', login:'', password:'' })

function fetchData() {
  usersStore.fetchUsers(filterRole.value ? { role: filterRole.value } : {})
}

function openModal(user = null) {
  editingUser.value = user
  modalError.value = ''
  if (user) {
    Object.assign(modalForm, { full_name: user.full_name, telegram_id: user.telegram_id, role: user.role, phone: user.phone || '', login: user.login || '', password: '' })
  } else {
    Object.assign(modalForm, { full_name:'', telegram_id:'', role:'', phone:'', login:'', password:'' })
  }
  showModal.value = true
}

async function saveUser() {
  saving.value = true; modalError.value = ''
  try {
    const data = { full_name: modalForm.full_name, telegram_id: Number(modalForm.telegram_id), role: modalForm.role }
    if (modalForm.phone)    data.phone    = modalForm.phone
    if (modalForm.login)    data.login    = modalForm.login
    if (modalForm.password) data.password = modalForm.password
    editingUser.value
      ? await usersStore.updateUser(editingUser.value.id, data)
      : await usersStore.createUser(data)
    showModal.value = false
    toast.success(editingUser.value ? "Foydalanuvchi yangilandi" : "Foydalanuvchi yaratildi")
  } catch (e) {
    modalError.value = e.response?.data?.detail || 'Xatolik yuz berdi'
  } finally {
    saving.value = false
  }
}

async function toggleActive(user) {
  await usersStore.updateUser(user.id, { is_active: !user.is_active })
  toast.success(user.is_active ? "Foydalanuvchi o'chirildi" : "Foydalanuvchi faollashtirildi")
}

const deleteUserTarget = ref(null)
const deletingUser     = ref(false)
const deleteUserError  = ref('')

function confirmDeleteUser(user) { deleteUserTarget.value = user; deleteUserError.value = '' }
async function doDeleteUser() {
  deletingUser.value = true; deleteUserError.value = ''
  try {
    await usersStore.deleteUser(deleteUserTarget.value.id)
    deleteUserTarget.value = null
    toast.success("Foydalanuvchi o'chirildi")
  } catch (e) {
    deleteUserError.value = e.response?.data?.detail || 'Xatolik yuz berdi'
    toast.error(deleteUserError.value)
  } finally { deletingUser.value = false }
}

onMounted(fetchData)
</script>
