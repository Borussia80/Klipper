-- Klipper — Memória de categorização (aprende com rótulos confirmados pelo usuário)
-- Execute este script no SQL Editor do painel Supabase.
--
-- Guarda, por usuário, o padrão normalizado da descrição (assinatura do
-- estabelecimento) → categoria que o usuário confirmou. É a camada 1 do
-- categorizador fuzzy (core/categorizer.py): tem precedência sobre as regras
-- genéricas. Uma linha por estabelecimento distinto (dedup por pattern), não
-- por transação — escala para milhares de transações sem inchar.

-- ============================================================
-- CATEGORY_MEMORY
-- ============================================================
CREATE TABLE IF NOT EXISTS category_memory (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pattern     TEXT NOT NULL,              -- descrição normalizada (ex.: "uber")
    category    TEXT NOT NULL,
    hits        INTEGER NOT NULL DEFAULT 1, -- quantas vezes foi confirmado
    user_id     UUID NOT NULL DEFAULT auth.uid(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (user_id, pattern)
);

CREATE INDEX IF NOT EXISTS idx_category_memory_user ON category_memory (user_id);

-- ── RLS — cada usuário só enxerga a própria memória ──────────────────────────
ALTER TABLE category_memory ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "user_category_memory" ON category_memory;
CREATE POLICY "user_category_memory" ON category_memory
    FOR ALL USING (user_id = auth.uid())
    WITH CHECK (user_id = auth.uid());
