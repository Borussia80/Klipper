<template>
  <div class="empty-state" :class="`is-${size}`">
    <slot>{{ message }}</slot>
    <div v-if="$slots.actions" class="empty-state-actions">
      <slot name="actions" />
    </div>
  </div>
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{
    /** Texto do estado vazio. Use o slot padrão quando precisar de marcação. */
    message?: string
    /**
     * sm — bloco aninhado dentro de uma seção que já tem conteúdo acima.
     * md — estado vazio de uma seção da página.
     * lg — a página inteira está vazia.
     */
    size?: 'sm' | 'md' | 'lg'
  }>(),
  { message: '', size: 'md' },
)
</script>

<style scoped>
.empty-state {
  text-align: center;
  color: var(--t3);
  font-size: 13px;
}

.empty-state.is-sm {
  padding: 24px 0;
  font-size: 12px;
}

.empty-state.is-md {
  padding: 40px 0;
}

.empty-state.is-lg {
  padding: 48px 0;
}

/* Centraliza uma ação ou várias com o mesmo espaçamento — antes cada página
   resolvia isso do seu jeito, com <br> + margin-top ou um flex próprio. */
.empty-state-actions {
  margin-top: 12px;
  display: flex;
  justify-content: center;
  gap: 8px;
}
</style>
