-- Migration 005b — Backfill user_id + políticas RLS user-scoped
--
-- PRÉ-REQUISITOS:
--   1. 005a já executado (colunas user_id existem).
--   2. Usuário roberto.milet@gmail.com criado no Supabase Auth Dashboard
--      (Authentication → Users → Add user).
--   3. Substituir o placeholder abaixo pelo UUID real:
--      SELECT id FROM auth.users WHERE email = 'roberto.milet@gmail.com';
--
-- ATENÇÃO:
--   - SUPABASE_KEY no Streamlit Cloud / Railway deve ser a **service_role key**.
--     A service_role bypassa RLS — o Streamlit continua funcionando sem mudança.
--   - A anon key (para o PWA browser) estará sujeita ao RLS.
--
-- Executar NO SQL Editor do Supabase.

-- ── 1. Definir o UUID do usuário (substituir o placeholder!) ──────────────────
DO $$
DECLARE
    owner_id UUID;
BEGIN
    SELECT id INTO owner_id
    FROM auth.users
    WHERE email = 'roberto.milet@gmail.com'
    LIMIT 1;

    IF owner_id IS NULL THEN
        RAISE EXCEPTION
            'Usuário roberto.milet@gmail.com não encontrado em auth.users. '
            'Crie o usuário no Supabase Auth Dashboard antes de executar este script.';
    END IF;

    -- ── 2. Backfill: preencher user_id em todas as linhas existentes ──────────
    UPDATE transactions         SET user_id = owner_id WHERE user_id IS NULL;
    UPDATE investments          SET user_id = owner_id WHERE user_id IS NULL;
    UPDATE decisions            SET user_id = owner_id WHERE user_id IS NULL;
    UPDATE bank_accounts        SET user_id = owner_id WHERE user_id IS NULL;
    UPDATE credit_cards         SET user_id = owner_id WHERE user_id IS NULL;
    UPDATE installments         SET user_id = owner_id WHERE user_id IS NULL;
    UPDATE budgets              SET user_id = owner_id WHERE user_id IS NULL;
    UPDATE financial_goals      SET user_id = owner_id WHERE user_id IS NULL;
    UPDATE health_professionals SET user_id = owner_id WHERE user_id IS NULL;
    UPDATE reimbursement_requests SET user_id = owner_id WHERE user_id IS NULL;
    UPDATE health_sessions      SET user_id = owner_id WHERE user_id IS NULL;

    RAISE NOTICE 'Backfill concluído para user_id = %', owner_id;
END $$;

-- ── 3. NOT NULL + DEFAULT auth.uid() ─────────────────────────────────────────
ALTER TABLE transactions
    ALTER COLUMN user_id SET NOT NULL,
    ALTER COLUMN user_id SET DEFAULT auth.uid();

ALTER TABLE investments
    ALTER COLUMN user_id SET NOT NULL,
    ALTER COLUMN user_id SET DEFAULT auth.uid();

ALTER TABLE decisions
    ALTER COLUMN user_id SET NOT NULL,
    ALTER COLUMN user_id SET DEFAULT auth.uid();

ALTER TABLE bank_accounts
    ALTER COLUMN user_id SET NOT NULL,
    ALTER COLUMN user_id SET DEFAULT auth.uid();

ALTER TABLE credit_cards
    ALTER COLUMN user_id SET NOT NULL,
    ALTER COLUMN user_id SET DEFAULT auth.uid();

ALTER TABLE installments
    ALTER COLUMN user_id SET NOT NULL,
    ALTER COLUMN user_id SET DEFAULT auth.uid();

ALTER TABLE budgets
    ALTER COLUMN user_id SET NOT NULL,
    ALTER COLUMN user_id SET DEFAULT auth.uid();

ALTER TABLE financial_goals
    ALTER COLUMN user_id SET NOT NULL,
    ALTER COLUMN user_id SET DEFAULT auth.uid();

ALTER TABLE health_professionals
    ALTER COLUMN user_id SET NOT NULL,
    ALTER COLUMN user_id SET DEFAULT auth.uid();

ALTER TABLE reimbursement_requests
    ALTER COLUMN user_id SET NOT NULL,
    ALTER COLUMN user_id SET DEFAULT auth.uid();

ALTER TABLE health_sessions
    ALTER COLUMN user_id SET NOT NULL,
    ALTER COLUMN user_id SET DEFAULT auth.uid();

-- ── 4. Substituir policies allow_all por user-scoped ─────────────────────────

-- transactions
DROP POLICY IF EXISTS "allow_all_transactions" ON transactions;
CREATE POLICY "user_transactions" ON transactions
    FOR ALL USING (user_id = auth.uid())
    WITH CHECK (user_id = auth.uid());

-- investments
DROP POLICY IF EXISTS "allow_all_investments" ON investments;
CREATE POLICY "user_investments" ON investments
    FOR ALL USING (user_id = auth.uid())
    WITH CHECK (user_id = auth.uid());

-- decisions
DROP POLICY IF EXISTS "allow_all_decisions" ON decisions;
CREATE POLICY "user_decisions" ON decisions
    FOR ALL USING (user_id = auth.uid())
    WITH CHECK (user_id = auth.uid());

-- bank_accounts
DROP POLICY IF EXISTS "allow_all_bank_accounts" ON bank_accounts;
CREATE POLICY "user_bank_accounts" ON bank_accounts
    FOR ALL USING (user_id = auth.uid())
    WITH CHECK (user_id = auth.uid());

-- credit_cards
DROP POLICY IF EXISTS "allow_all_credit_cards" ON credit_cards;
CREATE POLICY "user_credit_cards" ON credit_cards
    FOR ALL USING (user_id = auth.uid())
    WITH CHECK (user_id = auth.uid());

-- installments
DROP POLICY IF EXISTS "allow_all_installments" ON installments;
CREATE POLICY "user_installments" ON installments
    FOR ALL USING (user_id = auth.uid())
    WITH CHECK (user_id = auth.uid());

-- budgets
DROP POLICY IF EXISTS "allow_all_budgets" ON budgets;
CREATE POLICY "user_budgets" ON budgets
    FOR ALL USING (user_id = auth.uid())
    WITH CHECK (user_id = auth.uid());

-- financial_goals
DROP POLICY IF EXISTS "allow_all_financial_goals" ON financial_goals;
CREATE POLICY "user_financial_goals" ON financial_goals
    FOR ALL USING (user_id = auth.uid())
    WITH CHECK (user_id = auth.uid());

-- health_professionals
DROP POLICY IF EXISTS "allow_all_health_professionals" ON health_professionals;
CREATE POLICY "user_health_professionals" ON health_professionals
    FOR ALL USING (user_id = auth.uid())
    WITH CHECK (user_id = auth.uid());

-- reimbursement_requests
DROP POLICY IF EXISTS "allow_all_reimbursement_requests" ON reimbursement_requests;
CREATE POLICY "user_reimbursement_requests" ON reimbursement_requests
    FOR ALL USING (user_id = auth.uid())
    WITH CHECK (user_id = auth.uid());

-- health_sessions
DROP POLICY IF EXISTS "allow_all_health_sessions" ON health_sessions;
CREATE POLICY "user_health_sessions" ON health_sessions
    FOR ALL USING (user_id = auth.uid())
    WITH CHECK (user_id = auth.uid());

-- ── 5. Verificação ────────────────────────────────────────────────────────────
-- Deve retornar 11 políticas com policy_name contendo "user_":
SELECT schemaname, tablename, policyname, cmd, qual
FROM pg_policies
WHERE schemaname = 'public'
  AND policyname LIKE 'user_%'
ORDER BY tablename;
