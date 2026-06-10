# CLAUDE-pwa.md — Klipper PWA · Roadmap de Codificação
> Guia para sessões Claude Code (Sonnet 4.6) implementarem a migração Streamlit → PWA.
> Leia o `CLAUDE.md` primeiro. Este arquivo é a fonte de verdade da migração —
> **as decisões abaixo já foram tomadas; não reabrir debates de stack ou design.**

---

## VISÃO

Substituir a UI Streamlit por um **PWA instalável** (desktop Fedora/KDE, Android, iOS),
mantendo TODO o `core/` Python intacto. O Streamlit atual continua em produção
até a Fase 4 — as duas UIs falam com o mesmo Supabase.

```
┌─ web/  (Next.js PWA) ─────────── Vercel
│    ├── CRUD direto → supabase-js (transações, contas, orçamento, saúde)
│    └── fetch → api/ para o que é Python
│
├─ api/  (FastAPI fino) ────────── Railway (railway.toml já existe)
│    └── importa core/ SEM mudanças: OCR extratos, market_data,
│        engines M1/M2/M3, Kira (NVIDIA NIM)
│
└─ Supabase ── já existe: Postgres + Auth + RLS
```

**Estrutura: monorepo.** `web/` e `api/` são pastas novas neste repositório.
`core/`, `models/`, `tests/` permanecem onde estão e são compartilhados pela `api/`.

---

## REGRAS INEGOCIÁVEIS

1. **`core/` não se reescreve.** Nenhuma lógica de negócio (engines, parsers,
   matemática financeira) é portada para TypeScript. Se a UI precisa de um cálculo,
   a `api/` expõe um endpoint que chama o `core/`.
2. **Código sem teste não entra** (Regra de Ouro do CLAUDE.md). Web: Vitest +
   Testing Library. API: pytest (mesma suite, mesmo padrão dos 820 testes atuais).
3. **Não tocar no app Streamlit** (`app.py`, `pages/`) durante as Fases 0–3.
   Ele é a produção. Exceção: hotfix crítico pedido pelo Roberto.
4. **Nunca commitar credenciais.** Supabase keys via `.env.local` (web) e
   variáveis Railway (api). Manter `.env*` no `.gitignore`.
5. **Todo texto vindo do banco é escapado/sanitizado na renderização.**
   Lição do audit 2026-06: descrições de transação vêm de OCR de extratos
   (entrada externa). React escapa por padrão — **nunca** usar
   `dangerouslySetInnerHTML` com dados do banco.
6. **Uma fase por sessão.** Ao final, atualizar a seção `## ESTADO` deste arquivo
   e commitar com mensagem `feat(pwa): Fase N — descrição`.

---

## STACK (decidido — não reabrir)

| Camada | Escolha | Notas |
|---|---|---|
| Framework | **Next.js 15+ (App Router)** | React Server Components onde fizer sentido |
| Estilo | **Tailwind CSS v4** | tokens via CSS vars (ver Design System abaixo) |
| Componentes | **shadcn/ui** | copiar para `web/components/ui/`, customizar com tokens |
| Dados | **supabase-js v2** + **TanStack Query v5** | cache, optimistic updates |
| Formulários | **react-hook-form + zod** | validação espelhando os models Pydantic |
| Charts | **Recharts** (via shadcn/charts) | um único theme — sem layouts ad-hoc |
| PWA | **Serwist** | manifest + service worker + offline shell |
| Tema | **next-themes** | dark default, light opcional |
| Auth | **Supabase Auth** | email+senha + **MFA TOTP** (paridade com auth atual) |
| API Python | **FastAPI + uvicorn** | `api/main.py`, routers finos sobre `core/` |
| Testes web | **Vitest + @testing-library/react** | |
| Deploy | **Vercel** (web) + **Railway** (api) | Supabase permanece como está |

Moeda/datas: `Intl.NumberFormat('pt-BR', {currency:'BRL'})` — não reimplementar `fmt_brl`.

---

