# Auditoria Multi-Tenant — Klipper

**Data:** 2026-06-14 · **Fase:** 0.4 (P0, após auditoria de RLS)
**Pergunta central:** o `user_id` se propaga corretamente por toda a cadeia
`JWT → FastAPI → Repository → Banco`?

---

## 0. Veredito

| Elo da cadeia | Status |
|---|---|
| JWT → FastAPI | ✅ `CurrentUser` (`api/auth.py`) extrai `user_id` do JWT |
| FastAPI → Repository | ❌ **quebrado** — repos não recebem nem propagam `user_id` |
| Repository → Banco | ❌ **quebrado** — repos escrevem sem `user_id` (modelos não têm o campo) |
| Banco (RLS/DEFAULT) | ✅ 10 tabelas com `user_id NOT NULL DEFAULT auth.uid()` (aplicado — ver `rls_audit.md`) |

**Conclusão:** a camada de banco está pronta; a **camada de aplicação não**. O único
caminho de escrita hoje multi-tenant-correto é o **gateway de transações** (que **contorna
o repositório** e monta as rows à mão com `user_id` explícito) e o **PWA via supabase-js**
(anon key → `DEFAULT auth.uid()` preenche). Tudo que passa pelos **métodos de escrita dos
repositórios** está quebrado para multi-tenant.

> **Regra P0 (aceita):** nenhuma mutation migra para o gateway enquanto `user_id` não
> estiver propagado de ponta a ponta. Esta auditoria mapeia exatamente o que falta.

## 1. Cliente Supabase

`core/database.py::get_client()` usa **`SUPABASE_KEY` = service_role** → **bypassa RLS** e
faz **`auth.uid()` retornar NULL**. Consequência: no caminho server-side, o `DEFAULT
auth.uid()` **não** preenche `user_id` — o INSERT precisa trazê-lo **explícito**, ou falha
no `NOT NULL`.

## 2. Tabelas: `user_id` + `DEFAULT auth.uid()`

Todas as 10 tabelas financeiras: `user_id UUID NOT NULL DEFAULT auth.uid()`, RLS user-scoped,
**verificado aplicado** em 2026-06-14 (`rls_audit.md` §7). ✅

## 3. Modelos Pydantic: têm campo `user_id`?

| Modelo | `user_id`? |
|---|---|
| `transaction.py` (Transaction) | ❌ não |
| `transaction_split.py` | ❌ não |
| `bank_account.py` | ❌ não |
| `credit_card.py` | ❌ não |
| `installment.py` | ❌ não |
| `investment.py` | ❌ não |
| `budget.py` | ❌ não |
| `decision.py` | ❌ não |

**8/8 modelos sem `user_id`.** Logo qualquer repo que faça `model.model_dump()` insere
**sem** `user_id` → quebra sob service_role.

## 4. Repositórios: métodos de escrita

| Repo.método | Seta `user_id`? | Chamador hoje | Status |
|---|---|---|---|
| `TransactionRepository.create` | ❌ (`model_dump`) | — (gateway monta row à mão) | órfão p/ escrita |
| `TransactionRepository.update` | ❌ | — | órfão |
| `InvestmentRepository.upsert` | ❌ (`on_conflict="ticker"`) | — (PWA usa supabase-js) | órfão |
| `InvestmentRepository.delete` | n/a | — | órfão |
| `DecisionRepository.create/update` | ❌ | — | órfão |
| `BankAccountRepository.create` | ❌ | — (PWA supabase-js) | órfão |
| `CreditCardRepository.create` | ❌ | — | órfão |
| `InstallmentRepository.create` | ❌ | — (gateway monta à mão) | órfão |
| `BudgetRepository.upsert` | ❌ | — (PWA supabase-js) | órfão |
| **`CategoryMemoryRepository.remember`** | ❌ **+ queries sem filtro `user_id`** | **`api/category.py` + `api/routers/transactions.py`** | 🔴 **VIVO e QUEBRADO** |

