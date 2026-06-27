/**
 * useFormatters tests — pure formatting helpers, no Nuxt runtime needed.
 *
 * useFormatters() uses module-level Intl.NumberFormat instances, so we
 * call the exported function directly. No mocking required.
 */
import { describe, it, expect, vi, afterEach } from 'vitest'
import { useFormatters } from '../useFormatters'

describe('useFormatters', () => {
  const { formatBRL, formatBRLCompact, formatPercent, formatPercentRaw, deltaClass, deltaSign } =
    useFormatters()

  // ── formatBRL ─────────────────────────────────────────────────────────────

  describe('formatBRL', () => {
    it('formats a typical decimal value', () => {
      expect(formatBRL(1234.56)).toMatch(/1\.234,56/)
    })

    it('formats zero', () => {
      expect(formatBRL(0)).toMatch(/0,00/)
    })

    it('formats one million', () => {
      expect(formatBRL(1_000_000)).toMatch(/1\.000\.000,00/)
    })

    it('formats negative values', () => {
      const result = formatBRL(-500.5)
      // Both "−R$ 500,50" (with minus sign) and "R$ -500,50" are valid
      expect(result).toMatch(/500,50/)
      // Should contain the negative indicator
      expect(result).toMatch(/[-−]/)
    })

    it('includes BRL currency symbol', () => {
      expect(formatBRL(100)).toMatch(/R\$/)
    })

    it('always has two decimal places', () => {
      expect(formatBRL(5)).toMatch(/5,00/)
      expect(formatBRL(5.1)).toMatch(/5,10/)
    })
  })

  // ── formatBRLCompact ──────────────────────────────────────────────────────

  describe('formatBRLCompact', () => {
    it('compacts millions', () => {
      const result = formatBRLCompact(1_500_000)
      // Should produce something like "R$ 1,5 mi" or "R$ 1,5M"
      expect(result).toMatch(/1[,.]?5/)
    })

    it('compacts thousands', () => {
      const result = formatBRLCompact(2000)
      expect(result).toMatch(/2/)
    })

    it('includes BRL currency symbol', () => {
      expect(formatBRLCompact(100)).toMatch(/R\$/)
    })
  })

  // ── formatPercent ─────────────────────────────────────────────────────────

  describe('formatPercent', () => {
    it('formats a fraction (0.05 → ~5%)', () => {
      const result = formatPercent(0.05)
      expect(result).toMatch(/5/)
      expect(result).toMatch(/%/)
    })

    it('shows positive sign for positive values', () => {
      const result = formatPercent(0.1)
      expect(result).toMatch(/\+/)
    })

    it('shows negative sign for negative values', () => {
      const result = formatPercent(-0.05)
      expect(result).toMatch(/[-−]/)
    })

    it('formats zero without sign', () => {
      const result = formatPercent(0)
      // zero should not have a + sign (signDisplay: exceptZero)
      expect(result).not.toMatch(/\+/)
    })
  })

  // ── formatPercentRaw ──────────────────────────────────────────────────────

  describe('formatPercentRaw', () => {
    it('formats raw percentage (5 → ~5%)', () => {
      const result = formatPercentRaw(5)
      expect(result).toMatch(/5/)
      expect(result).toMatch(/%/)
    })

    it('formats 100 as ~100%', () => {
      const result = formatPercentRaw(100)
      expect(result).toMatch(/100/)
    })
  })

  // ── deltaClass ────────────────────────────────────────────────────────────

  describe('deltaClass', () => {
    it('returns val-positive for positive values', () => {
      expect(deltaClass(10)).toBe('val-positive')
    })

    it('returns val-negative for negative values', () => {
      expect(deltaClass(-1)).toBe('val-negative')
    })

    it('returns val-neutral for zero', () => {
      expect(deltaClass(0)).toBe('val-neutral')
    })
  })

  // ── deltaSign ─────────────────────────────────────────────────────────────

  describe('deltaSign', () => {
    it('returns ▲ for positive values', () => {
      expect(deltaSign(5)).toBe('▲')
    })

    it('returns ▼ for negative values', () => {
      expect(deltaSign(-5)).toBe('▼')
    })

    it('returns ▲ for zero', () => {
      expect(deltaSign(0)).toBe('▲')
    })
  })
})

// ── Date helpers ──────────────────────────────────────────────────────────────

describe('currentMonthLabel', () => {
  afterEach(() => vi.useRealTimers())

  it('retorna mês abreviado e ano', () => {
    vi.useFakeTimers()
    vi.setSystemTime(new Date(2026, 5, 22))
    const { currentMonthLabel } = useFormatters()
    const result = currentMonthLabel()
    expect(result).toMatch(/[Jj]un/)
    expect(result).toContain('2026')
  })

  it('capitaliza a primeira letra do mês', () => {
    vi.useFakeTimers()
    vi.setSystemTime(new Date(2026, 0, 15))
    const { currentMonthLabel } = useFormatters()
    expect(currentMonthLabel().charAt(0)).toMatch(/[A-Z]/)
  })
})

describe('fmtMonthFull', () => {
  afterEach(() => vi.useRealTimers())

  it('retorna mês por extenso e ano', () => {
    vi.useFakeTimers()
    vi.setSystemTime(new Date(2026, 5, 22))
    const { fmtMonthFull } = useFormatters()
    const result = fmtMonthFull()
    expect(result).toMatch(/[Jj]unho/)
    expect(result).toContain('2026')
  })

  it('capitaliza a primeira letra do mês', () => {
    vi.useFakeTimers()
    vi.setSystemTime(new Date(2026, 0, 15))
    const { fmtMonthFull } = useFormatters()
    expect(fmtMonthFull().charAt(0)).toMatch(/[A-Z]/)
  })
})

describe('daysLeftInMonth', () => {
  afterEach(() => vi.useRealTimers())

  it('retorna número >= 0 e <= 31', () => {
    vi.useFakeTimers()
    vi.setSystemTime(new Date(2026, 5, 22))
    const { daysLeftInMonth } = useFormatters()
    const result = daysLeftInMonth()
    expect(result).toBeGreaterThanOrEqual(0)
    expect(result).toBeLessThanOrEqual(31)
  })

  it('retorna 8 em 22 de junho de 2026', () => {
    vi.useFakeTimers()
    vi.setSystemTime(new Date(2026, 5, 22))
    const { daysLeftInMonth } = useFormatters()
    expect(daysLeftInMonth()).toBe(8)
  })

  it('no último dia retorna 0', () => {
    vi.useFakeTimers()
    vi.setSystemTime(new Date(2026, 5, 30))
    const { daysLeftInMonth } = useFormatters()
    expect(daysLeftInMonth()).toBe(0)
  })
})
