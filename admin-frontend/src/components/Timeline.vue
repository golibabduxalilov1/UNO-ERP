<template>
  <div class="relative">
    <ul class="space-y-0">
      <li v-for="(item, idx) in items" :key="idx" class="relative flex gap-4 pb-6 last:pb-0">
        <!-- Connector line -->
        <div v-if="idx < items.length - 1"
          class="absolute left-4 top-8 bottom-0 w-px bg-[#E8ECF4]" />

        <!-- Dot -->
        <div class="flex-shrink-0 relative z-10">
          <div class="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0"
            :style="dotStyle(item.status)">
            <AppIcon :name="dotIcon(item.status)" :size="15" :stroke-width="2" class="text-white" />
          </div>
        </div>

        <!-- Content -->
        <div class="flex-1 min-w-0 pt-1">
          <div class="flex items-start justify-between gap-2">
            <div class="flex-1 min-w-0">
              <p class="font-semibold text-ink text-[13px]">{{ item.title }}</p>
              <p v-if="item.subtitle" class="text-ink-3 text-[12px] mt-0.5">{{ item.subtitle }}</p>
              <div v-if="item.reason"
                class="flex items-start gap-1.5 mt-2 p-2.5 rounded-lg text-[12px]"
                style="background:#FEF2F2;border:1px solid #FECACA;color:#991B1B;">
                <AppIcon name="error" :size="14" class="flex-shrink-0 text-red-400 mt-0.5" />
                <span>Sabab: {{ item.reason }}</span>
              </div>
            </div>
            <span class="text-ink-4 font-mono text-[11px] whitespace-nowrap flex-shrink-0 tabular-nums">{{ item.time }}</span>
          </div>
        </div>
      </li>
    </ul>
  </div>
</template>

<script setup>
import AppIcon from '@/components/AppIcon.vue'

defineProps({ items: { type: Array, default: () => [] } })

const DOT_BG = {
  confirmed:         '#10B981',
  rejected:          '#EF4444',
  in_progress:       '#F59E0B',
  pending_brigadir:  '#366EF9',
  pending_nachalnik: '#8B5CF6',
  delivered:         '#3B82F6',
}
const DOT_ICONS = {
  confirmed:         'check',
  rejected:          'close',
  in_progress:       'play_arrow',
  pending_brigadir:  'hourglass_empty',
  pending_nachalnik: 'hourglass_empty',
  delivered:         'local_shipping',
}

function dotStyle(status) { return `background:${DOT_BG[status] || '#366EF9'};` }
function dotIcon(status)  { return DOT_ICONS[status] || 'circle' }
</script>
