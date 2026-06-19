<template>
  <div class="space-y-3">
    <div v-for="n in rows" :key="n"
      class="rounded-lg skeleton"
      :style="{ height: rowHeight }"
    />
  </div>
</template>

<script setup>
defineProps({
  rows: { type: Number, default: 5 },
  rowHeight: { type: String, default: '48px' },
})
</script>
