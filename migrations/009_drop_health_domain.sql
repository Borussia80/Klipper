-- Migration 009 — Remoção do domínio de SAÚDE do Klipper
-- Execute NO SQL Editor do Supabase. (Migrations são manuais — ver docs/security/.)
--
-- MOTIVO: o Klipper é, a partir de 2026-06-14, **exclusivamente financeiro**. A gestão
-- clínica/fiscal do Pedro (consultas, NF, protocolos, reembolso Bradesco) vive no projeto
-- desktop **Gestor-Reembolsos**, que é o sistema-de-registro desse domínio. O módulo de
-- saúde já foi removido do código (PWA + Streamlit + core/health_repository.py + models/health.py).
-- Esta migration remove o que sobrou no banco. Ver docs/architecture/domain-scope.md.
--
-- DADOS: confirmado pelo dono (Roberto) que os dados reais já estão preservados no
-- Gestor-Reembolsos. Esta operação é DESTRUTIVA e irreversível no Supabase.
--
-- (Opcional) BACKUP antes de dropar — rode e salve o resultado, se quiser uma cópia extra:
--   SELECT * FROM health_professionals;
--   SELECT * FROM reimbursement_requests;
--   SELECT * FROM health_sessions;
--
-- Ordem de drop respeita as FKs:
--   health_sessions → (reimbursement_requests, health_professionals)
--   reimbursement_requests → health_professionals
-- DROP TABLE remove junto as policies, índices e constraints da própria tabela.

DROP TABLE IF EXISTS health_sessions        CASCADE;
DROP TABLE IF EXISTS reimbursement_requests CASCADE;
DROP TABLE IF EXISTS health_professionals   CASCADE;

-- ── Verificação ─────────────────────────────────────────────────────────────
-- Deve retornar 0 linhas (nenhuma das 3 tabelas existe mais):
SELECT tablename
FROM pg_tables
WHERE schemaname = 'public'
  AND tablename IN ('health_professionals', 'reimbursement_requests', 'health_sessions');
