# Política de Escrita — Klipper

**Criado:** 2026-06-14 · **Fase:** 1.1 — Fonte Única de Verdade
**Decisão:** 2026-06-14 — abordagem **Pragmática** (ver §1). Stack: **PWA (Vercel) + API (Railway)**.
Streamlit removido do projeto.

---

## 1. Princípio (Pragmático)

> **Escrita com regra de negócio → FastAPI Gateway.**
> **CRUD simples → `supabase-js` direto** (já é multiusuário-correto via RLS).

Por que não rotear *tudo* pelo gateway: o caminho `supabase-js` (anon key) já é seguro —
a RLS isola por `user_id` e o `DEFAULT auth.uid()` preenche o dono no INSERT. Rotear CRUD
puro pelo gateway (service_role) **removeria** essa rede de segurança (exigiria plumbing
manual de `user_id` em modelos/repos compartilhados) e adicionaria latência, sem ganho real
enquanto não há regra de negócio. O gateway entra **onde há matemática/consistência**:
categorização, parcelamento, rateio, saldo, memória, auditoria, engines.

## 2. Tabela de decisão

| Operação | Canal | Justificativa |
|---|---|---|
| Transações (create) | **Gateway** | Categorização, parcelamento, rateio, saldo, memória |
| Parcelas / Splits | **Gateway** | Geração automática + consistência da soma |
| Decisões (auditoria) | **Gateway** | Trilha imutável |
| Engines M1/M2/M3 / fragility | **Gateway** | Lógica em `core/` |
| Investimentos (CRUD) | **supabase-js** | CRUD simples; RLS cuida do `user_id`. Migrar ao gateway só quando os engines escreverem |
| Orçamentos (upsert) | **supabase-js** | CRUD simples; cálculo (burn-rate/alertas) é **leitura** via `/budget/*` |
| Contas / Cartões (CRUD) | **supabase-js** | CRUD simples + soft delete (`is_active=false`) |
| Transações (update/delete) | **supabase-js** (hoje) | Revisitar: se precisar recalcular saldo no servidor → mover ao gateway |
| Leitura (SELECT) de qualquer dado | **supabase-js** | Sem mutação; RLS protege |
| Perfil / config / tema | **supabase-js** | Apresentação, sem regra |

## 3. Regras operacionais

- **Anon key (PWA):** sujeita a RLS. `DEFAULT auth.uid()` preenche `user_id` no INSERT.
- **Service_role (api/ FastAPI):** **bypassa RLS** → todo INSERT no gateway deve setar
  `user_id` explícito. Ver `docs/security/rls_audit.md` §4.
- **Gateway = `${NEXT_PUBLIC_API_URL}`** com `Authorization: Bearer <jwt>`.
- **Unicidade é por usuário** (migration 008): `UNIQUE (user_id, …)`. Upserts no front
  devem usar `onConflict` com `user_id` (ex.: `useBudgets` → `user_id,category,year,month`).

## 4. Correção multiusuário aplicada (estabilização)

A auditoria (2026-06-14) achou constraints UNIQUE **globais** — bug latente: dois usuários
não poderiam ter o mesmo ticker / orçamento de categoria / meta. Corrigido em
**`migrations/008_user_scoped_unique.sql`**:

| Tabela | Antes | Depois |
|---|---|---|
| investments | `UNIQUE (ticker)` | `UNIQUE (user_id, ticker)` |
| budgets | `UNIQUE (category, year, month)` | `UNIQUE (user_id, category, year, month)` |
| financial_goals | `UNIQUE (year, month)` | `UNIQUE (user_id, year, month)` |

Coordenação de front: `web/lib/queries/useBudgets.ts` agora usa
`onConflict: "user_id,category,year,month"`.

> **Ordem de aplicação:** rodar a 008 no SQL Editor **antes** de subir o frontend novo
> (o `onConflict` referencia a constraint nova). Migrations são manuais — ver
> [verificação] em `docs/security/`.

## 5. Estado de conformidade

- **Escritas com regra de negócio** (transações/parcelas/splits/engines): via gateway ✅
- **CRUD simples** (investimentos/orçamentos/contas/cartões): supabase-js + RLS ✅ (aceito)
- **Bug UNIQUE multiusuário:** corrigido na 008 (aplicar no banco) ✅
- **Streamlit:** removido do projeto ✅
