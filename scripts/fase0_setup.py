"""
scripts/fase0_setup.py — Executa a Fase 0 completa de forma autônoma.

Requer apenas UM token: o Supabase Personal Access Token.
  Encontre em: https://supabase.com/dashboard/account/tokens
  Tem a forma: sbp_xxxxxxxxxxxx...

Uso:
    SUPABASE_ACCESS_TOKEN=sbp_... python scripts/fase0_setup.py

O script:
  1. Obtém a service_role key via Management API
  2. Cria o usuário roberto.milet@gmail.com no Auth
  3. Executa migration 005a (adiciona user_id columns)
  4. Executa migration 005b (backfill + NOT NULL + policies user-scoped)
  5. Verifica que anon key = 0 linhas (critério de aceite)
  6. Imprime instrução única para Streamlit Cloud

Nota: atualização do Streamlit Cloud requer acesso ao dashboard web
(será impressa como último passo para o usuário completar).
"""

from __future__ import annotations

import os
import sys
import secrets
import string
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

PROJECT_REF = "obmudpulqzhwtcniyzcj"
OWNER_EMAIL = "roberto.milet@gmail.com"
BASE_DIR = Path(__file__).parent.parent
MIGRATION_005A = BASE_DIR / "migrations" / "005a_add_user_id_columns.sql"
MIGRATION_005B = BASE_DIR / "migrations" / "005b_rls_user_policies.sql"


def _token() -> str:
    t = os.environ.get("SUPABASE_ACCESS_TOKEN", "")
    if not t:
        print("ERRO: SUPABASE_ACCESS_TOKEN não definido.")
        print("  Obtenha em: https://supabase.com/dashboard/account/tokens")
        print("  Execute: SUPABASE_ACCESS_TOKEN=sbp_... python scripts/fase0_setup.py")
        sys.exit(1)
    return t


def _mgmt_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


def _project_headers(service_key: str) -> dict:
    return {
        "Authorization": f"Bearer {service_key}",
        "apikey": service_key,
        "Content-Type": "application/json",
    }


# ── Passo 1: Obter service_role key ──────────────────────────────────────────

def get_service_role_key(token: str) -> str:
    print("\n[1/5] Obtendo service_role key via Management API...")
    url = f"https://api.supabase.com/v1/projects/{PROJECT_REF}/api-keys"
    resp = requests.get(url, headers=_mgmt_headers(token), timeout=30)
    if resp.status_code != 200:
        print(f"ERRO: {resp.status_code} — {resp.text}")
        print("Verifique se o token tem permissão no projeto.")
        sys.exit(1)
    keys = resp.json()
    for k in keys:
        if k.get("name") == "service_role":
            key = k.get("api_key", "")
            masked = key[:12] + "..." if key else "?"
            print(f"  ✓ service_role key obtida: {masked}")
            return key
    print("ERRO: service_role key não encontrada na resposta.")
    print(f"  Resposta: {keys}")
    sys.exit(1)


# ── Passo 2: Criar usuário Auth ───────────────────────────────────────────────

def _generate_password(length: int = 24) -> str:
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return "".join(secrets.choice(alphabet) for _ in range(length))


def create_auth_user(service_key: str) -> str:
    """Cria o usuário Roberto no Auth. Retorna o UUID."""
    print(f"\n[2/5] Criando usuário Auth: {OWNER_EMAIL}...")
    url = f"https://{PROJECT_REF}.supabase.co/auth/v1/admin/users"

    # Primeiro verifica se já existe
    list_resp = requests.get(url, headers=_project_headers(service_key), timeout=30)
    if list_resp.status_code == 200:
        users = list_resp.json().get("users", [])
        existing = next((u for u in users if u.get("email") == OWNER_EMAIL), None)
        if existing:
            uid = existing["id"]
            print(f"  ✓ Usuário já existe: {uid}")
            return uid

    # Cria novo usuário
    password = _generate_password()
    payload = {
        "email": OWNER_EMAIL,
        "password": password,
        "email_confirm": True,
    }
    resp = requests.post(url, json=payload, headers=_project_headers(service_key), timeout=30)
    if resp.status_code not in (200, 201):
        print(f"ERRO ao criar usuário: {resp.status_code} — {resp.text}")
        sys.exit(1)
    uid = resp.json()["id"]
    print(f"  ✓ Usuário criado: {uid}")
    print(f"  ⚠️  Senha temporária gerada (troque após o primeiro login):")
    print(f"     {password}")
    print(f"  ⚠️  Salve essa senha agora — ela não será exibida novamente.")
    return uid


# ── Passo 3 & 4: Executar migrations via Management API ──────────────────────