## DESIGN SYSTEM — tokens portados + correções do audit

Portar de `core/styles.py` com as correções abaixo. Definir em
`web/app/globals.css` como CSS vars consumidas pelo Tailwind.

### Cores (dark — default)

```css
--bg:        #020617;   --card:      #0D1726;
--surface:   #07111D;   --layer:     #132238;
--ink:       #F1F5F9;   --ink-2:     #CBD5E1;
--ink-3:     #94A3B8;   --ink-4:     #64748B;  /* corrigido: era #475569, falhava AA */
--rule:      rgba(255,255,255,0.07);
--brass:     #D9B26F;   /* ÚNICO acento de marca */
--pos:       #10B981;   /* entradas, sucesso */
--neg:       #F87171;   /* SOMENTE alertas/estouro — não para gastos normais */
--warn:      #F59E0B;
```

### Decisões de design (encerram as inconsistências do audit 2026-06)

1. **Gastos são neutros** (`--ink`), entradas são verdes (`--pos`), vermelho é
   reservado para alerta real (orçamento estourado, saldo negativo, violação M2).
   Fim da ambiguidade azul/vermelho do Streamlit.
2. **Um acento só**: brass. As cores `sea/electric/copper/moss/lantern` do tema
   antigo **não migram**. Charts usam paleta categórica própria do theme Recharts.
3. **Calm UI**: sem glow ambiente, sem gradiente animado, sem backdrop-blur
   decorativo. Elevação por borda 1px + sombra sutil. Hierarquia por tipografia
   e espaço, não por efeito.
4. **Tipografia**: Geist Sans (UI) + Geist Mono (números, `tabular-nums`).
   Serif **não migra**. Base 14px, escala fluida com `clamp()` no hero.
5. **A11y desde o início**: `:focus-visible` em tudo, `prefers-reduced-motion`
   respeitado, touch targets ≥44px, contraste AA mínimo (4.5:1 texto normal).
6. **Mobile-first**: bottom tab bar fixa (5 destinos: Home, Transações, ＋ FAB
   central, Investimentos, Mais) + FAB de lançamento rápido. Desktop: sidebar.

---

## FASES

### ✅ Pré-requisito — decisões tomadas (este documento)

### Fase 0 — Segurança Supabase (RLS + Auth) · 1 sessão
> Hoje o Streamlit acessa via anon key (confirmado: role=anon no JWT). Browser
> falando direto com o banco exige RLS. **Bloqueia todas as fases seguintes.**

- [x] Auditar schema: 11 tabelas mapeadas, nenhuma tem `user_id` ainda
- [x] Migration 005a: `user_id` nullable adicionada a todas as tabelas
      (`migrations/005a_add_user_id_columns.sql`)
- [x] Migration 005b: backfill + NOT NULL + policies user-scoped
      (`migrations/005b_rls_user_policies.sql`) — **aguarda execução manual**
- [ ] Criar usuário no Supabase Auth (roberto.milet@gmail.com) e habilitar MFA TOTP
- [ ] **Atualizar SUPABASE_KEY no Streamlit Cloud para service_role key**
      (SUPABASE_KEY atual é anon — quebraria após 005b sem esta troca)
- [ ] Executar 005a → 005b no SQL Editor do Supabase
- [ ] Rodar `python scripts/verify_rls.py` e confirmar ✅
- [ ] Verificar Streamlit prod intacto após as mudanças
- **Aceite:** anon key sem sessão = zero linhas; com sessão = dados completos;
  Streamlit prod intacto.

### Fase 1 — Scaffold PWA + Design System + Shell · 1–2 sessões

- [x] `web/`: `create-next-app` (TypeScript, App Router, Tailwind) — Next.js 16 + React 19
- [x] `globals.css` com os tokens do design system; dark default
- [x] Componentes base com testes (16 testes passando):
      `KCard`, `KpiCard`, `TxRow`, `EmptyState`, `PageHeader`
