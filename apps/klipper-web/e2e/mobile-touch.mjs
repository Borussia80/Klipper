// Auditoria de toque e layout mobile em navegador real (fatia 1 de UI/UX).
//
// Requisitos verificados (docs/ux-research):
// - doc 04 §5: alvo de toque mínimo de 44 px no celular;
// - UXR-08: nenhuma tela rola para o lado em 390 px;
// - spec 02 (aceite 4) e UXR-07: o botão de salvar aparece sem rolar;
// - UXR-12: "Mais" é diálogo por teclado (foco entra, Esc fecha, foco volta);
// - campos com 16 px ou mais, para o Safari não dar zoom ao focar.
//
// O happy-dom do Vitest não mede layout; por isso esta checagem roda num
// Chromium real contra `nuxt dev`, com a API interceptada por dados fictícios.
//
// Uso: com `npm run dev` no ar, `npm run test:mobile`.
// Variáveis: BASE_URL (padrão http://localhost:3000) e SHOTS_DIR (se definida,
// salva capturas em 2x nessa pasta).

import { createRequire } from 'node:module'
import { mkdirSync } from 'node:fs'
import { join } from 'node:path'

const require = createRequire(import.meta.url)
const { chromium } = require('playwright')

const BASE_URL = process.env.BASE_URL ?? 'http://localhost:3000'
const SHOTS_DIR = process.env.SHOTS_DIR
const MIN_TAP = 44
const PAGES = ['/dashboard', '/transacoes', '/orcamento', '/contas']

// ── Dados fictícios ──────────────────────────────────────────────────────────
const today = new Date().toISOString().slice(0, 10)
const accounts = [
  { id: 1, name: 'Conta Corrente Teste', institution: 'Banco Fictício', account_type: 'corrente', balance: '1300.00', opening_balance: '1000.00', opening_balance_on: '2026-01-01', currency: 'BRL', active: true, created_at: today, updated_at: today, saldo_fatura_atual: null, pagamento_minimo: null, juros_rotativo_am: null, juros_rotativo_aa: null, iof_projetado: null, saldo_atualizado_em: null },
  { id: 2, name: 'Cartão Teste', institution: 'Banco Fictício', account_type: 'cartao', balance: '-250.00', currency: 'BRL', active: true, created_at: today, updated_at: today, saldo_fatura_atual: '250.00', pagamento_minimo: null, juros_rotativo_am: null, juros_rotativo_aa: null, iof_projetado: null, saldo_atualizado_em: null },
]
const categories = [
  { id: 1, name: 'Mercado', icon: 'cart', category_type: 'expense', natureza: 'variavel', color: null, active: true, reimbursed_by_category_id: null },
  { id: 2, name: 'Salário', icon: 'money', category_type: 'income', natureza: 'fixo', color: null, active: true, reimbursed_by_category_id: null },
]
const transactions = Array.from({ length: 12 }, (_, i) => ({
  id: i + 1,
  account_id: 1,
  category_id: i % 3 === 0 ? 2 : 1,
  description: i % 3 === 0 ? 'Salário de teste' : `Compra de teste ${i}`,
  amount: i % 3 === 0 ? '5000.00' : `${(i * 13.7).toFixed(2)}`,
  transaction_type: i % 3 === 0 ? 'credit' : 'debit',
  occurred_on: today,
  notes: null,
  installment_total: null,
  installment_number: null,
  member_id: null,
  kind: 'regular',
  status: 'efetivado',
}))

function fixtureFor(path) {
  if (path.endsWith('/auth/refresh')) return { token: 'token-ficticio' }
  if (path.endsWith('/users/me')) return { id: 1, name: 'Pessoa Teste', email: 'teste@example.com' }
  if (path.endsWith('/accounts')) return accounts
  if (path.endsWith('/categories')) return categories
  if (path.endsWith('/transactions')) return transactions
  if (/\/(members|budgets|investments|imports)$/.test(path)) return []
  if (path.endsWith('/budgets/summary')) return []
  return {}
}

// ── Checagens ────────────────────────────────────────────────────────────────
const failures = []
function check(ok, message) {
  console.log(`${ok ? '✓' : '✗'} ${message}`)
  if (!ok) failures.push(message)
}

async function newPage(browser, viewport) {
  const context = await browser.newContext({ viewport, deviceScaleFactor: SHOTS_DIR ? 2 : 1, hasTouch: viewport.width < 768 })
  await context.addCookies([{ name: 'klipper_token', value: 'token-ficticio', url: BASE_URL }])
  await context.route('**/api/v1/**', (route) => {
    const path = new URL(route.request().url()).pathname
    route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(fixtureFor(path)) })
  })
  return context.newPage()
}

// Abre a página e esconde o overlay do Nuxt DevTools, que só existe em
// `nuxt dev` e cobriria a barra inferior.
async function open(page, path) {
  await page.goto(`${BASE_URL}${path}`, { waitUntil: 'networkidle' })
  await page.addStyleTag({ content: '#nuxt-devtools-container { display: none !important; }' })
}

async function shot(page, name) {
  if (!SHOTS_DIR) return
  mkdirSync(SHOTS_DIR, { recursive: true })
  await page.screenshot({ path: join(SHOTS_DIR, `${name}.png`), fullPage: false })
}

async function noHorizontalScroll(page) {
  return page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)
}

