# 06 — Plano de implementação

**Aprovado em 2026-10-17.** Direção visual náutica, sem mudança de paleta; cores de banco mantidas; "+" no centro da
barra inferior mobile; dia de fechamento e de vencimento do cartão incluídos.

Regras do projeto valem em tudo: teste antes do código (Vitest / RSpec); um PR por fatia; merge um por vez esperando
o CI do `main`; uso local primeiro (Rails 3000, Nuxt 3001; Render/Vercel hibernados); Postgres de teste via
`podman start klipper-pg-test`.

## Escopo liberado agora: Fase 0 + Fatias 1 e 2

**Fatias 3–7 estão bloqueadas** até a análise de domínio (`docs/domain-research/`) ser aprovada — evita retrabalho em
saldo, cartão e agendados.

---

## Fase 0 — Correções

### 0.1 Isolar a suíte do Vitest da API local
`vitest.config.ts` aponta `NUXT_PUBLIC_API_URL` para uma porta morta. PR #135.

### 0.2 Documentos
Esta pesquisa e os docs de design alinhados à direção náutica.

### 0.3 `pages/configuracoes.vue` + teste de tokens
- Trocar os tokens inexistentes (`--ink`, `--ink-3`, `--rule`, `--space-3/4/5`) pelos reais.
- Teste (`assets/css/__tests__/tokens.test.ts`) que lê todo `var(--x…)` de `pages/`, `components/`, `layouts/` e
  CSS e falha se `--x` não estiver definido:
  - definidos = `--x:` em `tokens.css`, `main.css` e nos `<style>` dos `.vue` (variável escopada);
  - `var(--x, fallback)`: conta o nome; o fallback é ignorado, ou conferido se também for `var`;
  - variável definida inline (`style="--x:…"`, `:style="{ '--x': … }"`) conta como definida;
  - `--bank-*` aceito por prefixo (hoje definidos em `tokens.css` e não usados por nenhuma tela — `BankIcon` tira a
    cor de `@edusites/bancos-brasil`; dead code pré-existente, só registrado);
  - **lista de exceções explícita no próprio teste**, cada uma com o porquê; exceção que deixou de ser usada também
    falha.

### 0.4 `orcamento.vue` — `budgetSpentRatio(...) ?? 0`
"Sem orçamento" vira "0 %". Corrigido na Fatia 5, junto com a tela.

## Fatia 1 — Categorias em dois níveis (spec 07)

Backend primeiro. Usa `categories.active` como "oculta" (já existe). Migração `parent_id`, `position`,
`merged_into_id`. Validações, `CategoryMergeService` e a regra de orçamento pai × filha estão detalhados em
`05-specs/07-categorias.md`. Frontend: `composables/useCategoryTree.ts` (porte P4), seletor reutilizável e gestão em
`/configuracoes`.

## Fatia 2 — Lançamento rápido + navegação mobile (spec 02)

- `utils/amountExpression.ts` (porte P1), regras de ponto × vírgula e casos de teste em `05-specs/02-lancamento-rapido.md`.
- Reaproveitar `composables/useLancamentoForm.ts`; a folha mobile é apresentação nova.
- `MobileNav.vue`: Painel · Movimento · [+] · Orçamento · Mais (Investimentos para "Mais").
- `GET /categories?sort=usage&limit=8` e `GET /categories/suggest?description=` (usa `AutoCategorizerService.call`).
- Toast com "Desfazer" via `useToast`.
- Cria `THIRD_PARTY_NOTICES.md` na raiz.

---

## ⛔ Bloqueadas até `docs/domain-research/` ser aprovada

| Fatia | Spec | Já decidido para quando liberar |
|---|---|---|
| 3 — Painel com patrimônio + alarmes | 01 | Migrar `dia_fechamento` **junto** com `dia_vencimento`. Dia maior que o mês → último dia; vencimento em fim de semana/feriado → próximo dia útil; fechamento não se desloca. Testes: fevereiro bissexto e não, 30/31, sábado, domingo, feriado |
| 4 — Transações e contas | 03, 04 | `bulk_update` numa transação de banco, com escopo por usuário (ids ou categoria de outro usuário → 404, nada alterado). *O item chegou cortado em "escopo por" — confirmar ao liberar* |
| 5 — Orçamento | 05 | Ritmo, por dia, `copy_previous`, correção 0.4 |
| 6 — Agendados | 06 | Portes P2/P3 sem job; conciliação sugerida primeiro; o merge de categorias passa a mover agendados |
| 7 — OFX + regras | — | Portes P5/P6 |

---

## Itens do ezBookkeeping a portar

| # | Origem (commit `ff168cf`) | O que faz | Destino no Klipper | Fatia |
|---|---|---|---|---|
| P1 | `src/lib/evaluator.ts` | Avalia `45,90+12` sem `eval`, com limites | `apps/klipper-web/utils/amountExpression.ts` | 2 |
| P2 | `pkg/models/transaction_template.go` + `src/core/template.ts` | Modelo de frequência | `scheduled_transactions` + enum no model | 6 |
| P3 | `pkg/services/transactions.go#CreateScheduledTransactions` | Quais agendamentos vencem num intervalo | `app/services/scheduled_occurrences_calculator.rb` | 6 |
| P4 | `pkg/models/transaction_category.go` + `src/lib/category.ts` | Categoria com pai e ordem; marcar pai marca filhas | migração + `composables/useCategoryTree.ts` | 1 |
| P5 | `src/core/rule.ts` + `src/lib/rule.ts` | Regras condição → ação na importação | `app/services/import_rules/` (desenho) | 7 |
| P6 | `pkg/converters/ofx/*` | Leitura de OFX/QFX | `app/services/bank_import/ofx_reader.rb` | 7 |
| P7 | `src/lib/overview_layout.ts` | Blocos do painel configuráveis | **Não portar** | — |

Cabeçalho obrigatório em cada arquivo portado, e entrada com a licença MIT integral em `THIRD_PARTY_NOTICES.md`:

```
Portions adapted from ezBookkeeping (https://github.com/mayswind/ezbookkeeping), commit ff168cf,
<arquivo de origem>. Copyright (c) 2020-2026 MaysWind. Licensed under the MIT License.
```

## Riscos

| Risco | Mitigação |
|---|---|
| Telas sem moldura ou sem hierarquia | Critério de aceite com screenshot em 1440 px e 390 px em toda spec |
| Contaminação da sala limpa durante a implementação | Specs autossuficientes; `07-registro-pi.md` atualizado a cada consulta |
| Soma por pai errada muda relatórios | Specs dos calculators com pai + filhas antes de mudar o código |
| Render Free hiberna | Agendados sem job; cálculo sob demanda |

## Verificação de cada PR

1. `cd apps/klipper-web && npm run test` verde.
2. `podman start klipper-pg-test` e `bundle exec rspec` verde.
3. App local nas duas larguras, critérios de aceite da spec conferidos, screenshot no PR.
4. CI verde → merge → CI do `main` verde → próximo PR.
