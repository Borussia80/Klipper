# CLAUDE.md — Klipper Agent Memory
> Leia este arquivo PRIMEIRO em toda sessão. As seções de processo são obrigações técnicas, não sugestões.

---

## O QUE É O KLIPPER

App pessoal de gestão financeira de Roberto Milet.
Stack: Python · Streamlit Cloud · Supabase (PostgreSQL) · LiteLLM (multi-provider IA) · NVIDIA NIM.

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
├── Fragility Score        → core/fragility.py
├── Kira · IA Financeira   → core/financial_ai.py  (NVIDIA NIM)
└── Market Data            → core/market_data.py   (B3 · Tesouro · PTAX · câmbio)
```

## ESTRUTURA DO REPO

```
app.py                     ← entrada Streamlit
core/                      ← engines WikiAgent + utilitários
  market_data.py           ← cotações B3, Tesouro, câmbio (yfinance + BCB)
  market_cache.py          ← Redis (TTL) + fallback in-memory (fakeredis)
  circuit_breaker.py       ← CLOSED/OPEN/HALF_OPEN para APIs instáveis
  financial_ai.py          ← inteligência financeira NVIDIA NIM (Kira)
models/                    ← Pydantic (Transaction, Investment, BankAccount…)
pages/                     ← páginas Streamlit (1_Dashboard … 11_Extratos)
migrations/                ← SQL Supabase
tests/                     ← pytest ≥ 269 testes, cobertura ≥ 80%
bot/                       ← Telegram Bot (Fase 6 — pendente)
```

## PROVEDORES IA (M4)

Ordem de preferência auto-routing:
1. Claude (Anthropic) — análise complexa
2. Gemini (Google) — contexto mercado
3. GPT-4o (OpenAI) — segunda opinião
4. Qwen / Kimi — custo reduzido
5. NVIDIA NIM (`meta/llama-3.3-70b-instruct`) — Kira, inteligência financeira pessoal

Configurar chaves em `.env`:
```
ANTHROPIC_API_KEY=
GOOGLE_API_KEY=
OPENAI_API_KEY=
DASHSCOPE_API_KEY=
MOONSHOT_API_KEY=
NVIDIA_API_KEY=
REDIS_URL=          # opcional; sem ela usa fakeredis in-memory
```

## BANCO DE DADOS

- Supabase PostgreSQL · URL: https://obmudpulqzhwtcniyzcj.supabase.co
- Executar migrations em ordem: `001_initial_schema.sql` → `002_v2_schema.sql`

## PRODUÇÃO

URL: https://klipper.streamlit.app/
GitHub: https://github.com/Borussia80/Klipper

## COMO EXECUTAR (local)

```bash
cd /home/rmilet/Trabalho/Projetos/Klipper
export PATH="$HOME/.local/bin:$PATH"
streamlit run app.py
```

## COMO RODAR OS TESTES

```bash
python -m pytest tests/ -v            # suite completa
python -m pytest tests/ -q --tb=short # saída compacta
```

---

## PROCESSO DE DESENVOLVIMENTO — OBRIGAÇÕES TÉCNICAS

Esta seção descreve o único processo aceito neste repositório. Não são sugestões.

### TDD — Test-Driven Development

TDD não é filosofia de projeto. É a definição operacional de "código pronto".

**O ciclo obrigatório:**

```
① Red   — escreva o teste que descreve o comportamento. Ele deve falhar.
② Green — escreva o mínimo de código para o teste passar. Exatamente o mínimo.
③ Refactor — melhore o design. Nenhum teste pode quebrar.
```

Regras derivadas:
- Código sem teste correspondente não é aceito em nenhuma função pública.
- O teste é escrito **antes** do código que ele valida. Sempre.
- Um teste escrito após o código não é TDD; é auditoria post-mortem e não conta.
- Se não existe teste para um bug, o primeiro passo é escrever o teste que reproduz o bug — só então corrigi-lo.

---

### F.I.R.S.T. — Robert C. Martin

Todo teste escrito neste projeto satisfaz as cinco propriedades. Violações são corrigidas antes de qualquer outra coisa.

**F — Fast**
A suite completa executa em menos de 10 segundos. Testes que dependem de I/O de rede real (yfinance, BCB, Supabase) são sempre mockados. Testes de integração contra infraestrutura real são marcados `@pytest.mark.slow` e não bloqueiam o ciclo local.

**I — Independent**
Nenhum teste depende de estado deixado por outro. A ordem de execução do pytest não pode alterar o resultado de nenhum teste. Fixtures `autouse` isolam `st.session_state`, cache Redis (`fakeredis` dedicado por fixture), circuit breakers (`cb.reset()` no setup) e repositórios (dados sintéticos, nunca banco real).

**R — Repeatable**
O mesmo resultado em qualquer máquina, em qualquer momento do dia, sem acesso à internet. Datas relativas (`date.today()`) em testes são substituídas por datas absolutas futuras (ex.: `date(2030, 1, 1)`). APIs externas são sempre substituídas por `unittest.mock.patch` ou `MagicMock`.

**S — Self-Validating**
O teste passa ou falha — sem inspeção manual de stdout, log ou banco de dados. `assert` com mensagem clara é obrigatório. Um teste que "precisa ser lido para saber se passou" é reescrito. `print()` dentro de teste é proibido.

**T — Timely**
O teste é escrito antes do código de produção. Isso não é opcional — é o que separa TDD de "escrever testes depois". O timing é a propriedade mais frequentemente violada e a mais importante de preservar.

---

### Single Responsibility Principle (SRP)

Cada módulo, classe e função tem **exatamente um motivo para mudar**. Quando um módulo acumula uma segunda responsabilidade, ele é dividido imediatamente — não na próxima sprint, não "quando houver tempo".

**Como aplicar a heurística:**
- Se o nome do módulo contém "e" ou "ou" (`processa_e_salva`, `valida_ou_formata`), ele tem responsabilidade dupla.
- Se uma função ultrapassa ~25 linhas, questione se ela pode ser dividida. Acima de 40 linhas, divida.
- Se adicionar uma feature exige modificar uma classe que "não devia precisar mudar", a responsabilidade está errada.

**Exemplos concretos já aplicados:**

| Módulo | Responsabilidade única |
|--------|------------------------|
| `core/market_cache.py` | Persistência e TTL de cotações. Não conhece tickers nem regras de negócio. |
| `core/circuit_breaker.py` | Máquina de estados CLOSED/OPEN/HALF_OPEN. Não conhece quais APIs protege. |
| `core/market_data.py` | Orquestra fontes e cache. Não implementa protocolo HTTP nem lógica de TTL. |
| `core/financial_ai.py` | Constrói contexto financeiro e delega ao LLM. Não conhece Streamlit. |
| `core/m2_governance.py` | Verifica limites M2. Não calcula scores M1 nem acessa banco. |

---

### Práticas XP

#### Pair Programming
Toda sessão de desenvolvimento com o agente Claude Code é pair programming assistido por IA. O humano (Roberto) define **o quê** e **por quê**; o agente executa, questiona e propõe. O humano revisa cada diff antes de aceitar. O agente não faz commit sem aprovação explícita.

#### Integração Contínua (CI)
GitHub Actions executa em todo push para qualquer branch:
```
Ruff (lint) → mypy (tipos) → pytest (testes) → cobertura ≥ 80%
```
Nenhum merge acontece com CI vermelho. "Vou corrigir depois do merge" não é uma frase que existe neste repositório.

#### Test-First (Testes antes do código)
A sequência é invariável e não admite exceção:

1. Entender o requisito com precisão suficiente para descrever o comportamento esperado
2. Escrever o teste que falha (Red)
3. Escrever o código mínimo (Green)
4. Refatorar (Refactor)
5. Repetir

Features sem teste de aceitação correspondente não são iniciadas.

#### Refactoring contínuo
Refatoração não é evento separado com data marcada. Acontece no passo **Refactor** de cada ciclo TDD. A regra da escotagem: o código sai mais limpo do que entrou — dentro do escopo da mudança em curso. Fora do escopo, abre-se uma issue separada.

Sinais que disparam refactoring imediato:
- Duplicação de lógica (violação DRY)
- Função acima de ~25 linhas
- Classe com mais de uma responsabilidade (violação SRP)
- Teste que depende de outro teste (violação F.I.R.S.T.-I)
- Nome que precisa de comentário para ser entendido

#### Feedback curto
O tempo entre "escrever código" e "saber se funciona" é minimizado em todas as camadas:

| Camada | Meta |
|--------|------|
| Suite local (pytest) | < 10 s |
| CI completo (Actions) | < 3 min |
| Review de PR | mesmo dia útil |
| Deploy em produção | automático após merge em `main` (Streamlit Cloud) |

Qualquer aumento nessas janelas é tratado como defeito de processo, não como aceitável.

---

## REGRAS DO AGENTE (do KB WikiAgent)

- Matemática ancora. Narrativa sem evidência não altera decisão.
- Contexto modula risco — nunca compra ativo.
- Declarar incerteza sempre.
- Sem verborreia.
- M2 Beginner Mode: max ativo 10% | max tese 25% | caixa mínimo 20%.

---

## VERSIONAMENTO

Esquema X.Y.Z:
- X = grande mudança arquitetural
- Y = nova feature ou bug com impacto perceptível
- Z = correção pequena ou refactoring interno

---

## PENDÊNCIAS (Fases futuras)

- [ ] Fase 6: Telegram Bot (`bot/bot.py`) — captura zero-fricção
- [ ] Adicionar API keys de IA no `.env`
- [ ] Página de Cotações usando `MarketDataService`

## LOG DE SESSÕES

```
2026-05-22 FEAT  Market data: B3, Tesouro Direto, PTAX, câmbio.
                 Cache Redis + fakeredis. Circuit breaker CLOSED/OPEN/HALF_OPEN.
                 63 novos testes. Total: 269 testes.
2026-05-22 FEAT  Kira — IA financeira NVIDIA NIM (financial_ai.py).
                 Dashboard briefing widget + sidebar Q&A em todas as páginas.
2026-05-22 FEAT  Simplifi layout: Spending Plan hero, category badges, accounts rail.
                 TOTP modal synergy fix. XSS + CSS injection hardening.
2026-05-21 DEPLOY App em produção: https://klipper.streamlit.app/
2026-05-21 INIT  Projeto criado. Fases 0-5 implementadas.
                 Stack: Streamlit + Supabase + LiteLLM.
                 Engines M1/M2/M3/Anti-BS/Fragility implementados.
                 Migration SQL gerada (pendente execução no Supabase).
```
