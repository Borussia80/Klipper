-- Migration 008 — UNIQUE por usuário (correção de bug multiusuário)
-- Execute NO SQL Editor do Supabase.
--
-- Contexto: três constraints UNIQUE foram criadas SEM user_id (001/002), o que
-- impede dois usuários de terem o mesmo ticker / orçamento de categoria / meta.
-- Hoje não quebra porque só há um usuário, mas é um landmine multiusuário.
-- Ver docs/architecture/write-policy.md §4 e docs/security/rls_audit.md.
--
-- Idempotente: dropa a constraint antiga e a nova (se já existir) antes de criar.

-- ── investments: ticker UNIQUE global → (user_id, ticker) ────────────────────
ALTER TABLE investments DROP CONSTRAINT IF EXISTS investments_ticker_key;
ALTER TABLE investments DROP CONSTRAINT IF EXISTS investments_user_ticker_key;
ALTER TABLE investments
    ADD CONSTRAINT investments_user_ticker_key UNIQUE (user_id, ticker);

-- ── budgets: (category, year, month) → (user_id, category, year, month) ──────
ALTER TABLE budgets DROP CONSTRAINT IF EXISTS budgets_category_year_month_key;
ALTER TABLE budgets DROP CONSTRAINT IF EXISTS budgets_user_category_year_month_key;
ALTER TABLE budgets
    ADD CONSTRAINT budgets_user_category_year_month_key UNIQUE (user_id, category, year, month);

-- ── financial_goals: (year, month) → (user_id, year, month) ──────────────────
ALTER TABLE financial_goals DROP CONSTRAINT IF EXISTS financial_goals_year_month_key;
ALTER TABLE financial_goals DROP CONSTRAINT IF EXISTS financial_goals_user_year_month_key;
ALTER TABLE financial_goals
    ADD CONSTRAINT financial_goals_user_year_month_key UNIQUE (user_id, year, month);

-- ── Verificação ─────────────────────────────────────────────────────────────
-- Deve listar as 3 novas constraints com user_id na definição:
SELECT conrelid::regclass AS tabela, conname,
       pg_get_constraintdef(oid) AS definicao
FROM pg_constraint
WHERE conname IN ('investments_user_ticker_key',
                  'budgets_user_category_year_month_key',
                  'financial_goals_user_year_month_key')
ORDER BY tabela;

-- ATENÇÃO (coordenação com o front): após aplicar esta migration, o upsert de
-- orçamentos deve usar onConflict = "user_id,category,year,month".
-- Já ajustado em web/lib/queries/useBudgets.ts. Aplicar a migration ANTES de
-- subir o frontend novo (a constraint nova precisa existir para o onConflict).