- [x] Layout shell: `Sidebar` desktop + `BottomBar` mobile + FAB central
- [x] `manifest.json` PWA (nome, ícones, display standalone, theme #020617)
- [x] `types/database.ts` — tipos TypeScript do schema Supabase (manual, antes do gen)
- [x] `lib/utils.ts` — `fmtBRL`, `fmtPct`, `fmtDate`, `cn`
- [x] `lib/supabase.ts` — client com tipos genéricos
- [x] Vitest + Testing Library configurados (`npm test`)
- [x] Auth: `app/login/page.tsx` — login email+senha + desafio TOTP 2 steps
- [x] `proxy.ts` (Next.js 16) — protege rotas, redireciona /login se sem sessão
- [x] Serwist service worker (`app/sw.ts`) — precache shell + network-first
- [x] `vercel.json` — pronto para `git push` → deploy automático no Vercel
- [ ] Deploy inicial no Vercel + teste de instalação em 1 desktop + 1 Android
      **Ação Roberto: criar projeto Vercel vinculando github.com/Borussia80/Klipper,
      pasta `web/`, e adicionar vars NEXT_PUBLIC_SUPABASE_URL + ANON_KEY**
- **Aceite:** app instala como PWA no KDE e no Android, login com TOTP funciona,
  shell navega entre rotas vazias.

### Fase 2 — Páginas CRUD (supabase-js direto) · 2–3 sessões

Ordem: **Transações → Dashboard → Contas → Orçamento → Saúde**.

- [ ] Tipos TypeScript gerados do schema: `supabase gen types typescript`
- [ ] **Transações**: lista com filtros (mês, categoria, tipo, busca), lançamento
      rápido via dialog (FAB), edição, exclusão com confirmação,
      **optimistic update** via TanStack Query
- [ ] **Dashboard**: KPIs do mês, donut categorias, barras entradas×saídas 6m
      (Recharts), últimas transações — paridade com `pages/1_Dashboard.py`
- [ ] **Contas**: cards de conta/cartão, ajuste de saldo, transferência
      (replicar a lógica dupla-transação de `core/modals.py::modal_transfer`)
- [ ] **Orçamento**: limites por categoria, barras de progresso, alerta de estouro
      (vermelho SÓ aqui — ver decisão de design 1)
- [ ] **Saúde**: profissionais, sessões, reembolsos (paridade `pages/10_Saude.py`)
- [ ] Skeleton loading em toda lista/card (sem spinners)
- [ ] Testes por página: render, mutação otimista, caso de erro
- **Aceite:** uso diário completo (lançar, editar, conferir) possível só no PWA.
  Saldo ajustado corretamente ao criar/editar/excluir transação (regra
  `tx_balance_delta` — validar contra os testes Python existentes).

### Fase 3 — API Python (FastAPI sobre core/) · 2 sessões

- [ ] `api/`: FastAPI + routers; auth via verificação do JWT do Supabase
      (`Authorization: Bearer` do PWA)
- [ ] Endpoints:
      - `GET  /quotes/{ticker}` e `GET /benchmarks` → `core/market_data.py`
      - `POST /import/statement` (upload PDF/PNG) → `core/statement_reader.py`,
        retorna transações parseadas para revisão no PWA antes de salvar
      - `GET  /engines/m1/{ticker}` · `GET /engines/governance` ·
        `GET /engines/fragility` → `core/m1_quant.py`, `m2_governance.py`, `fragility.py`
      - `POST /kira/chat` → `core/financial_ai.py` (streaming SSE)
- [ ] Páginas PWA: **Investimentos** (posições ao vivo, alocação, rendimentos),
      **Importar** (upload → revisão → confirmação em lote), **Kira** (chat)
- [ ] Deploy Railway; CORS restrito ao domínio Vercel
- [ ] Testes: pytest dos routers (mock do core onde há rede), Vitest das páginas
- **Aceite:** importar um extrato real Itaú/BTG pelo PWA; cotações ao vivo;
  chat Kira com streaming.

### Fase 4 — Cutover · 1 sessão

- [ ] Checklist de paridade página a página vs Streamlit
- [ ] Uso paralelo por 1–2 semanas (Roberto valida no dia a dia)
- [ ] Apontar domínio/atalhos para o PWA; Streamlit vira fallback read-only
      ou é desligado (decisão do Roberto na hora)
- [ ] Atualizar `CLAUDE.md` e `README.md` com a nova arquitetura
- **Aceite:** 100% do uso diário no PWA por 1 semana sem recorrer ao Streamlit.

---

## PROTOCOLO DE SESSÃO

1. Ler `CLAUDE.md` → este arquivo → seção `## ESTADO` abaixo
2. Executar a fase (ou sub-bloco) indicada como próxima
3. TDD: Red → Green → Refactor; rodar a suite antes do commit
4. Commit atômico `feat(pwa): Fase N — …`; **não** fazer push sem pedir
5. Atualizar `## ESTADO` com: o que foi feito, decisões novas, pendências

### Comandos

```bash
# web
cd web && npm run dev          # localhost:3000
npm run test                   # vitest
npm run build                  # validar build de produção

# api
cd api && uvicorn main:app --reload --port 8000
python -m pytest tests/ -q --tb=short   # suite completa (raiz do repo)
```

---

## ESTADO

> Atualizar ao final de cada sessão.

**Última atualização:** 2026-06-10
**Fase atual:** Fase 0 (passos manuais pendentes) + Fase 1 scaffold iniciado
**Próxima ação:** Roberto executa os 3 passos manuais da Fase 0 → verificar RLS → Fase 1 continua

**Decisões registradas:**
- 2026-06-10 · Stack fechado (Next.js + shadcn/ui + Supabase + FastAPI) — ver tabela
- 2026-06-10 · Gastos neutros / verde entradas / vermelho só alerta
- 2026-06-10 · Monorepo: `web/` + `api/` neste repositório
- 2026-06-10 · Serif e cores secundárias do tema náutico não migram
- 2026-06-10 · **SUPABASE_KEY atual é anon key** — Streamlit Cloud DEVE ser atualizado
  para service_role key ANTES de 005b ser aplicado, senão o Streamlit perde dados.
  Arquitetura definitiva: Streamlit/Railway = service_role; PWA browser = anon key.

**Fase 0 — Passos manuais pendentes (executar nesta ordem):**

1. **Supabase Auth Dashboard** → Authentication → Users → Add user  
   `roberto.milet@gmail.com` + senha forte + "Auto Confirm"  
   Copiar o UUID gerado (ex: `xxxxxxxx-xxxx-…`)

2. **Supabase Auth Dashboard** → Authentication → Policies → MFA  
   Habilitar TOTP (ou fazer enrollment pelo próprio app Streamlit após login)

3. **Supabase SQL Editor** → executar `migrations/005a_add_user_id_columns.sql`  
   *(seguro; não altera policies)*

4. **Streamlit Cloud** → Settings → Secrets → atualizar `SUPABASE_KEY` para a  
   **service_role key** (Settings → API no painel Supabase)  
   Confirmar que o Streamlit continua carregando dados.

5. **Supabase SQL Editor** → executar `migrations/005b_rls_user_policies.sql`  
   *(faz backfill, NOT NULL, troca policies)*

6. **Local** → adicionar `SUPABASE_SERVICE_KEY=<service_role_key>` ao `.env`  
   e rodar: `python scripts/verify_rls.py`  
   → Deve imprimir: `✅ PASSOU — anon key bloqueada corretamente`

7. Confirmar que o Streamlit ainda funciona em produção (login + dados visíveis)

**Aceite Fase 0:** verify_rls.py passa + Streamlit prod intacto + MFA TOTP configurado

**Pendências abertas:**
- ⏳ Passos manuais acima (Roberto executa no painel Supabase + Streamlit Cloud)
- Gerar ícones PWA (192/512/maskable) a partir do brand existente em
  `design_handoff_klipper/`
