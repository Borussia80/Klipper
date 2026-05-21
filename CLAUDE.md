# CLAUDE.md — Klipper Agent Memory
> Leia este arquivo PRIMEIRO em toda sessão.

---

## O QUE É O KLIPPER

App pessoal de gestão financeira de Roberto Milet.
Stack: Python · Streamlit Cloud · Supabase (PostgreSQL) · LiteLLM (multi-provider IA).

Nome: "Klipper" — referência aos Clipper ships. Transmite organização, velocidade e modernidade.

---

## ARQUITETURA

```
WikiAgent Financeiro v2.0
├── M1  Quant Engine       → core/m1_quant.py
├── M2  Governance         → core/m2_governance.py
├── M3  Context Layer      → core/m3_context.py
├── M4  AI Consilium       → pages/5_AI_Consilium.py (LiteLLM multi-provider)
├── Anti-BS Engine         → core/anti_bs.py
└── Fragility Score        → core/fragility.py
```

## ESTRUTURA DO REPO

```
app.py                     ← entrada Streamlit
core/                      ← engines WikiAgent + utilitários
models/                    ← modelos Pydantic (Transaction, Investment, Decision)
pages/                     ← páginas Streamlit (1_Dashboard ... 5_AI_Consilium)
migrations/                ← SQL Supabase
tests/                     ← pytest (cobertura ≥ 80%)
bot/                       ← Telegram Bot (Fase 6 — pendente)
```

## PROVEDORES IA (M4)

Ordem de preferência auto-routing:
1. Claude (Anthropic) — análise complexa
2. Gemini (Google) — contexto mercado (já usado no OTGN)
3. GPT-4o (OpenAI) — segunda opinião
4. Qwen / Kimi — custo reduzido

Configurar chaves em `.env`:
```
ANTHROPIC_API_KEY=
GOOGLE_API_KEY=
OPENAI_API_KEY=
DASHSCOPE_API_KEY=
MOONSHOT_API_KEY=
```

## BANCO DE DADOS

- Supabase PostgreSQL
- URL: https://obmudpulqzhwtcniyzcj.supabase.co
- Executar `migrations/001_initial_schema.sql` no SQL Editor do Supabase

## COMO EXECUTAR

```bash
cd /home/rmilet/Trabalho/Projetos/Klipper
pip install -e ".[dev]"
streamlit run app.py
```

## REGRAS DO AGENTE (do KB WikiAgent)

- Matemática ancora. Narrativa sem evidência não altera decisão.
- Contexto modula risco — nunca compra ativo.
- Declarar incerteza sempre.
- Sem verborreia.
- M2 Beginner Mode: max ativo 10% | max tese 25% | caixa mínimo 20%.

## PENDÊNCIAS (Fases futuras)

- [ ] Fase 6: Telegram Bot (`bot/bot.py`) — captura zero-fricção
- [ ] Adicionar API keys de IA no `.env`
- [ ] Deploy no Streamlit Cloud (repo: Borussia80/klipper)
- [ ] Adicionar autenticação (Supabase Auth) se uso não-pessoal

## LOG DE SESSÕES

```
2026-05-21 INIT  Projeto criado. Fases 0-5 implementadas.
                 Stack: Streamlit + Supabase + LiteLLM.
                 Engines M1/M2/M3/Anti-BS/Fragility implementados.
                 5 páginas Streamlit criadas.
                 CI GitHub Actions configurado.
                 Migration SQL gerada (pendente execução no Supabase).
```
