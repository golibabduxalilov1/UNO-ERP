<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="modelValue"
        class="fixed inset-0 z-50 flex items-center justify-center p-4 sidebar-backdrop"
        @click.self="$emit('update:modelValue', false)">
        <div class="card p-6 max-w-sm w-full">
          <div class="flex items-start gap-4 mb-5">
            <div :class="['icon-box w-11 h-11 flex-shrink-0 rounded-xl', dangerous ? 'icon-box-red' : 'icon-box-blue']">
              <AppIcon :name="dangerous ? 'warning' : 'info'" :size="22" />
            </div>
            <div>
              <h3 class="font-display font-bold text-ink text-[16px]">{{ title }}</h3>
              <p class="text-ink-3 text-[13px] mt-1 leading-relaxed">{{ message }}</p>
            </div>
          </div>
          <div class="flex justify-end gap-2.5">
            <button class="btn-secondary" @click="$emit('update:modelValue', false)">Bekor qilish</button>
            <button :class="dangerous ? 'btn-danger' : 'btn-primary'" @click="confirm">
              {{ confirmText }}
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import AppIcon from '@/components/AppIcon.vue'

defineProps({
  modelValue:  Boolean,
  title:       { type: String, default: 'Tasdiqlash' },
  message:     { type: String, default: 'Davom etishni xohlaysizmi?' },
  confirmText: { type: String, default: 'Tasdiqlash' },
  dangerous:   { type: Boolean, default: false },
})
const emit = defineEmits(['update:modelValue', 'confirm'])
function confirm() { emit('confirm'); emit('update:modelValue', false) }
</script>
