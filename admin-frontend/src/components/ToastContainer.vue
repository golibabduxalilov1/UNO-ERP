<template>
  <Teleport to="body">
    <div class="fixed bottom-5 right-5 z-[9999] flex flex-col gap-2.5 pointer-events-none" style="max-width:360px;">
      <TransitionGroup name="toast">
        <div
          v-for="t in toasts"
          :key="t.id"
          class="flex items-start gap-3 px-4 py-3 rounded-xl shadow-lg pointer-events-auto cursor-pointer select-none"
          :style="styleFor(t.type)"
          @click="remove(t.id)"
        >
          <span class="flex-shrink-0 mt-0.5 text-[18px] leading-none">{{ iconFor(t.type) }}</span>
          <span class="text-[13px] font-medium leading-snug flex-1">{{ t.message }}</span>
          <span class="text-[16px] leading-none opacity-50 hover:opacity-80 flex-shrink-0">✕</span>
        </div>
      </TransitionGroup>
    </div>
  </Teleport>
</template>

<script setup>
import { useToast } from '@/composables/useToast'

const { toasts, remove } = useToast()

function iconFor(type) {
  return { success: '✅', error: '❌', info: 'ℹ️' }[type] ?? 'ℹ️'
}

function styleFor(type) {
  const styles = {
    success: 'background:#F0FDF4;border:1px solid #BBF7D0;color:#166534;',
    error:   'background:#FEF2F2;border:1px solid #FECACA;color:#991B1B;',
    info:    'background:#EFF6FF;border:1px solid #BFDBFE;color:#1E40AF;',
  }
  return styles[type] ?? styles.info
}
</script>

<style scoped>
.toast-enter-active { transition: all 0.25s ease; }
.toast-leave-active { transition: all 0.2s ease; }
.toast-enter-from   { opacity: 0; transform: translateY(16px) scale(0.97); }
.toast-leave-to     { opacity: 0; transform: translateX(100%); }
</style>
