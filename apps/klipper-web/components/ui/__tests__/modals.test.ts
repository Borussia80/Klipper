import { describe, it, expect, vi, afterEach } from 'vitest'
import { isFutureDate } from '../../../composables/useFormatters'

describe('isFutureDate', () => {
  afterEach(() => vi.useRealTimers())

  it('retorna false para data de hoje', () => {
    vi.useFakeTimers()
    vi.setSystemTime(new Date(2026, 5, 27, 12, 0, 0))
    expect(isFutureDate('2026-06-27')).toBe(false)
  })

  it('retorna false para data passada', () => {
    vi.useFakeTimers()
    vi.setSystemTime(new Date(2026, 5, 27, 12, 0, 0))
    expect(isFutureDate('2026-06-01')).toBe(false)
  })

  it('retorna true para amanhã', () => {
    vi.useFakeTimers()
    vi.setSystemTime(new Date(2026, 5, 27, 12, 0, 0))
    expect(isFutureDate('2026-06-28')).toBe(true)
  })

  it('retorna true para data futura distante', () => {
    vi.useFakeTimers()
    vi.setSystemTime(new Date(2026, 5, 27, 12, 0, 0))
    expect(isFutureDate('2099-01-01')).toBe(true)
  })
})
