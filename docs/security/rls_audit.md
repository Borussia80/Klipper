# Auditoria de RLS — Klipper

**Data da auditoria:** 2026-06-14
**Fase:** 0.3 — Estabilização / Segurança
**Escopo:** 10 tabelas de domínio financeiro
**Método:** análise estática das migrations + verificação do estado aplicado (SQL Editor)
**Status geral:** ✅ **10/10 conformes no estado aplicado** (após remediação da 007 em
2026-06-14). Estado declarado e aplicado agora coincidem. Ver §7.

---

## 1. Tabelas auditadas

`transactions`, `transaction_splits`, `bank_accounts`, `credit_cards`,
`installments`, `investments`, `budgets`, `financial_goals`, `decisions`,
`category_memory`.

> As tabelas de saúde (`health_professionals`, `health_sessions`,
> `reimbursement_requests`) estão **fora do escopo financeiro** e marcadas para
> remoção (ver `spec/fatia-6.md` OBSOLETA). Têm RLS user-scoped declarada em 005b,
> mas serão dropadas na Fase 1.3.

## 2. Convenção de política adotada

O projeto usa **uma única policy `FOR ALL` por tabela**:

```sql
CREATE POLICY "user_<tabela>" ON <tabela>
    FOR ALL USING (user_id = auth.uid())
    WITH CHECK (user_id = auth.uid());
```

- `FOR ALL` aplica-se a **SELECT, INSERT, UPDATE e DELETE**.
- `USING (user_id = auth.uid())` → rege **SELECT / UPDATE / DELETE** (linhas visíveis/afetadas).
- `WITH CHECK (user_id = auth.uid())` → rege **INSERT / UPDATE** (valores aceitos).

Portanto o checklist SELECT/INSERT/UPDATE/DELETE do roadmap é satisfeito por **uma**
policy — não são necessárias 4 policies separadas. Cada tabela tem ainda
`user_id UUID NOT NULL DEFAULT auth.uid()`.

## 3. Relatório de conformidade (estado declarado)

| Tabela | RLS | SELECT | INSERT | UPDATE | DELETE | user_id NOT NULL | Origem | Status |
|---|---|---|---|---|---|---|---|---|
| transactions | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | 001 + 005b | ✅ |
| transaction_splits | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | 007 | ✅ |
| bank_accounts | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | 002 + 005b | ✅ |
| credit_cards | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | 002 + 005b | ✅ |
| installments | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | 002 + 005b | ✅ |
| investments | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | 001 + 005b | ✅ |
| budgets | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | 002 + 005b | ✅ |
| financial_goals | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | 002 + 005b | ✅ |
| decisions | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | 001 + 005b | ✅ |
| category_memory | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | 006 | ✅ |

**Políticas encontradas (declaradas):**
- `ENABLE ROW LEVEL SECURITY`: 001 (transactions, investments, decisions),
  002 (bank_accounts, credit_cards, installments, budgets, financial_goals),
  006 (category_memory), 007 (transaction_splits).
- `user_id`: adicionado em 005a (8 tabelas core), `NOT NULL` + `DEFAULT auth.uid()` em 005b;
  já criado `NOT NULL DEFAULT auth.uid()` em 006 (category_memory) e 007 (transaction_splits).
- Policies user-scoped: 005b (8 tabelas), 006 (`user_category_memory`), 007 (`user_splits`).
- 005b faz `DROP POLICY IF EXISTS "allow_all_*"` antes de criar as user-scoped.

## 4. Gaps identificados

**No estado declarado: nenhum.** As 10 tabelas têm RLS + user_id NOT NULL + policy
user-scoped cobrindo os 4 comandos.

### ⚠️ Risco de estado aplicado (não verificado)

A existência da migration **não garante** que foi executada. As migrations
005b/006/007 são **manuais** (comentário "Executar NO SQL Editor do Supabase"), e a
005b aborta com `RAISE EXCEPTION` se o usuário não existir no `auth.users`. Cenários de
drift a confirmar:

1. **005b não aplicada** → as 8 tabelas core mantêm a policy `allow_all_* FOR ALL
   USING (true)` de 001/002: **RLS ligado, mas porta aberta** a qualquer usuário
   autenticado (vazamento horizontal entre usuários).
2. **006/007 não aplicadas** → `category_memory` / `transaction_splits` podem não
   existir ou estar sem policy/`user_id`.
3. **Backfill incompleto** → linhas antigas com `user_id NULL` teriam bloqueado o
   `SET NOT NULL` (a migration teria falhado — sinal indireto de não-aplicação).

### Consideração: service_role bypassa RLS

`SUPABASE_KEY` (service_role, usada por Streamlit e pela `api/` FastAPI) **ignora RLS
por design**. O isolamento RLS protege apenas o caminho do PWA (anon key + JWT). Logo:
- a `api/` deve **sempre** setar `user_id` explicitamente nos INSERTs (não confiar no
  `DEFAULT auth.uid()`, que é NULL sob service_role);
- vazamento da service_role key anula o RLS — tratar como segredo crítico.

## 5. Migrations criadas

**Nenhuma migration corretiva** foi gerada — o estado declarado já está conforme.
Conforme o protocolo ("somente após o diagnóstico criar a migration"), uma corretiva só
será escrita **se** a verificação do estado aplicado (passo 6) revelar drift.

