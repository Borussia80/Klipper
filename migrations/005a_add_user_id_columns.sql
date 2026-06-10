-- Migration 005a — Adiciona coluna user_id em todas as tabelas
-- SEGURO para executar enquanto o Streamlit está em produção.
-- Não altera nenhuma policy existente — o acesso continua aberto.
--
-- Executar NO SQL Editor do Supabase.
-- Pré-requisito: nenhum.
-- Próximo passo: criar usuário Auth + executar 005b.

-- ── transactions ──────────────────────────────────────────────────────────────
ALTER TABLE transactions
    ADD COLUMN IF NOT EXISTS user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE;

-- ── investments ───────────────────────────────────────────────────────────────
ALTER TABLE investments
    ADD COLUMN IF NOT EXISTS user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE;

-- ── decisions ─────────────────────────────────────────────────────────────────
ALTER TABLE decisions
    ADD COLUMN IF NOT EXISTS user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE;

-- ── bank_accounts ─────────────────────────────────────────────────────────────
ALTER TABLE bank_accounts
    ADD COLUMN IF NOT EXISTS user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE;

-- ── credit_cards ──────────────────────────────────────────────────────────────
ALTER TABLE credit_cards
    ADD COLUMN IF NOT EXISTS user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE;

-- ── installments ──────────────────────────────────────────────────────────────
ALTER TABLE installments
    ADD COLUMN IF NOT EXISTS user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE;

-- ── budgets ───────────────────────────────────────────────────────────────────
ALTER TABLE budgets
    ADD COLUMN IF NOT EXISTS user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE;

-- ── financial_goals ───────────────────────────────────────────────────────────
ALTER TABLE financial_goals
    ADD COLUMN IF NOT EXISTS user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE;

-- ── health_professionals ──────────────────────────────────────────────────────
ALTER TABLE health_professionals
    ADD COLUMN IF NOT EXISTS user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE;

-- ── reimbursement_requests ────────────────────────────────────────────────────
ALTER TABLE reimbursement_requests
    ADD COLUMN IF NOT EXISTS user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE;

-- ── health_sessions ───────────────────────────────────────────────────────────
ALTER TABLE health_sessions
    ADD COLUMN IF NOT EXISTS user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE;

-- ── Verificação ───────────────────────────────────────────────────────────────
-- Confirmar que as colunas foram criadas (deve retornar 11 linhas):
SELECT table_name, column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_schema = 'public'
  AND column_name = 'user_id'
ORDER BY table_name;
