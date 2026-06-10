# CLAUDE-log.md — Klipper · Log de Sessões
> Consulte ao investigar bugs ou entender histórico de uma feature.
> Formato: `DATA  TIPO  Descrição · detalhes técnicos · contagem de testes`

---

## 2026-05

### 2026-05-23
**FEAT** Sprint 1 — Dashboard charts
- `core/analytics.py`: `preparar_dados_donut_categorias` + `preparar_dados_barras_mensais`
- `pages/1_Dashboard.py`: donut de gastos por categoria + bar chart entradas×saídas últimos meses
- Plotly dark theme: `paper_bgcolor` transparent, cores de `CAT_COLORS`, tooltips
- Donut: top-8 categorias, `hole=0.62`
- 18 novos testes TDD → `tests/test_dashboard_charts.py`
- **Total acumulado: 466 testes**

**AUDIT** Deep dive UI/UX com Playwright (27 screenshots)
- Gap map documentado: Plotly importado mas nunca usado em Dashboard, Investimentos, Contas
- Mobile completamente quebrado: nav 840px preenche viewport 390×844
- Dashboard de cotações enterrado 3 níveis dentro de expander
- Referências adotadas: Figma Finance Mobile Kit + eliftech.com
- Sprints 1–6 planejados → ver `CLAUDE-ux.md`

### 2026-05-22
**FEAT** Toggle claro/escuro na barra de navegação
- `_FORCE_LIGHT_CSS` / `_FORCE_DARK_CSS` sobrescrevem `prefers-color-scheme`
- Persiste por sessão via `st.session_state["klipper_theme"]`

**FEAT** Dashboard ao vivo no modal de Investimentos (tab "◉ Dashboard ao vivo")
- Performance strip: portfólio hoje vs BOVA11, IFIX, IVVB11
- Posições ao vivo: preço, var.%, valor atual e G/L por ativo
- Feed de rendimentos: últimos 60 dias (`Category.RENDA`)

**FEAT** Parser BTG Pactual — prints PNG/JPG do app mobile
- `_parse_btg_date_line`, `_parse_btg_amount_line`, `parse_btg_statement`
- `_is_btg_format` detecta automaticamente o banco pelo texto OCR
- `read_statement_image`: OCR de imagem com roteamento Itaú/BTG
- Importar aceita PNG/JPG além de PDF
- 23 novos testes TDD → **Total: 448 testes**

**FIX** Cotações movidas para dentro do modal de Investimentos (tabs)
- Ticker lookup com pre-fill de Preço atual / DY / P/VP no form

**FIX** PDF statement reader — Itaú extrato
- `PyMuPDF get_text("words")` + Y-bucket para reconstruir linhas de tabela
- Filtro `_SKIP_RE` para "SALDO DO DIA" e cabeçalhos
- Default `GANHO` para valores sem sinal (convenção Itaú: débitos têm "-")
- 20 novos testes TDD (`TestParseItauLine`, `TestParseAmountAndType`, `TestParseTransactions`)

**FIX** Balance auto-adjustment
- `tx_balance_delta` + `BankAccountRepository.adjust_balance`
- Edição/criação/exclusão de transação atualiza saldo da conta automaticamente
- 8 novos testes TDD (`TestTxBalanceDelta`, `TestBankAccountAdjustBalance`)

**FEAT** Cotações helpers
- `fmt_change` → `core/styles.py`
- `is_fii` → `core/market_data.py`
- 16 novos testes TDD

**FIX** Homepage: removidos cards decorativos sem função
- Mantidos: hero logo, briefing diário (4 KPIs), WikiAgent engines

**FIX** Sidebar navigation
- Adicionado link "⌂ Klipper" (`app.py`) como primeiro item
- "Extratos" renomeado para "Importar" (ícone ⬆)
- `render_navigation()` protegida com try/except por item

**FEAT** Market data completo
- B3, Tesouro Direto, PTAX, câmbio (yfinance + BCB)
- Cache Redis + fakeredis · Circuit breaker CLOSED/OPEN/HALF\_OPEN
- 63 novos testes → **Total: 269 testes**

**FEAT** Kira — IA financeira NVIDIA NIM
- `core/financial_ai.py`: contexto financeiro + Llama 3.3-70B
- Dashboard briefing widget + sidebar Q&A em todas as páginas

**FEAT** Simplifi layout
- Spending Plan hero, category badges, accounts rail
- TOTP modal synergy fix · XSS + CSS injection hardening

### 2026-05-21
**DEPLOY** Produção: https://klipper.streamlit.app/

**INIT** Projeto criado — Fases 0–5
- Stack: Streamlit + Supabase + LiteLLM
- Engines M1/M2/M3/Anti-BS/Fragility implementados
- Migration SQL gerada (pendente execução no Supabase)

---

## PENDÊNCIAS ABERTAS

| ID | Fase | Descrição | Arquivo |
|---|---|---|---|
| P1 | 6 | Telegram Bot — captura zero-fricção | `bot/bot.py` |
| P2 | 7 | Sprint 2 — Investimentos charts | `pages/3_Investimentos.py` |
| P3 | 7 | Sprint 3 — Transações charts | `pages/2_Transacoes.py` |
| P4 | 7 | Sprint 4 — Contas charts | `pages/6_Contas.py` |
| P5 | 7 | Sprint 5 — Mobile fix | todas as páginas |
| P6 | 7 | Sprint 6 — Drill-down interativo | `pages/1_Dashboard.py` |
| P7 | — | API keys de IA no `.env` | `.env` |
