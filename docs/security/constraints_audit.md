# Auditoria de Constraints Multi-Tenant — Klipper

**Data:** 2026-06-14 · **Fase:** 0.5
**Escopo:** PRIMARY KEY, FOREIGN KEY, UNIQUE, INDEX nas 10 tabelas financeiras.
**Objetivo:** garantir que toda unicidade/relacionamento respeite o limite por usuário.

---

## 1. PRIMARY KEY

Todas as tabelas: `id UUID PRIMARY KEY DEFAULT gen_random_uuid()`.

**Veredito: ✅ OK.** PK por `id` global é correto — o UUID já é único entre usuários; não
precisa (nem deve) incluir `user_id` na PK.

## 2. UNIQUE

| Tabela | Constraint original | Problema | Correção |
|---|---|---|---|
| investments | `UNIQUE (ticker)` | 🔴 global — 2 usuários não teriam o mesmo ticker | `UNIQUE (user_id, ticker)` |
| budgets | `UNIQUE (category, year, month)` | 🔴 global | `UNIQUE (user_id, category, year, month)` |
| financial_goals | `UNIQUE (year, month)` | 🔴 global | `UNIQUE (user_id, year, month)` |
| category_memory | `UNIQUE (user_id, pattern)` | ✅ já por usuário | — |
| transaction_splits | (só PK) | ✅ sem unicidade extra | — |
| transactions / accounts / cards / installments / decisions | (só PK) | ✅ | — |

**Correção aplicada:** `migrations/008_user_scoped_unique.sql` (as 3 globais → por usuário).
Coordenação de front: `useBudgets` usa `onConflict: "user_id,category,year,month"`.

> ✅ **APLICADA E VERIFICADA no banco em 2026-06-14.** As constraints criadas:
> - `investments_user_ticker_key` → `UNIQUE (user_id, ticker)`
> - `budgets_user_category_year_month_key` → `UNIQUE (user_id, category, year, month)`
> - `financial_goals_user_year_month_key` → `UNIQUE (user_id, year, month)`

## 3. FOREIGN KEY

| FK | Referência | On Delete | Multi-tenant |
|---|---|---|---|
| `*.user_id` (10 tabelas) | `auth.users(id)` | CASCADE | ✅ correto |
| `transactions.account_id` | `bank_accounts(id)` | SET NULL | ⚠️ por `id` global |
| `transactions.card_id` | `credit_cards(id)` | SET NULL | ⚠️ por `id` global |
| `transactions.installment_id` | `installments(id)` | SET NULL | ⚠️ por `id` global |
| `transaction_splits.transaction_id` | `transactions(id)` | CASCADE | ⚠️ por `id` global |

**Veredito: ✅ aceitável, com ressalva.** As FKs referenciam `id` (UUID global), não
`(user_id, id)`. Em teoria um usuário poderia vincular uma transação a um `card_id` de outro
usuário **se conhecesse o UUID**. Mitigações reais:
- **RLS** impede `SELECT` de linhas de outro usuário → o UUID alheio não é descobrível pela API;
- **UUID v4** não é adivinhável.

Severidade **baixa**. FK composta `(user_id, id)` exigiria PK composta nas tabelas-pai e
complicaria o schema sem ganho proporcional. **Recomendação:** manter por `id` + reforçar no
gateway que `account_id`/`card_id` informados pertencem ao `user_id` do JWT (validação de
posse na escrita). Registrar como item P2.

## 4. INDEX

| Índice | Coluna(s) | Observação |
|---|---|---|
| idx_transactions_date | (date DESC) | perf; consultas são por usuário (RLS) |
| idx_transactions_type | (type) | perf |
| idx_investments_ticker | (ticker) | perf |
| idx_investments_type | (type) | perf |
| idx_decisions_ticker | (ticker) | perf |
| idx_decisions_date | (date DESC) | perf |
| idx_category_memory_user | (user_id) | ✅ já inclui user_id |
| idx_splits_tx | (transaction_id) | perf |

**Veredito: ✅ sem problema de correção** (índice não afeta isolamento). **Oportunidade de
perf (P3):** sob RLS, toda query carrega um predicado implícito `user_id = auth.uid()`.
Índices compostos `(user_id, date)`, `(user_id, ticker)` etc. seriam mais seletivos. Opcional,
só vale com volume. Não bloqueia.

## 5. Resumo

| Categoria | Status | Ação |
|---|---|---|
| PRIMARY KEY | ✅ OK | — |
| UNIQUE | ✅ corrigido e aplicado | `008` aplicada e verificada (2026-06-14) |
| FOREIGN KEY | ⚠️ baixo risco | validar posse de `account_id`/`card_id` no gateway (P2) |
| INDEX | ✅ OK | índices compostos por `user_id` opcionais (P3) |

**Pendência bloqueante:** nenhuma — `008` aplicada e verificada (2026-06-14). FK (P2) e
índices compostos (P3) ficam como itens não-bloqueantes.
