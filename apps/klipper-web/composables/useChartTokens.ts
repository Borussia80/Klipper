/**
 * Lê design tokens do CSS e os disponibiliza para React islands (charts).
 * React não tem acesso direto a CSS custom properties — esta composable
 * resolve os valores em mount-time e retorna um objeto plano.
 */
export function useChartTokens() {
  const tokens = ref({
    blue:        '#2B7DF4',
    blt:         '#5A9BFF',
    ok:          '#0DB878',
    warn:        '#E59010',
    alert:       '#E83535',
    pur:         '#7C5CF5',
    crypto:      '#F4C030',
    t2:          '#8AABCA',
    t3:          '#4D6E8A',
    t4:          '#284158',
    chartBg:     '#151D2A',
    chartBorder: '#1E2D3F',
    sf:          '#0C1B2C',
    ly:          '#122440',
  })

  onMounted(() => {
    const root = document.documentElement
    const get = (v: string) => getComputedStyle(root).getPropertyValue(v).trim()

    tokens.value = {
      blue:        get('--blue')         || tokens.value.blue,
      blt:         get('--blt')          || tokens.value.blt,
      ok:          get('--ok')           || tokens.value.ok,
      warn:        get('--warn')         || tokens.value.warn,
      alert:       get('--alert')        || tokens.value.alert,
      pur:         get('--pur')          || tokens.value.pur,
      crypto:      get('--crypto')       || tokens.value.crypto,
      t2:          get('--t2')           || tokens.value.t2,
      t3:          get('--t3')           || tokens.value.t3,
      t4:          get('--t4')           || tokens.value.t4,
      chartBg:     get('--chart-bg')     || tokens.value.chartBg,
      chartBorder: get('--chart-border') || tokens.value.chartBorder,
      sf:          get('--sf')           || tokens.value.sf,
      ly:          get('--ly')           || tokens.value.ly,
    }
  })

  return readonly(tokens)
}
