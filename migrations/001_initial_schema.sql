-- Klipper — Schema inicial Supabase
-- Execute este script no SQL Editor do painel Supabase

-- ============================================================
-- TRANSACTIONS
-- ============================================================
CREATE TABLE IF NOT EXISTS transactions (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    date        DATE NOT NULL,
    amount      NUMERIC(12, 2) NOT NULL CHECK (amount > 0),
    type        TEXT NOT NULL CHECK (type IN ('GASTO', 'GANHO')),
    category    TEXT NOT NULL,
    notes       TEXT NOT NULL DEFAULT '',
    created_at  TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions (date DESC);
CREATE INDEX IF NOT EXISTS idx_transactions_type ON transactions (type);

-- ============================================================
-- INVESTMENTS
-- ============================================================
CREATE TABLE IF NOT EXISTS investments (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ticker            TEXT NOT NULL UNIQUE,
    type              TEXT NOT NULL CHECK (type IN ('FII', 'Ação', 'Renda Fixa', 'Caixa')),
    quantity          NUMERIC(14, 4) NOT NULL CHECK (quantity > 0),
    avg_price         NUMERIC(12, 4) NOT NULL CHECK (avg_price > 0),
    current_price     NUMERIC(12, 4) NOT NULL CHECK (current_price > 0),
    dy_12m            NUMERIC(6, 2) NOT NULL DEFAULT 0,
    pvp               NUMERIC(6, 4) NOT NULL DEFAULT 0,
    liquidity_daily   NUMERIC(14, 2) NOT NULL DEFAULT 0,
    volatility        NUMERIC(6, 2) NOT NULL DEFAULT 0,
    spread_vs_cdi     NUMERIC(6, 2) NOT NULL DEFAULT 0,
    sector            TEXT NOT NULL DEFAULT '',
    fragility_score   NUMERIC(5, 4) NOT NULL DEFAULT 0 CHECK (fragility_score BETWEEN 0 AND 1),
    notes             TEXT NOT NULL DEFAULT '',
    updated_at        TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_investments_ticker ON investments (ticker);
CREATE INDEX IF NOT EXISTS idx_investments_type ON investments (type);

-- ============================================================
-- DECISIONS  (Investment Journal + Decision Template)
-- ============================================================
CREATE TABLE IF NOT EXISTS decisions (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ticker                  TEXT NOT NULL,
    date                    DATE NOT NULL DEFAULT CURRENT_DATE,

    -- M1 snapshot
    score_m1                NUMERIC(5, 4) DEFAULT 0,
    dy                      NUMERIC(6, 2) DEFAULT 0,
    pvp                     NUMERIC(6, 4) DEFAULT 0,
    liquidity               NUMERIC(14, 2) DEFAULT 0,

    -- M3 snapshot
    regime                  TEXT DEFAULT '',
    confidence              TEXT DEFAULT '',
    fragility               NUMERIC(5, 4) DEFAULT 0,

    -- Decisão
    outcome                 TEXT CHECK (outcome IN ('COMPRAR','MANTER','REDUZIR','VENDER') OR outcome IS NULL),
    invalidation_condition  TEXT NOT NULL DEFAULT '',

    -- Journal — antes da compra
    thesis                  TEXT NOT NULL DEFAULT '',
    risk                    TEXT NOT NULL DEFAULT '',
    alternative_scenario    TEXT NOT NULL DEFAULT '',
    expectation             TEXT NOT NULL DEFAULT '',

    -- Journal — depois
    result                  TEXT NOT NULL DEFAULT '',
    error                   TEXT NOT NULL DEFAULT '',
    learning                TEXT NOT NULL DEFAULT '',
    bias_identified         TEXT NOT NULL DEFAULT '',

    -- M4 AI audit
    ai_audit                TEXT NOT NULL DEFAULT '',
    ai_provider             TEXT NOT NULL DEFAULT '',
    uncertainty_declared    BOOLEAN NOT NULL DEFAULT FALSE,

    created_at              TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_decisions_ticker ON decisions (ticker);
CREATE INDEX IF NOT EXISTS idx_decisions_date ON decisions (date DESC);

-- ============================================================
-- Row Level Security (RLS) — habilitar para segurança
-- ============================================================
ALTER TABLE transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE investments ENABLE ROW LEVEL SECURITY;
ALTER TABLE decisions ENABLE ROW LEVEL SECURITY;

-- Política: acesso público via anon key (uso pessoal)
-- Para produção com autenticação, substituir por políticas por usuário
CREATE POLICY "allow_all_transactions" ON transactions FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "allow_all_investments"  ON investments  FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "allow_all_decisions"    ON decisions    FOR ALL USING (true) WITH CHECK (true);
