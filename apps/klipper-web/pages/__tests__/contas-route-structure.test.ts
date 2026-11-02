import { describe, expect, it } from 'vitest'
import { existsSync } from 'node:fs'
import { resolve } from 'node:path'

const pages = resolve(import.meta.dirname, '..')

describe('rotas de contas', () => {
  it('mantém a listagem em index.vue para não capturar a rota filha no Nuxt', () => {
    // Se contas.vue coexistir com contas/, o Nuxt trata a página como pai de /contas/:id.
    expect(existsSync(resolve(pages, 'contas.vue'))).toBe(false)
    expect(existsSync(resolve(pages, 'contas/index.vue'))).toBe(true)
    expect(existsSync(resolve(pages, 'contas/[id].vue'))).toBe(true)
  })
})