Entregue no lugar: **`docs/security/verify_rls.sql`** — script read-only de verificação
do estado aplicado.

## 6. Procedimento de verificação do estado aplicado

`psql` não está disponível no ambiente local e não há connection string direta do
Postgres (apenas a API key, que não introspecciona `pg_policies`). Opções:

**Opção A — SQL Editor (recomendada, manual):**
1. Abrir o SQL Editor do projeto Supabase.
2. Colar e rodar o bloco **DIAGNÓSTICO** de `docs/security/verify_rls.sql` (uma query
   só — o SQL Editor mostra apenas o resultado da última instrução).
3. Aprovação: as 10 linhas devem ter `status = 'OK'`, com `rls_on = true`,
   `user_id_notnull = true`, `user_policies = 1` e `allow_all_policies = 0`.
4. Qualquer status diferente de `OK` aponta o gap exato (RLS off, allow_all ativa,
   sem policy user-scoped, ou user_id nullable). Use as consultas de DETALHE (D1/D2)
   para investigar.

**Opção B — Probe externo com anon key (automatizável):**
Uma requisição **não autenticada** com a anon key a cada tabela: se a RLS estiver
corretamente aplicada, retorna 0 linhas; se `allow_all` ainda existir, retorna dados
(= vazamento). É read-only e prova o isolamento de fora. Requer autorização para
acessar a produção.

## 7. Resultado da verificação aplicada

**Executado em:** 2026-06-14 (SQL Editor do Supabase, bloco DIAGNÓSTICO).

**Resultado: 9/10 tabelas `OK`. 1 gap.**

| Tabela | rls_on | user_id_notnull | user_policies | allow_all | status |
|---|---|---|---|---|---|
| transactions | true | true | 1 | 0 | ✅ OK |
| bank_accounts | true | true | 1 | 0 | ✅ OK |
| credit_cards | true | true | 1 | 0 | ✅ OK |
| installments | true | true | 1 | 0 | ✅ OK |
| investments | true | true | 1 | 0 | ✅ OK |
| budgets | true | true | 1 | 0 | ✅ OK |
| financial_goals | true | true | 1 | 0 | ✅ OK |
| decisions | true | true | 1 | 0 | ✅ OK |
| category_memory | true | true | 1 | 0 | ✅ OK |
| **transaction_splits** | false | false | 0 | 0 | ❌ **TABELA AUSENTE** |

### Conclusão

- **RLS das 9 tabelas existentes está aplicada e correta** — sem `allow_all` remanescente,
  sem porta aberta. O backfill/NOT NULL/policies de 005b **foram aplicados**.
- **`transaction_splits` não existe no banco → a migration 007 não foi aplicada.**
  Confirmado em 2026-06-14: a coluna `transactions.is_recurring` **também está ausente**
  (a consulta de verificação retornou 0 linhas). A 007 não foi aplicada em momento
  algum — falta a tabela `transaction_splits` **e** a coluna `is_recurring`. Isso
  **quebra escritas via gateway** (que grava `is_recurring` e splits). Severidade:
  **alta** (afeta produção).

### Remediação

A 007 já é **idempotente** (`ADD COLUMN IF NOT EXISTS`, `CREATE TABLE IF NOT EXISTS`,
`DROP POLICY IF EXISTS` → `CREATE POLICY`). **Não é necessária uma migration nova** — a
correção é **aplicar a 007 existente** no SQL Editor:

1. Rodar `migrations/007_domain_model.sql` no SQL Editor.
2. Re-rodar o DIAGNÓSTICO de `verify_rls.sql` → esperar 10/10 `OK`.
3. (Confirmar `is_recurring`) — ver consulta abaixo.

```sql
-- Confirma a outra metade da 007 (coluna is_recurring em transactions):
SELECT column_name, is_nullable, column_default
FROM information_schema.columns
WHERE table_schema = 'public' AND table_name = 'transactions' AND column_name = 'is_recurring';
-- 0 linhas = coluna ausente (007 não aplicada). 1 linha = OK.
```

**Por que não criar `008`:** duplicar o DDL da 007 num arquivo novo deixaria a 007
permanentemente "pendente" no histórico e confundiria a ordem. O artefato correto existe;
faltou executá-lo.

### Reverificação pós-remediação — 2026-06-14 ✅

Após aplicar a 007 no SQL Editor, o bloco DIAGNÓSTICO retornou **10/10 `OK`**:

| Tabela | rls_on | user_id_notnull | user_policies | allow_all | status |
|---|---|---|---|---|---|
| transactions | true | true | 1 | 0 | ✅ OK |
| transaction_splits | true | true | 1 | 0 | ✅ OK (criada) |
| bank_accounts | true | true | 1 | 0 | ✅ OK |
| credit_cards | true | true | 1 | 0 | ✅ OK |
| installments | true | true | 1 | 0 | ✅ OK |
| investments | true | true | 1 | 0 | ✅ OK |
| budgets | true | true | 1 | 0 | ✅ OK |
| financial_goals | true | true | 1 | 0 | ✅ OK |
| decisions | true | true | 1 | 0 | ✅ OK |
| category_memory | true | true | 1 | 0 | ✅ OK |

**Gap fechado.** As 10 tabelas financeiras estão com RLS user-scoped aplicada, `user_id
NOT NULL` e zero policies permissivas. Estado declarado = estado aplicado.
