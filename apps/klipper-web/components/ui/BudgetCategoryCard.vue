<template>
  <div
    class="bc"
    :class="{
      'bc-w': status === 'warn',
      'bc-a': status === 'alert',
    }"
  >
    <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px">
      <div style="display:flex;align-items:center;gap:10px">
        <UiAppIcon :name="icon" :size="20" style="flex-shrink:0;color:var(--t2)" />
        <div>
          <div style="font-size:14px;font-weight:600;color:var(--t1)">{{ name }}</div>
          <div
            :style="{ fontSize: '11px', color: status === 'alert' ? 'var(--alert)' : 'var(--t3)' }"
          >
            <template v-if="status === 'alert'">
              Limite excedido em R$ {{ overshoot.toFixed(0).replace('.', ',') }}
            </template>
            <template v-else>{{ daysLeft }} dias restantes</template>
          </div>
        </div>
      </div>
      <span
        v-if="status === 'alert'"
        class="tag tag-a"
      >ESTOURADO</span>
      <span
        v-else-if="status === 'warn'"
        class="tag tag-w"
      >{{ pct }}%</span>
      <span
        v-else
        class="tag tag-b"
      >{{ pct }}%</span>
    </div>

    <div
      :style="{
        height: '10px',
        background: status === 'alert' ? 'var(--ald)' : 'var(--ly)',
        borderRadius: '5px',
        overflow: 'hidden',
        marginBottom: '8px',
      }"
    >
      <div
        :style="{
          width: `${Math.min(pct, 100)}%`,
          height: '100%',
          background: barColor,
          borderRadius: '5px',
        }"
      />
    </div>

    <div style="display:flex;justify-content:space-between;font-size:12px">
      <span :style="{ color: status === 'alert' ? 'var(--alert)' : 'var(--t2)' }">
        R$ {{ spent.toLocaleString('pt-BR', { minimumFractionDigits: 0 }) }} gastos
      </span>
      <span :style="{ color: status === 'alert' ? 'var(--alert)' : 'var(--t3)' }">
        <template v-if="status === 'alert'">
          R$ {{ overshoot.toFixed(0) }} acima do limite de R$ {{ limit.toLocaleString('pt-BR') }}
        </template>
        <template v-else>
          R$ {{ (limit - spent).toLocaleString('pt-BR', { minimumFractionDigits: 0 }) }} livres de R$ {{ limit.toLocaleString('pt-BR') }}
        </template>
      </span>
    </div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  icon: string
  name: string
  pct: number
  spent: number
  limit: number
  daysLeft: number
}>()

const status = computed<'ok' | 'warn' | 'alert'>(() => {
  if (props.pct > 100) return 'alert'
  if (props.pct >= 80) return 'warn'
  return 'ok'
})

const overshoot = computed(() => Math.max(0, props.spent - props.limit))

const barColor = computed(() => {
  if (status.value === 'alert') return 'var(--alert)'
  if (status.value === 'warn') return 'var(--warn)'
  return 'var(--blue)'
})
</script>
