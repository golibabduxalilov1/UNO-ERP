<template>
  <div class="flex h-screen overflow-hidden bg-page">

    <!-- MOBILE BACKDROP -->
    <Transition name="backdrop">
      <div v-if="sidebarOpen"
        class="fixed inset-0 z-40 sidebar-backdrop md:hidden"
        @click="sidebarOpen = false" />
    </Transition>

    <!-- SIDEBAR -->
    <aside
      class="sidebar fixed inset-y-0 left-0 z-50 flex flex-col w-[248px] transition-transform duration-300 ease-in-out md:translate-x-0 md:relative md:z-auto"
      :class="sidebarOpen ? 'translate-x-0' : '-translate-x-full'"
    >
      <!-- Logo -->
      <div class="flex items-center gap-3 px-5 py-4 border-b border-[#E8ECF4]">
        <RouterLink to="/" class="flex items-center gap-3 flex-1 min-w-0 hover:opacity-80 transition-opacity">
          <div class="w-8 h-8 rounded-xl overflow-hidden flex-shrink-0 border border-[#E8ECF4]">
            <img src="@/assets/logo.jpg" alt="Logo" class="w-full h-full object-cover" />
          </div>
          <div class="flex-1 min-w-0">
            <p class="font-display font-bold text-ink text-[14px] leading-tight truncate">Mebel Sex</p>
            <p class="text-[10px] font-medium text-ink-4 mt-0.5">Admin Panel</p>
          </div>
        </RouterLink>
        <button class="md:hidden btn-icon border-0 bg-transparent w-7 h-7"
          @click="sidebarOpen = false">
          <AppIcon name="close" :size="18" />
        </button>
      </div>

      <!-- Navigation -->
      <nav class="flex-1 py-3 overflow-y-auto">
        <p class="px-5 pt-2 pb-1 text-[10px] font-bold uppercase tracking-[1.8px] text-ink-5">Asosiy</p>

        <RouterLink
          v-for="item in mainNav" :key="item.path"
          :to="item.path"
          class="nav-item"
          :class="{ active: isActive(item.path) }"
          @click="sidebarOpen = false"
        >
          <AppIcon :name="item.icon" :size="18" class="nav-icon" />
          <span>{{ item.label }}</span>
          <span v-if="isActive(item.path)"
            class="ml-auto w-1.5 h-1.5 rounded-full bg-brand-500 flex-shrink-0" />
        </RouterLink>

        <hr class="sidebar-divider mt-3" />
        <p class="px-5 pt-1 pb-1 text-[10px] font-bold uppercase tracking-[1.8px] text-ink-5">Boshqaruv</p>

        <RouterLink
          v-for="item in adminNav" :key="item.path"
          :to="item.path"
          class="nav-item"
          :class="{ active: isActive(item.path) }"
          @click="sidebarOpen = false"
        >
          <AppIcon :name="item.icon" :size="18" class="nav-icon" />
          <span>{{ item.label }}</span>
          <span v-if="isActive(item.path)"
            class="ml-auto w-1.5 h-1.5 rounded-full bg-brand-500 flex-shrink-0" />
        </RouterLink>
      </nav>

      <!-- User -->
      <div class="border-t border-[#E8ECF4] p-3">
        <div class="flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-surface transition-colors group cursor-default">
          <div class="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 font-bold text-sm text-white bg-brand-500">
            {{ userInitial }}
          </div>
          <div class="flex-1 min-w-0">
            <p class="text-[13px] font-semibold text-ink truncate">{{ authStore.user?.full_name || 'Admin' }}</p>
            <p class="text-[11px] text-ink-4 capitalize">{{ authStore.user?.role || 'admin' }}</p>
          </div>
          <button @click.stop="handleLogout"
            class="opacity-0 group-hover:opacity-100 btn-icon border-0 bg-transparent w-7 h-7 hover:bg-red-50 hover:text-red-500 hover:border-red-100 transition-all"
            title="Chiqish">
            <AppIcon name="logout" :size="16" />
          </button>
        </div>
      </div>
    </aside>

    <!-- MAIN CONTENT -->
    <div class="flex-1 flex flex-col min-w-0 overflow-hidden">

      <!-- Top bar -->
      <header class="topbar flex items-center gap-3 px-4 md:px-6 h-14 flex-shrink-0">
        <button @click="sidebarOpen = true"
          class="md:hidden btn-icon flex-shrink-0">
          <AppIcon name="menu" :size="20" />
        </button>

        <div class="flex items-center gap-2 text-[13px]">
          <span class="text-ink-4 hidden sm:inline">Admin</span>
          <span class="text-ink-4 hidden sm:inline">/</span>
          <span class="font-semibold text-ink">{{ pageTitle }}</span>
        </div>

        <div class="ml-auto flex items-center gap-2">
          <div class="hidden sm:flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-[12px] font-mono text-ink-3 border border-[#E8ECF4] bg-[#FAFBFC]">
            <AppIcon name="schedule" :size="14" class="text-brand-500" />
            {{ currentTime }}
          </div>

          <button @click="handleLogout" class="btn-secondary py-1.5 px-3 text-[12px]">
            <AppIcon name="logout" :size="16" />
            <span class="hidden sm:inline">Chiqish</span>
          </button>
        </div>
      </header>

      <!-- Page content -->
      <main class="flex-1 overflow-y-auto">
        <div class="p-4 md:p-6">
          <RouterView v-slot="{ Component }">
            <Transition name="page" mode="out-in">
              <component :is="Component" :key="$route.path" />
            </Transition>
          </RouterView>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { RouterLink, RouterView, useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import AppIcon from '@/components/AppIcon.vue'

const authStore   = useAuthStore()
const route       = useRoute()
const router      = useRouter()
const sidebarOpen = ref(false)
const currentTime = ref('')

const mainNav = [
  { path: '/',        icon: 'dashboard',    label: 'Dashboard' },
  { path: '/orders',  icon: 'shopping_bag', label: 'Buyurtmalar' },
  { path: '/clients', icon: 'people',       label: 'Mijozlar' },
  { path: '/reports', icon: 'bar_chart',    label: 'Hisobotlar' },
]

const adminNav = computed(() => [
  ...(authStore.user?.role === 'admin'
    ? [{ path: '/users', icon: 'badge', label: 'Ishchilar' }]
    : []),
  { path: '/complaint', icon: 'troubleshoot', label: 'Shikoyatlar' },
])

const PAGE_TITLES = {
  '/': 'Dashboard', '/orders': 'Buyurtmalar', '/orders/new': 'Yangi buyurtma',
  '/clients': 'Mijozlar', '/reports': 'Hisobotlar',
  '/users': 'Ishchilar', '/complaint': 'Shikoyatlar',
}

const pageTitle = computed(() => {
  if (route.name === 'OrderDetail') return `Buyurtma #${route.params.id}`
  return PAGE_TITLES[route.path] || 'Admin Panel'
})

const userInitial = computed(() =>
  (authStore.user?.full_name || 'A').charAt(0).toUpperCase()
)

function isActive(path) {
  if (path === '/') return route.path === '/'
  return route.path.startsWith(path)
}

function handleLogout() {
  authStore.logout()
  router.push('/login')
}

let timer = null
function tick() {
  currentTime.value = new Date().toLocaleTimeString('uz-UZ', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
}

onMounted(() => { authStore.fetchMe?.(); tick(); timer = setInterval(tick, 1000) })
onUnmounted(() => clearInterval(timer))
</script>

<style scoped>
.backdrop-enter-active, .backdrop-leave-active { transition: opacity 0.25s ease; }
.backdrop-enter-from, .backdrop-leave-to { opacity: 0; }
</style>
