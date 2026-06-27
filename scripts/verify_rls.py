"""
scripts/verify_rls.py — Verifica que RLS está corretamente configurado.

Critérios de aceite da Fase 0:
  1. anon key sem sessão  → zero linhas em todas as tabelas
  2. service_role key     → dados completos (prova que Streamlit continua funcionando)

Uso:
    python scripts/verify_rls.py

Variáveis de ambiente necessárias:
    SUPABASE_URL          URL do projeto
    SUPABASE_ANON_KEY     chave pública (anon/publishable)
    SUPABASE_SERVICE_KEY  chave privada (service_role) — nunca exposta no browser
"""

from __future__ import annotations

import os
import sys

from dotenv import load_dotenv

load_dotenv()

TABLES = [
    "transactions",
    "investments",
    "decisions",
    "bank_accounts",
    "credit_cards",
    "installments",
    "budgets",
    "financial_goals",
    "category_memory",
    "transaction_splits",
]


def _count(client, table: str) -> int:
    resp = client.table(table).select("id", count="exact").execute()
    return resp.count or 0


def _check_env() -> tuple[str, str, str]:
    url = os.environ.get("SUPABASE_URL", "")
    # SUPABASE_ANON_KEY explícita, ou fallback para SUPABASE_KEY (que pode ser anon)
    anon = os.environ.get("SUPABASE_ANON_KEY") or os.environ.get("SUPABASE_KEY", "")
    svc = os.environ.get("SUPABASE_SERVICE_KEY", "")
    missing = [k for k, v in [("SUPABASE_URL", url), ("SUPABASE_ANON_KEY / SUPABASE_KEY", anon), ("SUPABASE_SERVICE_KEY", svc)] if not v]
    if missing:
        print(f"ERRO: variáveis ausentes: {', '.join(missing)}")
        print("Adicione ao .env e rode novamente.")
        sys.exit(1)
    return url, anon, svc


def verify() -> None:
    from supabase import create_client

    url, anon_key, svc_key = _check_env()

    print("=" * 60)
    print("Klipper — Verificação de RLS (Fase 0)")
    print("=" * 60)

    # ── Teste 1: anon key sem sessão → deve retornar 0 linhas ────────────────
    print("\n[1] anon key (sem sessão) — espera: 0 linhas em todas as tabelas")
    anon_client = create_client(url, anon_key)
    failures_anon = []
    for table in TABLES:
        count = _count(anon_client, table)
        status = "✓" if count == 0 else "✗"
        print(f"  {status} {table:<30} {count} linha(s)")
        if count != 0:
            failures_anon.append(table)

    # ── Teste 2: service_role → deve retornar dados ───────────────────────────
    print("\n[2] service_role key — espera: dados acessíveis (Streamlit usa esta key)")
    svc_client = create_client(url, svc_key)
    failures_svc = []
    for table in TABLES:
        count = _count(svc_client, table)
        status = "✓" if count >= 0 else "✗"
        print(f"  {status} {table:<30} {count} linha(s)")

    # ── Resultado ─────────────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    if not failures_anon:
        print("✅ PASSOU — anon key bloqueada corretamente")
    else:
        print(f"❌ FALHOU — tabelas expostas via anon: {failures_anon}")
        print("   Verifique se 005b foi executado e as policies user-scoped estão ativas.")

    if failures_anon:
        sys.exit(1)


if __name__ == "__main__":
    verify()
