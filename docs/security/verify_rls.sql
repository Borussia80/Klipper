-- ============================================================================
-- verify_rls.sql — Verificação do estado APLICADO de RLS no Supabase
-- ----------------------------------------------------------------------------
-- READ-ONLY. Não altera nada. Cole no SQL Editor do Supabase.
--
-- Objetivo: confirmar que o que as migrations DECLARAM (001, 002, 005a, 005b,
-- 006, 007) está de fato APLICADO. A existência da migration no repo NÃO garante
-- que foi executada — 005b/006/007 são manuais (SQL Editor).
--
-- O SQL Editor mostra apenas o resultado da ÚLTIMA instrução de um script. Por
-- isso a verificação principal é UMA query só (DIAGNÓSTICO). As consultas de
-- detalhe abaixo são opcionais — rode-as individualmente se precisar investigar.
--
-- Critério de aprovação (Fase 0.3): as 10 tabelas devem retornar status = 'OK'.
-- ============================================================================

-- ╔══════════════════════════════════════════════════════════════════════════╗
-- ║ DIAGNÓSTICO — uma linha por tabela. Rode este bloco. Esperado: tudo 'OK'.  ║
-- ╚══════════════════════════════════════════════════════════════════════════╝
WITH alvo(t) AS (
    VALUES ('transactions'), ('transaction_splits'), ('bank_accounts'),
           ('credit_cards'), ('installments'), ('investments'),
           ('budgets'), ('financial_goals'), ('decisions'), ('category_memory')
),
pol AS (
    SELECT tablename,
           COUNT(*) FILTER (WHERE policyname ILIKE 'user_%')      AS user_pol,
           COUNT(*) FILTER (WHERE policyname ILIKE 'allow_all_%') AS allow_pol
    FROM pg_policies
    WHERE schemaname = 'public'
    GROUP BY tablename
)
SELECT
    a.t                                       AS tabela,
    COALESCE(c.relrowsecurity, false)         AS rls_on,
    (col.column_name IS NOT NULL
        AND col.is_nullable = 'NO')           AS user_id_notnull,
    COALESCE(p.user_pol, 0)                    AS user_policies,
    COALESCE(p.allow_pol, 0)                   AS allow_all_policies,
    CASE
        WHEN c.relname IS NULL                          THEN '*** FALHA: tabela ausente ***'
        WHEN NOT c.relrowsecurity                       THEN '*** FALHA: RLS desligado ***'
        WHEN COALESCE(p.allow_pol, 0) > 0              THEN '*** PERIGO: allow_all ainda ativa ***'
        WHEN COALESCE(p.user_pol, 0) = 0               THEN '*** FALHA: sem policy user-scoped ***'
        WHEN col.column_name IS NULL
             OR col.is_nullable = 'YES'                 THEN '*** FALHA: user_id nullable/ausente ***'
        ELSE 'OK'
    END                                       AS status
FROM alvo a
LEFT JOIN pg_namespace n ON n.nspname = 'public'
LEFT JOIN pg_class c     ON c.relname = a.t AND c.relnamespace = n.oid
LEFT JOIN information_schema.columns col
       ON col.table_schema = 'public' AND col.table_name = a.t AND col.column_name = 'user_id'
LEFT JOIN pol p          ON p.tablename = a.t
ORDER BY (CASE WHEN c.relname IS NULL OR NOT c.relrowsecurity
                    OR COALESCE(p.allow_pol,0) > 0 OR COALESCE(p.user_pol,0) = 0
                    OR col.column_name IS NULL OR col.is_nullable = 'YES'
               THEN 0 ELSE 1 END), a.t;


-- ╔══════════════════════════════════════════════════════════════════════════╗
-- ║ DETALHE (opcional) — rode individualmente se o diagnóstico acusar algo.    ║
-- ╚══════════════════════════════════════════════════════════════════════════╝

-- D1 — Todas as policies das tabelas-alvo (cmd, USING, WITH CHECK):
-- SELECT tablename, policyname, cmd, qual AS using_expr, with_check
-- FROM pg_policies
-- WHERE schemaname = 'public'
--   AND tablename IN ('transactions','transaction_splits','bank_accounts','credit_cards',
--                     'installments','investments','budgets','financial_goals',
--                     'decisions','category_memory')
-- ORDER BY tablename, policyname;

-- D2 — Policies permissivas remanescentes (esperado: 0 linhas):
-- SELECT tablename, policyname
-- FROM pg_policies
-- WHERE schemaname = 'public' AND policyname ILIKE 'allow_all_%'
-- ORDER BY tablename;
