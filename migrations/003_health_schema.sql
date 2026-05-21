-- Migration 003 — Módulo Saúde (TEA)
-- Controle de atendimentos, solicitações de reembolso e profissionais de saúde.
-- Executar no SQL Editor do Supabase após 002_v2_schema.sql.

-- ── Profissionais de saúde ────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS health_professionals (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    name            TEXT        NOT NULL,
    specialty       TEXT        NOT NULL
                                CHECK (specialty IN (
                                    'FONOAUDIOLOGIA','TERAPIA_OCUPACIONAL','PSICOLOGIA',
                                    'PSIQUIATRIA','NEUROLOGIA','FISIOTERAPIA','OUTRO'
                                )),
    council_number  TEXT,       -- CRP, CREFITO, CRM, etc.
    is_active       BOOLEAN     NOT NULL DEFAULT true,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ── Solicitações de reembolso ─────────────────────────────────────────────────
-- Criada antes de health_sessions para que a FK funcione.
CREATE TABLE IF NOT EXISTS reimbursement_requests (
    id                UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    professional_id   UUID        NOT NULL REFERENCES health_professionals(id),
    request_date      DATE        NOT NULL,
    protocol_number   TEXT,       -- protocolo gerado pela operadora ao receber
    amount_requested  NUMERIC(10,2) NOT NULL CHECK (amount_requested > 0),
    amount_received   NUMERIC(10,2),  -- nulo até a operadora pagar
    status            TEXT        NOT NULL DEFAULT 'PENDENTE'
                                  CHECK (status IN ('PENDENTE','REEMBOLSADO','PARCIAL','NEGADO')),
    notes             TEXT,       -- motivo de glosa, observações da operadora
    created_at        TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ── Sessões / atendimentos ────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS health_sessions (
    id                          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    professional_id             UUID        NOT NULL REFERENCES health_professionals(id),
    session_date                DATE        NOT NULL,
    amount_paid                 NUMERIC(10,2) NOT NULL CHECK (amount_paid > 0),
    nf_number                   TEXT,       -- número da nota fiscal ou recibo
    notes                       TEXT,
    reimbursement_request_id    UUID        REFERENCES reimbursement_requests(id),
    created_at                  TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ── Índices ───────────────────────────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_health_sessions_professional ON health_sessions(professional_id);
CREATE INDEX IF NOT EXISTS idx_health_sessions_date         ON health_sessions(session_date DESC);
CREATE INDEX IF NOT EXISTS idx_health_sessions_request      ON health_sessions(reimbursement_request_id);
CREATE INDEX IF NOT EXISTS idx_reimbursement_professional   ON reimbursement_requests(professional_id);
CREATE INDEX IF NOT EXISTS idx_reimbursement_status         ON reimbursement_requests(status);
