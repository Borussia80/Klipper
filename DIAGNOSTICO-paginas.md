# KLIPPER — Diagnóstico de páginas · Sprint 7
> Gerado após leitura de todas as 12 páginas. Use como guia de sessão.

---

## Status geral de layout

| ✅ | Todas as 12 páginas já usam `setup_sidebar()` |
|---|---|
| ✅ | Nenhuma página tem `st.columns([1, 4])` no topo |
| ✅ | `initial_sidebar_state="collapsed"` em todas |

**Conclusão: o problema de mobile NÃO é de layout de nav — é de conteúdo.**
O Streamlit empilha `st.columns` de conteúdo em telas < 640px. As páginas com
grids de 4 colunas (KPI strips) precisam de CSS `@media` para colapsar em 2×2.

---

## Mapa de modais — o que existe vs o que falta

| Página | Modal existente | Qualidade | Ação |
|---|---|---|---|
| `1_Dashboard.py` | nenhum próprio — usa `core/modals` via botão | ✅ OK | — |
| `2_Transacoes.py` | `quick_add_dialog()` + edit dialog próprios | ✅ Bons | ver nota abaixo |
| `3_Investimentos.py` | usa `core.modals.modal_add/edit_investment` | ✅ OK | — |
| `4_Decisoes.py` | `st.form` em tabs (sem modal) | ✅ Adequado | — |
| `5_AI_Consilium.py` | sem modal (é chat — correto) | ✅ OK | — |
| `6_Contas.py` | `st.expander` para cartão + conta | ⚠️ Expander | → `@st.dialog` |
| `7_Orcamento.py` | `@st.dialog("Orçamento")` | ✅ OK | — |
| `8_Posicoes.py` | sem modal (tabela read-only) | ✅ OK | — |
| `9_Portfolio.py` | sem modal (tabela read-only) | ✅ OK | — |
| `10_Saude.py` | `st.expander` "Novo profissional" | ⚠️ Expander | → `@st.dialog` |
| `11_Extratos.py` | sem modal (flow de importação) | ✅ OK | — |
| `12_Sobre.py` | sem modal (informativo) | ✅ OK | — |

---

## ⚠️ Conflito identificado: `core/modals.py` vs `2_Transacoes.py`

O `core/modals.py` entregue na sessão anterior define `modal_add_transaction`
e `modal_edit_transaction`. Mas `2_Transacoes.py` já tem seus próprios dialogs:
- `quick_add_dialog()` — lançamento rápido por texto livre com NLP
- edit dialog inline (linha 150)

**Resolução correta:**
```
core/modals.py  →  manter só: modal_confirm_delete, modal_transfer,
                               modal_add_investment, modal_edit_investment
2_Transacoes.py →  manter seus próprios dialogs (são mais ricos — têm
                   quick_add NLP + installment engine)
```

Remover `modal_add_transaction` e `modal_edit_transaction` do `core/modals.py`
para evitar duplicação e confusão.

---

## Ações necessárias (escopo real desta sessão)

### P0 — Corrigir agora
1. **`6_Contas.py`** — converter 2 expanders em `@st.dialog`
   - `expander("+ Novo cartão")` → `@st.dialog("Novo cartão")`
   - `expander("+ Nova conta bancária")` → `@st.dialog("Nova conta bancária")`

2. **`10_Saude.py`** — converter 1 expander em `@st.dialog`
   - `expander("+ Novo profissional")` → `@st.dialog("Novo profissional")`

3. **`core/modals.py`** — remover modais de transação duplicados
   - Manter: `modal_confirm_delete`, `modal_transfer`, `modal_add_investment`, `modal_edit_investment`
   - Remover: `modal_add_transaction`, `modal_edit_transaction`

### P1 — CSS mobile KPI grid
Aplicar em todas as páginas que têm `st.columns(4)`:
```css
@media (max-width: 640px) {
  /* KPI strip 4-col → 2×2 */
  div[data-testid="stHorizontalBlock"] {
    flex-wrap: wrap !important;
  }
  div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] {
    flex: 1 1 calc(50% - 8px) !important;
    min-width: calc(50% - 8px) !important;
    max-width: calc(50% - 8px) !important;
  }
}
```
Melhor colocar isso no `KLIPPER_CSS` do `core/styles.py` — aplica globalmente.

---

## Páginas que NÃO precisam de ajuste

- `4_Decisoes.py` — `st.form` em tabs é o padrão correto para decisões auditáveis
- `5_AI_Consilium.py` — interface de chat sem modal é correto
- `8_Posicoes.py` — tabela de mercado read-only, sem CRUD
- `9_Portfolio.py` — master/detail read-only, sem CRUD
- `11_Extratos.py` — flow de importação sequencial, sem modal
- `12_Sobre.py` — informativo, sem ação

---

## Sessão Claude Code — comando de abertura

```
Sessão Klipper. Leia CLAUDE.md.

Tarefas desta sessão (3 itens, nesta ordem):

1. core/modals.py — REMOVER modal_add_transaction e modal_edit_transaction.
   Manter: modal_confirm_delete, modal_transfer, modal_add_investment, modal_edit_investment.
   Os modais de transação vivem em 2_Transacoes.py — não duplicar.

2. pages/6_Contas.py — converter expanders em @st.dialog.
   Ver arquivo PATCH-6_Contas_dialogs.py para as funções prontas.
   Substituir os blocos with st.expander("+ Novo cartão") e
   with st.expander("+ Nova conta bancária") pelos botões + dialogs.

3. pages/10_Saude.py — converter expander em @st.dialog.
   Ver arquivo PATCH-10_Saude_dialog.py para a função pronta.
   Substituir with st.expander("+ Novo profissional") pelo botão + dialog.

4. core/styles.py — adicionar CSS @media mobile KPI grid no KLIPPER_CSS.
   Ver seção "P1 — CSS mobile KPI grid" no diagnóstico.

Ciclo: Red → Green → Refactor. Testes em tests/test_modals.py.
Não toque em nada fora desses 4 arquivos.
```
