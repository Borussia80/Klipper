/**
 * Lê design tokens do CSS e os disponibiliza para React islands (charts).
 * React não tem acesso direto a CSS custom properties — esta composable
 * resolve os valores em mount-time e retorna um objeto plano.
 */
export function useChartTokens() {
  const tokens = ref({
    blue:        '#5B9BD5',
    blt:         '#7FB3E3',
    ok:          '#43C59E',
    warn:        '#E6B44C',
    alert:       '#E8735A',
    crypto:      '#F4C030',
    t2:          '#AEB4B8',
    t3:          '#7D848A',
    t4:          '#565D63',
    chartBg:     '#1E2122',
    chartBorder: '#32373A',
    sf:          '#1E2122',
    ly:          '#282C2E',
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
