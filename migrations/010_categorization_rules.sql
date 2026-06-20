-- Klipper — Regras de auto-categorização determinísticas
-- Aplicadas ANTES do fuzzy+memória (maior prioridade). priority ASC = aplicado primeiro.

CREATE TABLE IF NOT EXISTS categorization_rules (
    id          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    priority    INTEGER     NOT NULL DEFAULT 100,
    field       TEXT        NOT NULL CHECK (field       IN ('notes', 'amount')),
    operator    TEXT        NOT NULL CHECK (operator    IN ('contains', 'starts_with', 'equals', 'greater_than', 'less_than', 'regex')),
    value       TEXT        NOT NULL,
    category    TEXT        NOT NULL,
    is_active   BOOLEAN     NOT NULL DEFAULT true,
    user_id     UUID        NOT NULL DEFAULT auth.uid(),
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_cat_rules_user_prio
    ON categorization_rules (user_id, priority);

ALTER TABLE categorization_rules ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "user_cat_rules" ON categorization_rules;
CREATE POLICY "user_cat_rules" ON categorization_rules
    FOR ALL USING (user_id = auth.uid())
    WITH CHECK (user_id = auth.uid());
