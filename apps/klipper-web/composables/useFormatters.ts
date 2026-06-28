/**
 * useFormatters — BRL currency and percent helpers.
 * Keeping formatting in one place avoids locale drift across components.
 */

const monthShort = new Intl.DateTimeFormat('pt-BR', { month: 'short' })
const monthLong = new Intl.DateTimeFormat('pt-BR', { month: 'long' })

const brl = new Intl.NumberFormat('pt-BR', {
  style: 'currency',
  currency: 'BRL',
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
})

const brlCompact = new Intl.NumberFormat('pt-BR', {
  style: 'currency',
  currency: 'BRL',
  notation: 'compact',
  minimumFractionDigits: 0,
  maximumFractionDigits: 1,
})

const pct = new Intl.NumberFormat('pt-BR', {
  style: 'percent',
  minimumFractionDigits: 1,
  maximumFractionDigits: 2,
  signDisplay: 'exceptZero',
})

export function useFormatters() {
  function formatBRL(value: number): string {
    return brl.format(value)
  }

  function formatBRLCompact(value: number): string {
    return brlCompact.format(value)
  }

  function formatPercent(value: number): string {
    // value is already a fraction (0.05 = 5%)
    return pct.format(value)
  }

  function formatPercentRaw(value: number): string {
    // value is raw percentage (5 = 5%)
    return pct.format(value / 100)
  }

  function deltaClass(value: number): string {
    if (value > 0) return 'val-positive'
    if (value < 0) return 'val-negative'
    return 'val-neutral'
  }

  function deltaSign(value: number): string {
    return value >= 0 ? '▲' : '▼'
  }

  function currentMonthLabel(): string {
    const now = new Date()
    const abbr = monthShort.format(now).replace(/\.$/, '')
    return `${abbr.charAt(0).toUpperCase() + abbr.slice(1)} ${now.getFullYear()}`
  }

  function fmtMonthFull(): string {
    const now = new Date()
    const name = monthLong.format(now)
    return `${name.charAt(0).toUpperCase() + name.slice(1)} ${now.getFullYear()}`
  }

  function daysLeftInMonth(): number {
    const now = new Date()
    const lastDay = new Date(now.getFullYear(), now.getMonth() + 1, 0).getDate()
    return lastDay - now.getDate()
  }

  return {
    formatBRL,
    formatBRLCompact,
    formatPercent,
    formatPercentRaw,
    deltaClass,
    deltaSign,
    currentMonthLabel,
    fmtMonthFull,
    daysLeftInMonth,
  }
}

export function isFutureDate(dateStr: string): boolean {
  const [y, m, d] = dateStr.split('-').map(Number)
  const today = new Date()
  return new Date(y, m - 1, d) > new Date(today.getFullYear(), today.getMonth(), today.getDate())
}
