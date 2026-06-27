<template>
  <div
    class="sk-line"
    :style="{ width, height, borderRadius: round ? '999px' : '4px' }"
    role="presentation"
    aria-hidden="true"
  />
</template>

<script setup lang="ts">
withDefaults(defineProps<{ width?: string; height?: string; round?: boolean }>(), {
  width: '100%',
  height: '12px',
  round: false,
})
</script>

<style scoped>
.sk-line {
  background: linear-gradient(90deg, var(--sf) 25%, var(--ly) 50%, var(--sf) 75%);
  background-size: 200% 100%;
  animation: shimmer 1.4s ease infinite;
}

@keyframes shimmer {
  0%   { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

@media (prefers-reduced-motion: reduce) {
  .sk-line {
    animation: none;
    background: var(--sf);
  }
}
</style>
