import { readdirSync, readFileSync } from 'node:fs'
import { join, relative } from 'node:path'
import { describe, expect, it } from 'vitest'

// Um `var(--x)` sem `--x` definido não quebra nada à vista: a propriedade cai
// no valor herdado e a tela fica com a cor ou o espaçamento errado sem erro
// nenhum. Foi assim que `configuracoes.vue` viveu com `--ink`, `--rule` e
// `--space-*`, nomes de um tema que o projeto não usa.
// O Vitest roda a partir de apps/klipper-web (onde está o vitest.config.ts).
const ROOT = process.cwd()
const DIRS = ['pages', 'components', 'layouts', 'assets/css']
const FILES_SOLTOS = ['app.vue']

// Cada exceção diz por que está aqui. Exceção que deixou de ser usada também
// falha, para a lista não apodrecer.
const EXCECOES: Record<string, string> = {
  '--mono': 'pages/importar.vue usa sem definição; correção fora do escopo da Fase 0.3, fica para PR próprio',
}

// Cores de banco são aceitas por prefixo: hoje estão definidas em tokens.css e
// nenhuma tela as usa (o BankIcon tira a cor de @edusites/bancos-brasil).
const PREFIXOS_ACEITOS = ['--bank-']

function arquivos(): string[] {
  const out: string[] = []
  for (const dir of DIRS) {
    for (const f of readdirSync(join(ROOT, dir), { recursive: true }) as string[]) {
      if (f.includes('__tests__')) continue
      if (f.endsWith('.vue') || f.endsWith('.css')) out.push(join(ROOT, dir, f))
    }
  }
  return [...out, ...FILES_SOLTOS.map((f) => join(ROOT, f))]
}

// Definidas = declarações `--x:` em qualquer CSS ou <style> (inclui variável
// escopada a um componente) e variáveis inline do template, seja em
// `style="--x: …"` ou em `:style="{ '--x': … }"`.
export function definidas(fonte: string): Set<string> {
  const nomes = new Set<string>()
  for (const m of fonte.matchAll(/(?:^|[\s;{"'])(--[a-zA-Z0-9-]+)\s*:/g)) nomes.add(m[1]!)
  for (const m of fonte.matchAll(/['"](--[a-zA-Z0-9-]+)['"]\s*:/g)) nomes.add(m[1]!)
  return nomes
}

// Usadas = cada `var(--x` encontrado. Em `var(--x, fallback)` só o nome conta;
// se o fallback for outro `var(--y)`, o regex também o encontra e ele é
// conferido.
export function usadas(fonte: string): Set<string> {
  return new Set([...fonte.matchAll(/var\(\s*(--[a-zA-Z0-9-]+)/g)].map((m) => m[1]!))
}

describe('tokens CSS', () => {
  const lista = arquivos()
  const fontes = new Map(lista.map((f) => [f, readFileSync(f, 'utf8')]))
  const todasDefinidas = new Set<string>()
  for (const fonte of fontes.values()) for (const n of definidas(fonte)) todasDefinidas.add(n)

  const aceita = (nome: string) =>
    todasDefinidas.has(nome) || nome in EXCECOES || PREFIXOS_ACEITOS.some((p) => nome.startsWith(p))

  it('todo var(--x) usado tem --x definido', () => {
    const faltando: string[] = []
    for (const [arquivo, fonte] of fontes) {
      for (const nome of usadas(fonte)) {
        if (!aceita(nome)) faltando.push(`${relative(ROOT, arquivo)}: ${nome}`)
      }
    }
    expect(faltando).toEqual([])
  })

  it('toda exceção ainda é usada e continua sem definição', () => {
    const usadosEmAlgumLugar = new Set<string>()
    for (const fonte of fontes.values()) for (const n of usadas(fonte)) usadosEmAlgumLugar.add(n)
    const obsoletas = Object.keys(EXCECOES).filter((n) => !usadosEmAlgumLugar.has(n) || todasDefinidas.has(n))
    expect(obsoletas).toEqual([])
  })
})

describe('extração de tokens', () => {
  it('lê o nome em var() com fallback literal e com fallback var()', () => {
    expect([...usadas('color: var(--a, #fff); border: var(--b, var(--c));')].sort()).toEqual(['--a', '--b', '--c'])
  })

  it('reconhece declaração em CSS, style inline e :style de objeto', () => {
    const fonte = `
      :root { --x: 1px; }
      .c { --escopada:2px }
      <div style="--inline: 3px"></div>
      <div :style="{ '--bind': valor }"></div>
    `
    expect([...definidas(fonte)].sort()).toEqual(['--bind', '--escopada', '--inline', '--x'])
  })

  it('não confunde uso com definição', () => {
    expect(definidas('color: var(--so-uso);').has('--so-uso')).toBe(false)
  })
})
