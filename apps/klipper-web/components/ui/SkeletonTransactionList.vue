<template>
  <div style="display:flex;flex-direction:column;gap:0">
    <!-- Date divider skeleton -->
    <div style="display:flex;align-items:center;gap:10px;padding:18px 0 8px">
      <UiSkeletonLine width="60px" height="10px" />
      <div style="flex:1;height:1px;background:var(--bd)" />
    </div>
    <!-- Transaction row skeletons -->
    <UiSkeletonCard
      v-for="n in count"
      :key="n"
      style="border:none;border-bottom:1px solid var(--bd);border-radius:0;padding:10px 8px"
    />
  </div>
</template>

<script setup lang="ts">
withDefaults(defineProps<{ count?: number }>(), { count: 4 })
</script>
