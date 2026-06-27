<template>
  <div
    :style="{
      fontSize: '10px',
      fontWeight: '600',
      letterSpacing: '.09em',
      textTransform: 'uppercase',
      color: 'var(--t4)',
      fontFamily: mono ? '\'JetBrains Mono\', monospace' : 'inherit',
      marginBottom: mb,
    }"
  >
    <slot>{{ label }}</slot>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  label?: string
  mono?: boolean
  mb?: string
}>()
</script>
