/**
 * useFormatters — BRL currency and percent helpers.
 * Keeping formatting in one place avoids locale drift across components.
 */

const monthShort = new Intl.DateTimeFormat('pt-BR', { month: 'short' })
const monthLong = new Intl.DateTimeFormat('pt-BR', { month: 'long' })
const dayMonth = new Intl.DateTimeFormat('pt-BR', { day: '2-digit', month: 'short' })
const fullDate = new Intl.DateTimeFormat('pt-BR', { day: '2-digit', month: '2-digit', year: 'numeric' })

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

  // O meio-dia não é enfeite: `new Date('2026-09-16')` é parseado como UTC e,
  // em BRT (UTC-3), volta para o dia 15. Toda data que chega da API é um
  // date-only ISO, então ancorar no meio-dia local é o que mantém o dia certo.
  function parseISODate(iso: string): Date {
    return new Date(`${iso}T12:00:00`)
  }

  // "16 de set." — listagens e cabeçalhos de agrupamento, onde o ano é
  // redundante porque o período já está delimitado na tela.
  function formatDayMonth(iso: string): string {
    return dayMonth.format(parseISODate(iso))
  }

  // "16/09/2026" — conferência linha a linha de documento importado, onde o
  // ano é parte do que o usuário está validando contra o extrato.
  function formatFullDate(iso: string): string {
    return fullDate.format(parseISODate(iso))
  }

  // O mês pode não ser o de hoje: o painel mostra o último mês com movimento.
  function currentMonthLabel(date: Date = new Date()): string {
    const abbr = monthShort.format(date).replace(/\.$/, '')
    return `${abbr.charAt(0).toUpperCase() + abbr.slice(1)} ${date.getFullYear()}`
  }

  function fmtMonthFull(date: Date = new Date()): string {
    const name = monthLong.format(date)
    return `${name.charAt(0).toUpperCase() + name.slice(1)} ${date.getFullYear()}`
  }

  function daysLeftInMonth(): number {
    const now = new Date()
    const lastDay = new Date(now.getFullYear(), now.getMonth() + 1, 0).getDate()
    return lastDay - now.getDate()
  }

  function formatDaysAgo(dateStr: string): string {
    const then = new Date(dateStr)
    const days = Math.floor((Date.now() - then.getTime()) / 86_400_000)
    if (days <= 0) return 'atualizado hoje'
    if (days === 1) return 'atualizado há 1 dia'
    if (days < 30) return `atualizado há ${days} dias`
    const months = Math.floor(days / 30)
    return months === 1 ? 'atualizado há 1 mês' : `atualizado há ${months} meses`
  }

  return {
    formatBRL,
    formatBRLCompact,
    formatPercent,
    formatPercentRaw,
    deltaClass,
    deltaSign,
    formatDayMonth,
    formatFullDate,
    currentMonthLabel,
    fmtMonthFull,
    daysLeftInMonth,
    formatDaysAgo,
  }
}

export function isFutureDate(dateStr: string): boolean {
  const [y, m, d] = dateStr.split('-').map(Number)
  const today = new Date()
  return new Date(y, m - 1, d) > new Date(today.getFullYear(), today.getMonth(), today.getDate())
}

// Aceita só dois formatos sem ambiguidade: BR com milhar+decimal (1.234,56)
// ou decimal simples com ponto (1234.56). Qualquer outra coisa — inclusive o
// formato americano com milhar (1,234.56), que colidia com o replace(',', '.')
// ingênuo e truncava o valor em silêncio — retorna null em vez de adivinhar.
export function parseBRLAmount(input: string): number | null {
  const s = input.trim().replace(/^R\$\s*/, '')
  if (!s) return null
  const brPattern = /^-?(\d{1,3}(\.\d{3})*|\d+)(,\d{1,2})?$/
  const plainPattern = /^-?\d+(\.\d{1,2})?$/
  if (brPattern.test(s)) return parseFloat(s.replace(/\./g, '').replace(',', '.'))
  if (plainPattern.test(s)) return parseFloat(s)
  return null
}

// Local calendar date (not UTC) — must stay in sync with isFutureDate's "today".
export function todayISO(): string {
  const now = new Date()
  const y = now.getFullYear()
  const m = String(now.getMonth() + 1).padStart(2, '0')
  const d = String(now.getDate()).padStart(2, '0')
  return `${y}-${m}-${d}`
}