// Alvos visíveis menores que 44 px. Links dentro de texto corrido ficam de
// fora (exceção prevista para alvos em linha).
async function smallTargets(page, root = 'body') {
  return page.evaluate(([min, rootSel]) => {
    const out = []
    for (const el of document.querySelector(rootSel).querySelectorAll('button, a[href], [role="button"], select')) {
      const r = el.getBoundingClientRect()
      const style = getComputedStyle(el)
      if (r.width === 0 || r.height === 0 || style.visibility === 'hidden') continue
      if (r.bottom < 0 || r.top > window.innerHeight) continue
      if (el.tagName === 'A' && style.display === 'inline') continue
      if (r.width < min - 0.5 || r.height < min - 0.5) {
        const label = el.getAttribute('aria-label') || el.textContent.trim().slice(0, 30) || el.tagName
        out.push(`${label} (${Math.round(r.width)}×${Math.round(r.height)})`)
      }
    }
    return out
  }, [MIN_TAP, root])
}

async function smallFonts(page, root = 'body') {
  return page.evaluate((rootSel) => {
    const out = []
    for (const el of document.querySelector(rootSel).querySelectorAll('input:not([type=checkbox]):not([type=radio]):not([type=hidden]), select, textarea')) {
      const r = el.getBoundingClientRect()
      if (r.width === 0 || r.height === 0) continue
      const size = parseFloat(getComputedStyle(el).fontSize)
      if (size < 16) out.push(`${el.getAttribute('aria-label') || el.name || el.type} (${size}px)`)
    }
    return out
  }, root)
}

async function auditMobile(browser) {
  const page = await newPage(browser, { width: 390, height: 844 })

  for (const path of PAGES) {
    await open(page, path)
    await shot(page, `390${path.replaceAll('/', '-')}`)
    check(await noHorizontalScroll(page), `390 px ${path}: sem rolagem lateral (UXR-08)`)
    const small = await smallTargets(page)
    check(small.length === 0, `390 px ${path}: alvos ≥ 44 px (doc 04)${small.length ? ` — menores: ${small.join('; ')}` : ''}`)
  }

  // Folha de lançamento: Salvar visível sem rolar, com o valor em foco.
  await open(page, '/dashboard')
  await page.click('nav[aria-label="Navegação mobile"] button[aria-label="Novo lançamento"]')
  const dialog = page.locator('[role="dialog"][aria-label="Novo lançamento"]')
  await dialog.waitFor()
  await page.waitForTimeout(300) // fim da transição de entrada
  await page.locator('input[aria-label="Valor do lançamento em reais"]').focus()
  await shot(page, '390-folha-lancamento')
  const ctaVisible = await page.locator('[role="dialog"] button.cta').evaluate((el) => {
    const r = el.getBoundingClientRect()
    return r.top >= 0 && r.bottom <= window.innerHeight && r.height >= 44
  })
  check(ctaVisible, '390 px folha de lançamento: Salvar visível sem rolar, com 44 px (spec 02, aceite 4)')
  // Com a folha aberta, só ela é tocável; o conteúdo por trás fica coberto.
  const sheet = '[role="dialog"][aria-label="Novo lançamento"]'
  const fonts = await smallFonts(page, sheet)
  check(fonts.length === 0, `390 px folha de lançamento: campos com 16 px ou mais${fonts.length ? ` — menores: ${fonts.join('; ')}` : ''}`)
  const sheetTargets = await smallTargets(page, sheet)
  check(sheetTargets.length === 0, `390 px folha de lançamento: alvos ≥ 44 px${sheetTargets.length ? ` — menores: ${sheetTargets.join('; ')}` : ''}`)
  await page.keyboard.press('Escape')

  // "Mais" por teclado (UXR-12).
  await open(page, '/dashboard')
  const trigger = page.locator('button[aria-label="Mais páginas"]')
  await trigger.focus()
  await page.keyboard.press('Enter')
  const more = page.locator('section[aria-label="Mais páginas"]')
  await more.waitFor()
  await shot(page, '390-mais')
  check(await more.getAttribute('role') === 'dialog', '"Mais": anunciado como diálogo (UXR-12)')
  check(await more.evaluate((el) => el.contains(document.activeElement)), '"Mais": o foco entra no diálogo ao abrir (UXR-12)')
  const moreTargets = await smallTargets(page, 'section[aria-label="Mais páginas"]')
  check(moreTargets.length === 0, `"Mais": alvos ≥ 44 px${moreTargets.length ? ` — menores: ${moreTargets.join('; ')}` : ''}`)
  await page.keyboard.press('Escape')
  check(await more.count() === 0, '"Mais": Esc fecha (UXR-12)')
  check(await trigger.evaluate((el) => el === document.activeElement), '"Mais": o foco volta ao gatilho (UXR-12)')

  await page.context().close()
}

async function auditDesktop(browser) {
  const page = await newPage(browser, { width: 1440, height: 900 })
  for (const path of PAGES) {
    await open(page, path)
    await shot(page, `1440${path.replaceAll('/', '-')}`)
    check(await noHorizontalScroll(page), `1440 px ${path}: sem rolagem lateral`)
  }
  await page.context().close()
}

const browser = await chromium.launch()
try {
  await auditMobile(browser)
  await auditDesktop(browser)
} finally {
  await browser.close()
}

console.log(failures.length ? `\n${failures.length} checagem(ns) falharam.` : '\nTodas as checagens passaram.')
process.exit(failures.length ? 1 : 0)