### 4.1 🔴 P0 — `CategoryMemoryRepository`

Único método de escrita de repo ainda **vivo** (chamado pelo gateway). Defeitos:

1. **INSERT de padrão novo sem `user_id`** → service_role → `auth.uid()`=NULL → viola
   `NOT NULL` → **falha** (engolida pelo try/except "best-effort"). Resultado:
   **aprender categoria de estabelecimento novo não persiste em produção.**
2. **SELECT/UPDATE sem filtro `user_id`** → sob service_role (RLS bypassada) enxerga linhas
   de **todos** os usuários (hoje inócuo: 1 usuário; multi-tenant: vazamento + corrupção).

O próprio código admite o débito: *"App é single-user… se virar multi-tenant, trocar por RPC."*

**Correção:** `remember(description, category, user_id)` e `load_history(user_id)` recebendo
`user_id` do `CurrentUser`, com `.eq("user_id", user_id)` em todas as queries e `user_id` no
INSERT. (Há `tests/test_category_memory.py` para cobrir a mudança.)

> ✅ **CORRIGIDO 2026-06-14.** `user_id` agora obrigatório (guard `ValueError` antes de
> qualquer I/O) em `remember`/`load_history`/`categorize_with_memory`/`confirm_transaction`;
> filtro `.eq("user_id", …)` em todo SELECT/UPDATE; `user_id` no INSERT. Callers atualizados:
> `category.py`, `transactions.py`, `statement.py` (todos threadam o `CurrentUser`). Testes de
> isolamento entre 2 usuários adicionados — suíte 738 verde.

### 4.2 Métodos órfãos (pós-remoção do Streamlit)

Os demais métodos de escrita só eram chamados pelas `pages/` Streamlit (removidas). Hoje
**não têm chamador**. Antes de ressuscitar qualquer um deles num endpoint do gateway, aplicar
o pré-requisito da §5.

## 5. Pré-requisito para migrar QUALQUER escrita ao gateway (checklist P0)

Por domínio, antes de criar um endpoint de escrita no gateway:

- [ ] Modelo Pydantic ganha campo `user_id: str` (ou o endpoint injeta na row, como faz hoje
      o `transactions.py`).
- [ ] Método do repo recebe `user_id` explícito e o grava (não confiar em `DEFAULT auth.uid()`
      sob service_role).
- [ ] Toda query de leitura/seleção do repo filtra por `user_id`.
- [ ] Teste de integração **sem mock de core/** prova que a row gravada tem o `user_id` do JWT
      e que outro usuário não a enxerga.

## 6. Caminhos de escrita HOJE — classificação

| Caminho | Multi-tenant? | Observação |
|---|---|---|
| Gateway `POST /transactions` | ✅ correto | monta rows à mão com `user_id` do JWT; **contorna** os repos |
| `CategoryMemoryRepository.remember` (gateway) | ✅ corrigido (2026-06-14) | §4.1 |
| PWA `supabase-js` (anon key) p/ CRUD simples | ✅ correto | RLS + `DEFAULT auth.uid()` |
| Métodos de escrita dos repos (genérico) | ❌ inseguro | órfãos; não usar sem §5 |

## 7. Remediação priorizada

1. **P0 — ✅ FEITO (2026-06-14):** `CategoryMemoryRepository` corrigido (`user_id` explícito +
   filtros + guard + testes de isolamento).
2. **P1 —** ao gateway-ificar um domínio (write-policy §2), seguir o checklist §5; preferir
   o padrão do `transactions.py` (row à mão com `user_id`) ou adicionar `user_id` aos modelos.
3. **P2 —** decidir o destino dos métodos de escrita órfãos dos repos: remover (dead code) ou
   adequar à §5 quando forem reusados.

> Constraints (UNIQUE/PK/FK/INDEX) por usuário: ver `docs/security/constraints_audit.md` (Fase 0.5).
