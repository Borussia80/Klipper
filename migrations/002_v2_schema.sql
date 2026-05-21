-- Klipper v2.0 — Schema Migration
-- Run this in Supabase SQL Editor after 001_initial_schema.sql

-- ──────────────────────────────────────────────────────
-- New tables
-- ──────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS bank_accounts (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name        TEXT NOT NULL,
    bank        TEXT NOT NULL DEFAULT '',
    type        TEXT NOT NULL DEFAULT 'CORRENTE'
                    CHECK (type IN ('CORRENTE', 'POUPANCA', 'INVESTIMENTO')),
    balance     NUMERIC(14, 2) NOT NULL DEFAULT 0.00,
    color       TEXT NOT NULL DEFAULT '#6366F1',
    is_active   BOOLEAN NOT NULL DEFAULT true,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS credit_cards (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name        TEXT NOT NULL,
    bank        TEXT NOT NULL DEFAULT '',
    limit_total NUMERIC(14, 2) NOT NULL DEFAULT 0.00,
    closing_day INT NOT NULL DEFAULT 1 CHECK (closing_day BETWEEN 1 AND 31),
    due_day     INT NOT NULL DEFAULT 10 CHECK (due_day BETWEEN 1 AND 31),
    color       TEXT NOT NULL DEFAULT '#EF4444',
    is_active   BOOLEAN NOT NULL DEFAULT true,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS installments (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    description         TEXT NOT NULL,
    total_amount        NUMERIC(14, 2) NOT NULL,
    n_total             INT NOT NULL CHECK (n_total >= 1),
    n_paid              INT NOT NULL DEFAULT 0 CHECK (n_paid >= 0),
    installment_amount  NUMERIC(14, 2) NOT NULL,
    start_date          DATE NOT NULL,
    card_id             UUID REFERENCES credit_cards(id) ON DELETE SET NULL,
    account_id          UUID REFERENCES bank_accounts(id) ON DELETE SET NULL,
    category            TEXT NOT NULL DEFAULT 'Outros',
    notes               TEXT NOT NULL DEFAULT '',
    is_active           BOOLEAN NOT NULL DEFAULT true,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS budgets (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    category        TEXT NOT NULL,
    monthly_limit   NUMERIC(14, 2) NOT NULL,
    year            INT NOT NULL,
    month           INT NOT NULL CHECK (month BETWEEN 1 AND 12),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (category, year, month)
);

CREATE TABLE IF NOT EXISTS financial_goals (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    savings_rate_target     NUMERIC(5, 2) NOT NULL DEFAULT 20.00,
    year                    INT NOT NULL,
    month                   INT NOT NULL CHECK (month BETWEEN 1 AND 12),
    created_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (year, month)
);

-- ──────────────────────────────────────────────────────
-- Extend transactions table
-- ──────────────────────────────────────────────────────

ALTER TABLE transactions
    ADD COLUMN IF NOT EXISTS payment_method TEXT NOT NULL DEFAULT 'PIX'
        CHECK (payment_method IN ('PIX','CARTAO_CREDITO','CARTAO_DEBITO',
                                  'DINHEIRO','TED','BOLETO','TRANSFERENCIA'));

ALTER TABLE transactions
    ADD COLUMN IF NOT EXISTS account_id UUID REFERENCES bank_accounts(id) ON DELETE SET NULL;

ALTER TABLE transactions
    ADD COLUMN IF NOT EXISTS card_id UUID REFERENCES credit_cards(id) ON DELETE SET NULL;

ALTER TABLE transactions
    ADD COLUMN IF NOT EXISTS installment_id UUID REFERENCES installments(id) ON DELETE SET NULL;

ALTER TABLE transactions
    ADD COLUMN IF NOT EXISTS status TEXT NOT NULL DEFAULT 'PAGO'
        CHECK (status IN ('PAGO', 'PENDENTE', 'AGENDADO'));

-- ──────────────────────────────────────────────────────
-- Row-Level Security for new tables
-- ──────────────────────────────────────────────────────

ALTER TABLE bank_accounts ENABLE ROW LEVEL SECURITY;
CREATE POLICY "allow_all_bank_accounts" ON bank_accounts FOR ALL USING (true) WITH CHECK (true);

ALTER TABLE credit_cards ENABLE ROW LEVEL SECURITY;
CREATE POLICY "allow_all_credit_cards" ON credit_cards FOR ALL USING (true) WITH CHECK (true);

ALTER TABLE installments ENABLE ROW LEVEL SECURITY;
CREATE POLICY "allow_all_installments" ON installments FOR ALL USING (true) WITH CHECK (true);

ALTER TABLE budgets ENABLE ROW LEVEL SECURITY;
CREATE POLICY "allow_all_budgets" ON budgets FOR ALL USING (true) WITH CHECK (true);

ALTER TABLE financial_goals ENABLE ROW LEVEL SECURITY;
CREATE POLICY "allow_all_financial_goals" ON financial_goals FOR ALL USING (true) WITH CHECK (true);
