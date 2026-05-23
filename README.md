# Klipper — Wealth Operating System

Sistema pessoal de gestão financeira. Matemática ancora. Contexto modula risco. Narrativa sem evidência não altera decisão.

**Stack:** Python · Streamlit Cloud · Supabase (PostgreSQL) · LiteLLM (multi-provider IA) · NVIDIA NIM

**Produção:** https://klipper.streamlit.app/ · **Repo:** https://github.com/Borussia80/Klipper

---

## Instalação

```bash
git clone https://github.com/Borussia80/Klipper
cd Klipper
pip install -r requirements.txt
cp .env.example .env          # preencha as chaves
streamlit run app.py
```

## Variáveis de ambiente

```
SUPABASE_URL=
SUPABASE_KEY=
ANTHROPIC_API_KEY=
GOOGLE_API_KEY=
OPENAI_API_KEY=
DASHSCOPE_API_KEY=
MOONSHOT_API_KEY=
NVIDIA_API_KEY=
REDIS_URL=          # opcional; sem ela usa fakeredis in-memory
```

## Banco de dados

Execute `migrations/001_initial_schema.sql` e `migrations/002_v2_schema.sql` no SQL Editor do Supabase antes do primeiro uso.

## Testes

```bash
python -m pytest tests/ -v               # suite completa
python -m pytest tests/ --tb=short -q   # saída compacta
```

A cobertura mínima aceita pelo CI é **80 %**. Qualquer PR que reduza a cobertura abaixo desse limiar é bloqueado automaticamente.

---

## Arquitetura

```
WikiAgent Financeiro v2.0
├── M1  Quant Engine       → core/m1_quant.py
├── M2  Governance         → core/m2_governance.py
├── M3  Context Layer      → core/m3_context.py
├── M4  AI Consilium       → pages/5_AI_Consilium.py
├── Anti-BS Engine         → core/anti_bs.py
├── Fragility Score        → core/fragility.py
├── Kira · IA Financeira   → core/financial_ai.py  (NVIDIA NIM)
└── Market Data            → core/market_data.py   (B3 · Tesouro · PTAX)
```

```
app.py                     ← entrada Streamlit
core/                      ← engines + utilitários
  market_data.py           ← cotações B3, Tesouro, câmbio
  market_cache.py          ← Redis + fallback in-memory
  circuit_breaker.py       ← proteção a APIs instáveis
  financial_ai.py          ← inteligência financeira NVIDIA NIM
models/                    ← Pydantic (Transaction, Investment, BankAccount…)
pages/                     ← páginas Streamlit (1_Dashboard … 11_Extratos)
migrations/                ← SQL Supabase
tests/                     ← pytest ≥ 448 testes
```

---

## Processo de desenvolvimento

### TDD é obrigação técnica

Não existe "adicionar testes depois". O ciclo é:

```
Red → Green → Refactor
```

1. **Red** — escreva o teste que descreve o comportamento esperado. Ele falha porque o código ainda não existe.
2. **Green** — escreva o mínimo de código para o teste passar. Nada além disso.
3. **Refactor** — melhore o design sem quebrar nenhum teste existente.

Código sem teste não entra no repositório. Não é filosofia; é a definição de "pronto".

---

### F.I.R.S.T. — os cinco atributos de um bom teste

Princípio de Robert C. Martin. Todo teste escrito neste projeto deve satisfazer as cinco propriedades:

| Letra | Atributo | O que significa aqui |
|-------|----------|----------------------|
| **F** | **Fast** | A suite completa roda em < 10 s. Testes de integração com I/O de rede são marcados `@pytest.mark.slow` e excluídos do ciclo local. |
| **I** | **Independent** | Nenhum teste depende do estado deixado por outro. Cada teste cria seus próprios dados e limpa atrás de si. `autouse` fixtures isolam session state e cache. |
| **R** | **Repeatable** | Mesmo resultado em qualquer máquina, em qualquer hora. Datas fixas usam valores absolutos (ex.: `date(2030, 1, 1)`); APIs externas são sempre mockadas. |
| **S** | **Self-Validating** | O teste passa ou falha — sem inspeção manual de log. `assert` com mensagem clara é obrigatório. Testes que "precisam ser lidos" para entender o resultado são reescritos. |
| **T** | **Timely** | O teste é escrito **antes** do código de produção, não depois. Um teste escrito após o código que ele valida não é TDD; é auditoria. |