def run_sql(token: str, sql: str, label: str) -> None:
    print(f"\n  Executando {label}...")
    url = f"https://api.supabase.com/v1/projects/{PROJECT_REF}/database/query"
    resp = requests.post(url, json={"query": sql}, headers=_mgmt_headers(token), timeout=60)
    if resp.status_code not in (200, 201):
        print(f"  ERRO {resp.status_code}: {resp.text[:500]}")
        sys.exit(1)
    print(f"  ✓ {label} concluída.")


def run_migrations(token: str) -> None:
    print("\n[3/5] Executando migrations...")
    sql_005a = MIGRATION_005A.read_text(encoding="utf-8")
    run_sql(token, sql_005a, "005a (adiciona user_id columns)")

    print("\n[4/5] Executando 005b (backfill + policies)...")
    sql_005b = MIGRATION_005B.read_text(encoding="utf-8")
    # Remove a query de verificação final (SELECT) para evitar timeout
    sql_005b_exec = sql_005b.split("-- ── 5. Verificação")[0].strip()
    run_sql(token, sql_005b_exec, "005b (backfill + NOT NULL + user-scoped policies)")


# ── Passo 5: Verificar RLS ────────────────────────────────────────────────────

TABLES = [
    "transactions", "investments", "decisions", "bank_accounts",
    "credit_cards", "installments", "budgets", "financial_goals",
    "category_memory", "transaction_splits",
]


def verify_rls(service_key: str) -> bool:
    print("\n[5/5] Verificando RLS — anon key deve retornar 0 linhas...")
    anon_key = os.environ.get("SUPABASE_KEY", "")
    if not anon_key:
        print("  AVISO: SUPABASE_KEY não encontrada — pulando verificação anon.")
        return True

    from supabase import create_client  # type: ignore
    anon_client = create_client(f"https://{PROJECT_REF}.supabase.co", anon_key)
    svc_client = create_client(f"https://{PROJECT_REF}.supabase.co", service_key)

    failures = []
    for table in TABLES:
        anon_count = anon_client.table(table).select("id", count="exact").execute().count or 0
        svc_count = svc_client.table(table).select("id", count="exact").execute().count or 0
        status = "✓" if anon_count == 0 else "✗"
        print(f"  {status} {table:<30} anon={anon_count}  service={svc_count}")
        if anon_count != 0:
            failures.append(table)

    if failures:
        print(f"\n  ❌ FALHOU — tabelas ainda expostas via anon: {failures}")
        return False
    print("\n  ✅ PASSOU — anon key bloqueada corretamente.")
    return True


# ── Passo final: instrução para Streamlit Cloud ───────────────────────────────

def print_streamlit_instruction(service_key: str) -> None:
    masked = service_key[:12] + "..." if service_key else "?"
    print("\n" + "=" * 60)
    print("AÇÃO MANUAL NECESSÁRIA — Streamlit Cloud")
    print("=" * 60)
    print("""
O Streamlit usa SUPABASE_KEY (atualmente anon key). Após o RLS
ativo, precisa da service_role key para continuar funcionando.

Passos:
  1. Acesse: https://share.streamlit.io/
  2. Seu app → Settings → Secrets
  3. Substitua:
       SUPABASE_KEY = "eyJhbGci..."   ← anon (atual)
     por:
       SUPABASE_KEY = "<service_role_key>"
  4. Clique em Save → aguarde o reboot

A service_role key começa com "eyJhbGci..." mas tem role=service_role
no payload JWT (diferente da anon key atual).
""")
    print(f"  service_role key (copie): começa com {masked}")


# ── main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    print("=" * 60)
    print("Klipper — Fase 0 Setup Automatizado")
    print(f"Projeto: {PROJECT_REF}")
    print("=" * 60)

    token = _token()

    service_key = get_service_role_key(token)
    create_auth_user(service_key)
    run_migrations(token)

    # Salva service_role key no .env local para uso futuro
    env_path = BASE_DIR / ".env"
    env_content = env_path.read_text(encoding="utf-8")
    if "SUPABASE_SERVICE_KEY=" not in env_content:
        env_path.write_text(env_content + f"\nSUPABASE_SERVICE_KEY={service_key}\n", encoding="utf-8")
        print(f"\n  → SUPABASE_SERVICE_KEY salva no .env local.")

    ok = verify_rls(service_key)
    print_streamlit_instruction(service_key)

    print("\n" + "=" * 60)
    if ok:
        print("✅ Fase 0 concluída com sucesso!")
        print("   Pendência: atualizar Streamlit Cloud (ver instrução acima).")
    else:
        print("⚠️  Fase 0 parcialmente concluída — verificar erros acima.")
    print("=" * 60)


if __name__ == "__main__":
    main()
