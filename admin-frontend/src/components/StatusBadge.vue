<template>
  <span class="badge" :style="style">
    <span class="w-1.5 h-1.5 rounded-full flex-shrink-0" :style="{ background: info.dot }" />
    {{ info.label }}
  </span>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({ status: { type: String, required: true } })

const MAP = {
  new:               { label: 'Yangi',             bg: '#EFF4FF', border: '#C4D8FD', color: '#1234A8', dot: '#366EF9' },
  cutting:           { label: 'Kesishda',           bg: '#FFFBEB', border: '#FDE68A', color: '#92400E', dot: '#F59E0B' },
  drilling:          { label: 'Teshishda',          bg: '#FFF7ED', border: '#FED7AA', color: '#9A3412', dot: '#F97316' },
  assembling:        { label: "Yig'ishda",          bg: '#FEFCE8', border: '#FEF08A', color: '#713F12', dot: '#EAB308' },
  pending_nachalnik: { label: 'Nachalnik tasdiqida', bg: '#F5F3FF', border: '#DDD6FE', color: '#5B21B6', dot: '#8B5CF6' },
  ready:             { label: 'Tayyor',             bg: '#ECFDF5', border: '#A7F3D0', color: '#065F46', dot: '#10B981' },
  delivered:         { label: 'Yetkazildi',         bg: '#EFF6FF', border: '#BFDBFE', color: '#1E40AF', dot: '#3B82F6' },
  cancelled:         { label: 'Bekor',              bg: '#FEF2F2', border: '#FECACA', color: '#991B1B', dot: '#EF4444' },
  confirmed:         { label: 'Tasdiqlangan',       bg: '#ECFDF5', border: '#A7F3D0', color: '#065F46', dot: '#10B981' },
  rejected:          { label: 'Rad etilgan',        bg: '#FEF2F2', border: '#FECACA', color: '#991B1B', dot: '#EF4444' },
  in_progress:       { label: 'Jarayonda',          bg: '#FFFBEB', border: '#FDE68A', color: '#92400E', dot: '#F59E0B' },
  pending_brigadir:  { label: 'Brigadir kutmoqda',  bg: '#EFF4FF', border: '#C4D8FD', color: '#1234A8', dot: '#366EF9' },
}

const info  = computed(() => MAP[props.status] || { label: props.status, bg: '#F3F4F6', border: '#E5E7EB', color: '#6B7280', dot: '#9CA3AF' })
const style = computed(() => `background:${info.value.bg};border:1px solid ${info.value.border};color:${info.value.color};`)
</script>
