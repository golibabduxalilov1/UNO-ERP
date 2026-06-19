<template>
  <div class="min-h-screen flex">

    <!-- LEFT: Image panel -->
    <div class="hidden lg:flex flex-col w-[480px] flex-shrink-0 relative overflow-hidden">

      <!-- Background image -->
      <div class="absolute inset-0 bg-cover bg-center bg-no-repeat"
        style="background-image: url('/src/assets/images.jpg')" />

      <!-- Dark overlay -->
      <div class="absolute inset-0 bg-gradient-to-t from-black/75 via-black/30 to-black/20" />

      <!-- Content -->
      <div class="relative z-10 flex flex-col h-full p-10">
        <!-- Logo -->
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-2xl overflow-hidden border border-white/30">
            <img src="@/assets/logo.jpg" alt="Logo" class="w-full h-full object-cover" />
          </div>
          <div>
            <p class="font-display font-bold text-white text-[17px]">Mebel Sex</p>
          </div>
        </div>

        <div class="flex-1" />

        <!-- Bottom -->
        <div>
          <div class="inline-flex items-center gap-2 px-3 py-1.5 rounded-full mb-5 bg-white/10 backdrop-blur-sm border border-white/20">
            <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
            <span class="text-white/80 text-xs font-medium">Tizim ishlayapti</span>
          </div>
          <h2 class="font-display font-bold text-white text-[32px] leading-tight mb-3">
            Mebel ishlab<br/>chiqarishni<br/>boshqaring
          </h2>
          <p class="text-white/55 text-[14px] leading-relaxed mb-8">
            Buyurtmalar, ishchilar va yetkazib berish jarayonini yagona platformada kuzating.
          </p>

        </div>
      </div>
    </div>

    <!-- RIGHT: Login form -->
    <div class="flex-1 flex items-center justify-center bg-[#F5F7FB] p-6 sm:p-12">
      <div class="w-full max-w-[460px]">

        <!-- Mobile logo -->
        <div class="lg:hidden flex items-center gap-3 mb-10">
          <div class="w-10 h-10 rounded-xl overflow-hidden border border-[#E8ECF4]">
            <img src="@/assets/logo.jpg" alt="Logo" class="w-full h-full object-cover" />
          </div>
          <div>
            <p class="font-display font-bold text-ink text-[17px]">Mebel Sex</p>
            <p class="text-ink-4 text-xs">Admin Panel</p>
          </div>
        </div>

        <!-- Heading -->
        <div class="mb-8">
          <h1 class="font-display font-bold text-ink text-[32px] leading-tight">Xush kelibsiz 👋</h1>
          <p class="text-ink-3 mt-2 text-[15px]">Tizimga kirish uchun ma'lumotlaringizni kiriting</p>
        </div>

        <!-- Form -->
        <form @submit.prevent="handleLogin" class="space-y-5">

          <!-- Login -->
          <div>
            <label class="label text-[13px] mb-1.5 block">Login</label>
            <div class="relative">
              <div class="absolute left-4 top-1/2 -translate-y-1/2 pointer-events-none text-ink-4">
                <AppIcon name="person" :size="18" />
              </div>
              <input
                id="login"
                v-model="form.login"
                type="text"
                class="input pl-11 h-12 text-[14px]"
                placeholder="Loginni kiriting"
                required autofocus
              />
            </div>
          </div>

          <!-- Password -->
          <div>
            <label class="label text-[13px] mb-1.5 block">Parol</label>
            <div class="relative">
              <div class="absolute left-4 top-1/2 -translate-y-1/2 pointer-events-none text-ink-4">
                <AppIcon name="lock" :size="18" />
              </div>
              <input
                id="password"
                v-model="form.password"
                :type="showPass ? 'text' : 'password'"
                class="input pl-11 pr-12 h-12 text-[14px]"
                placeholder="Parolni kiriting"
                required
              />
              <button type="button" @click="showPass = !showPass"
                class="absolute right-4 top-1/2 -translate-y-1/2 text-ink-4 hover:text-ink-2 transition-colors">
                <AppIcon :name="showPass ? 'visibility_off' : 'visibility'" :size="18" />
              </button>
            </div>
          </div>

          <!-- Error -->
          <div v-if="authStore.error"
            class="flex items-start gap-3 p-4 rounded-xl text-[13px]"
            style="background:#FEF2F2; border:1px solid #FECACA; color:#991B1B;">
            <AppIcon name="error" :size="18" class="flex-shrink-0 text-red-500 mt-0.5" />
            {{ authStore.error }}
          </div>

          <!-- Submit -->
          <button
            type="submit"
            class="btn-primary w-full h-12 text-[15px] font-semibold mt-2"
            :disabled="authStore.loading"
          >
            <AppIcon v-if="authStore.loading" name="progress_activity" :size="18" class="animate-spin" />
            <AppIcon v-else name="login" :size="18" />
            {{ authStore.loading ? 'Kirilmoqda...' : 'Tizimga kirish' }}
          </button>
        </form>

        <!-- Footer -->
        <p class="text-center text-ink-5 text-[12px] mt-10">
          © {{ new Date().getFullYear() }} Mebel Sex. Barcha huquqlar himoyalangan.
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import AppIcon from '@/components/AppIcon.vue'

const authStore = useAuthStore()
const form      = reactive({ login: '', password: '' })
const showPass  = ref(false)
const imgError  = ref(false)


async function handleLogin() {
  await authStore.login(form)
}
</script>
