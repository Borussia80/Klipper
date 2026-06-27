<template>
  <div :style="containerStyle" aria-hidden="true">
    <SvgBanco v-if="slug" :banco="slug" :tamanho="innerSize" />
    <span v-else :style="fallbackStyle">{{ initial }}</span>
  </div>
</template>

<script setup lang="ts">
import { SvgBanco, obterPreset, listarBancos } from '@edusites/bancos-brasil'

const SLUG_MAP: Record<string, string> = {
  nubank: 'nubank', neon: 'neon', inter: 'inter',
  itaú: 'itau', itau: 'itau',
  btg: 'btg',
  bradesco: 'bradesco', caixa: 'caixa', santander: 'santander',
  xp: 'xp', c6: 'c6',
  'banco do brasil': 'bancodobrasil', 'bb ': 'bancodobrasil',
  original: 'original', next: 'next',
  sicoob: 'sicoob', sicredi: 'sicredi',
  safra: 'safra', pan: 'pan', picpay: 'picpay',
  'mercado pago': 'mercadopago', pagbank: 'pagbank',
  stone: 'stone', wise: 'wise',
}

const props = withDefaults(
  defineProps<{ institution?: string | null; name?: string | null; size?: number }>(),
  { size: 36 }
)

const banks = listarBancos()

const slug = computed<string | null>(() => {
  const raw = (props.institution || props.name || '').toLowerCase().trim()
  if (banks.includes(raw)) return raw
  for (const [key, value] of Object.entries(SLUG_MAP)) {
    if (raw.includes(key)) return value
  }
  return null
})

const preset = computed(() => (slug.value ? obterPreset(slug.value) : null))

const innerSize = computed(() => Math.round(props.size * 0.72))

const containerStyle = computed(() => ({
  width: `${props.size}px`,
  height: `${props.size}px`,
  borderRadius: preset.value?.formato === 'redondo' ? '50%' : '9px',
  background: preset.value?.fundo ?? 'var(--blue)',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  flexShrink: '0',
  overflow: 'hidden',
}))

const initial = computed(() =>
  (props.institution || props.name || '?').charAt(0).toUpperCase()
)

const fallbackStyle = computed(() => ({
  fontSize: `${Math.round(props.size * 0.4)}px`,
  fontWeight: '700',
  color: '#fff',
  lineHeight: '1',
}))
</script>
