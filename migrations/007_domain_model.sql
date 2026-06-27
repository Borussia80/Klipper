-- Klipper — Fase 0.5: modelo de domínio (rateio + recorrência)
-- Execute no SQL Editor do Supabase após 006_category_memory.sql

-- ── Recorrência ───────────────────────────────────────────────────────────────

ALTER TABLE transactions
    ADD COLUMN IF NOT EXISTS is_recurring BOOLEAN NOT NULL DEFAULT false;

-- ── Rateio ────────────────────────────────────────────────────────────────────
-- Uma transação com category='Rateado' pode ter N splits.
-- Splits e parcelamento não são mutuamente exclusivos no schema:
-- cada transação filha de um parcelamento rateado carrega seus próprios splits
-- proporcionais, calculados pelo gateway.

CREATE TABLE IF NOT EXISTS transaction_splits (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    transaction_id  UUID NOT NULL REFERENCES transactions(id) ON DELETE CASCADE,
    category        TEXT NOT NULL,
    amount          NUMERIC(14, 2) NOT NULL CHECK (amount > 0),
    user_id         UUID NOT NULL DEFAULT auth.uid(),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_splits_tx ON transaction_splits (transaction_id);

ALTER TABLE transaction_splits ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "user_splits" ON transaction_splits;
CREATE POLICY "user_splits" ON transaction_splits
    FOR ALL USING (user_id = auth.uid())
    WITH CHECK (user_id = auth.uid());
