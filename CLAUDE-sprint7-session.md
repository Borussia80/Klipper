# CLAUDE-sprint7-session.md
# Sessão Klipper · Sprint 7 — Home, Dashboard, Modais Transações & Investimentos
> Cole este arquivo no Claude Code no início da sessão. Leia também CLAUDE.md.

---

## CONTEXTO

Roberto (product owner) identificou que Home, Dashboard e os modais de Transações e
Investimentos estão quebrados no mobile e aquém do padrão visual esperado.
Esta sessão entrega os 4 arquivos abaixo. Nada além disso.

---

## ARQUIVOS DESTA SESSÃO (escopo fechado)

| Arquivo | Ação |
|---|---|
| `core/modals.py` | CRIAR — todos os @st.dialog do app |
| `pages/1_Dashboard.py` | SUBSTITUIR — dashboard completo com charts |
| `pages/3_Investimentos.py` | SUBSTITUIR — dashboard promovido ao nível home |
| `app.py` | EDITAR — só o mobile fix CSS (não tocar em mais nada) |

**Não toque em:** `core/styles.py`, `core/repositories.py`, `models/`, `migrations/`, `tests/`, `bot/`.

---

## REFERÊNCIAS OBRIGATÓRIAS (leia antes de escrever qualquer linha)

```
/add core/styles.py          ← tokens, CAT_COLORS, fmt_brl, kpi_card, action_card,
                                hero_section, tx_row, setup_sidebar, context_card
/add core/repositories.py    ← TransactionRepository, BankAccountRepository,
                                InvestmentRepository
/add models/transaction.py   ← Transaction, TransactionType, TransactionStatus
/add models/investment.py    ← Investment
/add models/bank_account.py  ← BankAccount
/add pages/7_Orcamento.py    ← referência de qualidade: gauge + line chart Plotly
/add tests/test_dashboard_charts.py ← referência TDD
```

---

## CICLO OBRIGATÓRIO

```
① Red   — escreva o teste antes do código. Ele deve falhar.
② Green — mínimo de código para passar.
③ Refactor — sem quebrar testes.
```

Arquivos de teste desta sessão:
- `tests/test_modals.py`
- `tests/test_dashboard_sprint7.py`
- `tests/test_investimentos_sprint7.py`

---

## CRITÉRIOS DE ACEITAÇÃO

### Mobile (testado em 390×844)
- [ ] Coluna nav oculta em telas < 640px
- [ ] Conteúdo ocupa 100% da largura
- [ ] Nenhum scroll horizontal
- [ ] Hero section legível sem zoom

### Home (app.py)
- [ ] Hero com saldo líquido do mês em `font-serif` 38px
- [ ] 4 KPI cards em grid responsivo (2×2 no mobile)
- [ ] Quick actions row com: Lançar · Transferir · Importar · Investir
- [ ] WikiAgent engines no final
- [ ] Sem cards decorativos sem dados reais

### Dashboard (pages/1_Dashboard.py)
- [ ] Hero section com saldo, entradas e saídas do mês
- [ ] Donut: top-8 categorias de gastos (hole=0.62, CAT_COLORS, dark theme)
- [ ] Bar chart: últimos 6 meses entradas × saídas (barmode="group")
- [ ] Lista das 5 últimas transações usando tx_row()
- [ ] Botão "Ver todas" → link para /Transacoes
- [ ] Tudo via setup_sidebar() — sem st.columns([1, 4]) no topo

### Modais de Transações (core/modals.py)
- [ ] modal_add_transaction(): data, valor, tipo (GANHO/GASTO), categoria,
      conta bancária, descrição, status, notas
- [ ] modal_edit_transaction(tx_id): mesmos campos, pre-filled
- [ ] modal_confirm_delete(label, on_confirm): genérico, reutilizável
- [ ] modal_transfer(): conta origem, conta destino, valor, data
- [ ] Todos com st.toast() de sucesso/erro
- [ ] Todos com adjust_balance() automático após salvar

### Modais de Investimentos (core/modals.py)
- [ ] modal_add_investment(): ticker input + botão "Buscar cotação" (lookup
      market_data → pre-fill preço, DY, P/VP), quantidade, preço médio,
      setor, conta custódia
- [ ] modal_edit_investment(inv_id): pre-filled
- [ ] Ticker lookup não bloqueia o form se API falhar (try/except)

### Dashboard de Investimentos (pages/3_Investimentos.py)
- [ ] Hero: valor total da carteira + variação do dia
- [ ] Performance strip: portfólio vs BOVA11, IFIX, IVVB11 (sem expander)
- [ ] Posições ao vivo: tabela com ticker, preço, var%, valor atual, G/L
- [ ] Donut de alocação: FII × Ações × RF × Caixa (px.pie, CAT_COLORS-inspired)
- [ ] Botão "+ Posição" → modal_add_investment()
- [ ] Botão editar por linha → modal_edit_investment(inv_id)
- [ ] Feed de rendimentos últimos 60 dias ao final da página
- [ ] setup_sidebar() — sem layout columns legado

---

## PADRÕES DE CÓDIGO

### @st.dialog obrigatório (NÃO usar st.modal ou qualquer outro)
```python
@st.dialog("Lançar transação", width="large")
def modal_add_transaction() -> None:
    """Abre form de nova transação. Salva via TransactionRepository."""
    ...
    if st.button("Salvar", type="primary", use_container_width=True):
        try:
            repo.create(tx)
            BankAccountRepository().adjust_balance(tx.account_id, delta)
            st.toast("Transação salva ✓", icon="✅")
            st.rerun()
        except Exception as e:
            st.error(str(e))
```

### Plotly dark theme (obrigatório em todos os charts)
```python
fig.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font_family="Geist Sans, Inter, sans-serif",
    font_color="#94A3B8",
    showlegend=True,
    margin=dict(t=8, b=8, l=0, r=0),
)
fig.update_xaxes(showgrid=False, zeroline=False)
fig.update_yaxes(showgrid=True, gridcolor="rgba(255,255,255,0.05)", zeroline=False)
```

### Mobile fix (aplicar APENAS no app.py, bloco CSS já existente)
```css
@media (max-width: 640px) {
  div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:first-child {
    display: none !important;
    width: 0 !important;
    min-width: 0 !important;
    padding: 0 !important;
    flex: 0 0 0 !important;
  }
  div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:last-child {
    flex: 1 1 100% !important;
    width: 100% !important;
  }
}
```

### Grid KPI responsivo (2 colunas no mobile)
```python
# Use st.columns com gap pequeno
c1, c2, c3, c4 = st.columns(4, gap="small")
# CSS já cuida do colapso mobile via @media
```

---

## QUANDO TERMINAR

1. Rode `python -m pytest tests/test_modals.py tests/test_dashboard_sprint7.py tests/test_investimentos_sprint7.py -v`
2. Rode `python -m pytest tests/ -q --tb=short` — cobertura geral não pode cair abaixo de 80%
3. Rode `streamlit run app.py` e valide visualmente no browser em 390px (DevTools mobile)
4. Faça commit apenas com aprovação explícita do Roberto

---

## NÃO FAZER (lista de proibições)

- `st.columns([1, 4])` no topo de nenhuma página (usar `setup_sidebar()`)
- Cores hardcoded fora de `CAT_COLORS` ou tokens de `styles.py`
- `st.experimental_dialog` (deprecated — usar `@st.dialog`)
- Charts sem tooltip configurado
- Modais sem `st.rerun()` após salvar
- Lógica de negócio dentro de `pages/` (vai para `core/` ou `models/`)
- Função com mais de ~25 linhas sem questionar a divisão
