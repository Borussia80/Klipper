-- Klipper — Migration 004: padroniza colunas monetárias para NUMERIC(15,4)
-- Executar no SQL Editor do Supabase após 003_health_schema.sql.
--
-- Motivação: modelos Python agora usam decimal.Decimal. Ampliar a precisão
-- (de NUMERIC(12,2) → NUMERIC(15,4)) garante que arredondamentos de 4 casas
-- produzidos pelo motor de parcelamentos sejam armazenados fielmente.
-- Operação segura: widening apenas — nenhum dado existente é truncado.

-- ── transactions ─────────────────────────────────────────────────────────────
ALTER TABLE transactions
    ALTER COLUMN amount TYPE NUMERIC(15,4) USING amount::NUMERIC(15,4);

-- ── investments ───────────────────────────────────────────────────────────────
ALTER TABLE investments
    ALTER COLUMN avg_price       TYPE NUMERIC(15,4) USING avg_price::NUMERIC(15,4),
    ALTER COLUMN current_price   TYPE NUMERIC(15,4) USING current_price::NUMERIC(15,4),
    ALTER COLUMN liquidity_daily TYPE NUMERIC(15,4) USING liquidity_daily::NUMERIC(15,4);

-- ── bank_accounts ─────────────────────────────────────────────────────────────
ALTER TABLE bank_accounts
    ALTER COLUMN balance TYPE NUMERIC(15,4) USING balance::NUMERIC(15,4);

-- ── credit_cards ──────────────────────────────────────────────────────────────
ALTER TABLE credit_cards
    ALTER COLUMN limit_total TYPE NUMERIC(15,4) USING limit_total::NUMERIC(15,4);

-- ── installments ──────────────────────────────────────────────────────────────
ALTER TABLE installments
    ALTER COLUMN total_amount       TYPE NUMERIC(15,4) USING total_amount::NUMERIC(15,4),
    ALTER COLUMN installment_amount TYPE NUMERIC(15,4) USING installment_amount::NUMERIC(15,4);

-- ── budgets ───────────────────────────────────────────────────────────────────
ALTER TABLE budgets
    ALTER COLUMN monthly_limit TYPE NUMERIC(15,4) USING monthly_limit::NUMERIC(15,4);

-- ── health_sessions ───────────────────────────────────────────────────────────
ALTER TABLE health_sessions
    ALTER COLUMN amount_paid TYPE NUMERIC(15,4) USING amount_paid::NUMERIC(15,4);

-- ── reimbursement_requests ────────────────────────────────────────────────────
ALTER TABLE reimbursement_requests
    ALTER COLUMN amount_requested TYPE NUMERIC(15,4) USING amount_requested::NUMERIC(15,4),
    ALTER COLUMN amount_received  TYPE NUMERIC(15,4) USING amount_received::NUMERIC(15,4);
