<template>
  <component :is="icon" :size="size" weight="regular" aria-hidden="true" />
</template>

<script setup lang="ts">
import {
  PhHouse, PhShoppingCart, PhCar, PhFirstAidKit, PhGameController,
  PhForkKnife, PhTShirt, PhLightning, PhGraduationCap, PhTrendUp,
  PhChartBar, PhArrowsLeftRight, PhMusicNotes, PhAirplane,
  PhHeart, PhPlusCircle, PhWallet, PhCreditCard,
  PhArrowCircleUpRight, PhArrowCircleDownLeft, PhReceipt,
  PhBuildings, PhTarget, PhCaretDown, PhBell, PhMagnifyingGlass,
  PhGear, PhUploadSimple, PhSquaresFour, PhPulse, PhChartPie,
  PhDownloadSimple, PhBrain, PhQuestion, PhArrowsClockwise,
  PhWarningCircle, PhCheckCircle, PhInfo, PhX,
  PhHandbag, PhCurrencyCircleDollar, PhPiggyBank, PhChartLine,
  PhArrowUUpRight, PhArrowUDownLeft, PhShoppingBag,
} from '@phosphor-icons/vue'

const ICONS: Record<string, Component> = {
  // Categorias financeiras
  home: PhHouse,
  moradia: PhHouse,
  shopping: PhShoppingCart,
  alimentacao: PhForkKnife,
  restaurant: PhForkKnife,
  restaurante: PhForkKnife,
  car: PhCar,
  transporte: PhCar,
  health: PhFirstAidKit,
  saude: PhFirstAidKit,
  gaming: PhGameController,
  lazer: PhGameController,
  clothing: PhTShirt,
  vestuario: PhTShirt,
  utilities: PhLightning,
  education: PhGraduationCap,
  educacao: PhGraduationCap,
  music: PhMusicNotes,
  travel: PhAirplane,
  viagem: PhAirplane,
  pet: PhHeart,

  // Finanças
  income: PhArrowCircleUpRight,
  renda: PhArrowCircleUpRight,
  expense: PhArrowCircleDownLeft,
  investment: PhChartLine,
  investimento: PhChartLine,
  transfer: PhArrowsLeftRight,
  transferencia: PhArrowsLeftRight,
  wallet: PhWallet,
  card: PhCreditCard,
  receipt: PhReceipt,
  bank: PhBuildings,
  money: PhCurrencyCircleDollar,
  savings: PhPiggyBank,
  budget: PhHandbag,

  // UI chrome
  target: PhTarget,
  plus: PhPlusCircle,
  chevron: PhCaretDown,
  bell: PhBell,
  search: PhMagnifyingGlass,
  settings: PhGear,
  upload: PhUploadSimple,
  dashboard: PhSquaresFour,
  chart: PhPulse,
  donut: PhChartPie,
  download: PhDownloadSimple,
  ai: PhBrain,
  help: PhQuestion,
  refresh: PhArrowsClockwise,
  alert: PhWarningCircle,
  success: PhCheckCircle,
  info: PhInfo,
  close: PhX,
  'trend-up': PhTrendUp,
  'chart-bar': PhChartBar,
  'arrow-up': PhArrowUUpRight,
  'arrow-down': PhArrowUDownLeft,
  bag: PhShoppingBag,
}

const props = withDefaults(
  defineProps<{ name: string; size?: number }>(),
  { size: 16 }
)

const icon = computed(() => ICONS[props.name] ?? PhInfo)
</script>