Violações são bloqueadas no code review. Não existem exceções.

---

### Single Responsibility Principle (SRP)

Cada módulo, classe e função tem **um único motivo para mudar**.

Exemplos concretos neste código:

- `core/market_cache.py` — só cuida de persistência e TTL de cotações. Não conhece formato de ticker nem regra de negócio.
- `core/circuit_breaker.py` — só implementa a máquina de estados CLOSED/OPEN/HALF_OPEN. Não conhece quais APIs estão sendo protegidas.
- `core/market_data.py` — orquestra fontes e cache; não implementa protocolo HTTP nem lógica de TTL.
- `core/financial_ai.py` — constrói contexto financeiro e delega ao LLM. Não conhece Streamlit nem repositórios.

Quando uma função passa de **~25 linhas** ou uma classe acumula mais de uma responsabilidade, ela é dividida antes de qualquer nova feature ser adicionada.

---

### Práticas XP incorporadas

#### Pair Programming
Toda sessão de desenvolvimento com o agente Claude Code é pair programming assistido. O humano define **o quê** e **por quê**; o agente executa e questiona. O humano revisa cada diff antes de aceitar.

#### Integração Contínua (CI)
GitHub Actions executa em todo push:
```
lint (Ruff) → type check (mypy) → testes (pytest) → cobertura ≥ 80%
```
Nenhum merge acontece com CI vermelho. Não existe "vou corrigir depois do merge".

#### Testes antes do código (Test-First)
A ordem é invariável:
1. Entender o requisito
2. Escrever o teste que falha
3. Escrever o código mínimo que passa
4. Refatorar

Issues abertas sem teste de aceitação correspondente não são iniciadas.

#### Refactoring contínuo
Refatoração não é sprint separado. Acontece no passo **Refactor** de cada ciclo Red→Green→Refactor. A regra da escotagem: deixe o código mais limpo do que encontrou — dentro do escopo do que está sendo alterado. Nunca fora do escopo sem discussão prévia.

#### Feedback curto
- Suite local: < 10 s
- CI completo: < 3 min
- Review de PR: mesmo dia
- Deploy em produção: automático via Streamlit Cloud após merge em `main`

O tempo entre "escrever código" e "saber se funciona" é minimizado em todas as camadas.

---

## Regras do WikiAgent

- Matemática ancora. Narrativa sem evidência quantitativa não altera decisão.
- Contexto modula risco — nunca compra ativo sozinho.
- Declarar incerteza sempre que dados forem insuficientes.
- Sem verborreia. Resposta máxima: 300 palavras.
- M2 Beginner Mode: max ativo 10% · max tese 25% · caixa mínimo 20%.

---

## Funcionalidades

| Área | O que faz |
| ---- | --------- |
| **Dashboard** | KPIs do mês, briefing diário, WikiAgent engines |
| **Transações** | CRUD com auto-ajuste de saldo da conta bancária |
| **Investimentos (modal)** | Dashboard ao vivo (preços, performance, feed de rendimentos), lookup de cotação com pre-fill no form, cotações do portfólio + benchmarks |
| **Contas & Cartões** | Saldo por conta, fatura, limites, parcelamentos |
| **Orçamento** | Limites por categoria, meta de poupança, score financeiro 0–100 |
| **Importar extrato** | PDF (Itaú e outros) + **print de tela PNG/JPG (BTG Pactual)** — OCR automático, revisão antes de importar |
| **AI Consilium** | Multi-provider: Claude, Gemini, GPT-4o, Qwen, Kimi |
| **Kira** | IA financeira pessoal via NVIDIA NIM (Llama 3.3-70B) |
| **Market Data** | Cotações B3, Tesouro Direto, PTAX, câmbio em tempo real |
| **Tema** | Toggle claro/escuro na barra de navegação, persiste por sessão |

## Pendências

- [ ] Fase 6: Telegram Bot (`bot/bot.py`) — captura zero-fricção
- [ ] Adicionar API keys de IA no `.env`
