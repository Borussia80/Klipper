# CLAUDE-arch.md — Klipper · Arquitetura

---

## ESTRUTURA DO REPO

```
app.py                      ← entrada Streamlit (hero + briefing + WikiAgent)
core/                       ← engines + utilitários
  analytics.py              ← preparar_dados_donut_categorias, preparar_dados_barras_mensais
  anti_bs.py                ← Anti-BS Engine
  auth.py                   ← require_auth()
  circuit_breaker.py        ← máquina CLOSED/OPEN/HALF_OPEN
  financial_ai.py           ← Kira · NVIDIA NIM (Llama 3.3-70B)
  fragility.py              ← Fragility Score
  m1_quant.py               ← Quant Engine (DY, P/VP, score 0–1)
  m2_governance.py          ← hard limits: max ativo 10%, tese 25%, caixa 20%
  m3_context.py             ← Context Layer (regime de mercado)
  market_cache.py           ← Redis TTL + fakeredis in-memory
  market_data.py            ← B3, Tesouro Direto, PTAX, câmbio (yfinance + BCB)
  repositories.py           ← TransactionRepository, BankAccountRepository, …
  styles.py                 ← inject_css, kpi_card, action_card, CAT_COLORS, fmt_brl
models/
  transaction.py            ← Transaction, TransactionType (GANHO/GASTO), status
  investment.py             ← Investment
  bank_account.py           ← BankAccount
pages/
  1_Dashboard.py            ← KPIs + charts (Sprint 1 concluído)
  2_Transacoes.py           ← CRUD transações
  3_Investimentos.py        ← portfólio + modal ao vivo
  4_Kira.py                 ← IA financeira
  5_AI_Consilium.py         ← multi-provider LiteLLM
  6_Contas.py               ← contas + cartões + parcelas
  7_Orcamento.py            ← orçamento + score (referência de charts)
  8_Planejamento.py         ← planejamento financeiro
  9_Mercado.py              ← market data ao vivo
  10_Configuracoes.py       ← settings
  11_Extratos.py            ← importar PDF/PNG (Itaú + BTG)
migrations/
  001_initial_schema.sql
  002_v2_schema.sql
tests/                      ← pytest ≥ 466 testes, cobertura ≥ 80%
bot/                        ← Telegram Bot (Fase 6 — NÃO TOCAR)
```

---

## WIKIA GENT FINANCEIRO v2.0

| ID | Engine | Arquivo | Responsabilidade única |
|---|---|---|---|
| M1 | Quant Engine | `core/m1_quant.py` | Score 0–1 por ativo (DY, P/VP, liquidez, spread CDI) |
| M2 | Governance | `core/m2_governance.py` | Verifica hard limits. Não calcula scores. |
| M3 | Context Layer | `core/m3_context.py` | Regime de mercado. Modula prudência, não compra ativo. |
| M4 | AI Consilium | `pages/5_AI_Consilium.py` | Multi-provider via LiteLLM |
| AB | Anti-BS | `core/anti_bs.py` | Detecta narrativa sem evidência quantitativa |
| FR | Fragility | `core/fragility.py` | Resiliência: liquidez, concentração, correlação |
| KR | Kira | `core/financial_ai.py` | Constrói contexto financeiro + delega ao LLM |

---

## BANCO DE DADOS

- **Supabase PostgreSQL** — URL: `https://obmudpulqzhwtcniyzcj.supabase.co`
- Migrations em ordem: `001_initial_schema.sql` → `002_v2_schema.sql`
- Repositórios em `core/repositories.py`: `TransactionRepository`, `BankAccountRepository`
- Balance auto-adjustment: toda criação/edição/exclusão de transação chama `adjust_balance()`.

---

## PROVEDORES IA (M4 · LiteLLM auto-routing)

| Prioridade | Provider | Uso preferencial |
|---|---|---|
| 1 | Claude (Anthropic) | Análise complexa |
| 2 | Gemini (Google) | Contexto de mercado |
| 3 | GPT-4o (OpenAI) | Segunda opinião |
| 4 | Qwen / Kimi | Custo reduzido |
| 5 | NVIDIA NIM Llama 3.3-70B | Kira — inteligência pessoal |

Chaves em `.env`:
```
ANTHROPIC_API_KEY=
GOOGLE_API_KEY=
OPENAI_API_KEY=
DASHSCOPE_API_KEY=
MOONSHOT_API_KEY=
NVIDIA_API_KEY=
SUPABASE_URL=
SUPABASE_KEY=
REDIS_URL=          # opcional; sem ela usa fakeredis in-memory
```

---

## SRP — RESPONSABILIDADES CONSOLIDADAS

| Módulo | Responsabilidade única | O que ele NÃO faz |
|---|---|---|
| `market_cache.py` | Persistência e TTL de cotações | Não conhece tickers nem regras de negócio |
| `circuit_breaker.py` | Máquina de estados CLOSED/OPEN/HALF\_OPEN | Não conhece quais APIs protege |
| `market_data.py` | Orquestra fontes e cache | Não implementa HTTP nem lógica de TTL |
| `financial_ai.py` | Constrói contexto + delega ao LLM | Não conhece Streamlit nem repositórios |
| `m2_governance.py` | Verifica limites M2 | Não calcula scores M1, não acessa banco |
| `analytics.py` | Prepara dados para charts | Não renderiza, não acessa Streamlit |

---

## VERSIONAMENTO

`X.Y.Z` — X: mudança arquitetural · Y: nova feature · Z: correção/refactoring interno
