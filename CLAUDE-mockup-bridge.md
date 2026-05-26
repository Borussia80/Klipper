# CLAUDE-mockup-bridge.md
# Klipper · Mapeamento Mockup React → Streamlit
> Carregue junto com CLAUDE.md quando a tarefa for implementar uma página
> baseada no mockup visual (design_handoff_klipper/mockup/klipper-mockup-v2.jsx).

---

## Princípio

O mockup React é a VERDADE VISUAL — cores, espaçamentos, hierarquia, ordem
dos elementos. O Streamlit é o CONTAINER — tem limitações, mas o resultado
visual deve ser o mais próximo possível do mockup.

Nunca invente tokens ou cores. Se o mockup usa uma cor, encontre o equivalente
em `core/styles.py` ou nas CSS variables já definidas.

---

## Mapeamento de componentes

### Layout geral
```
React                          Streamlit
─────────────────────────────────────────────────────
<Sidebar>                   →  setup_sidebar()
<div style={{flex:1}}>      →  conteúdo após setup_sidebar()
page padding: 28px 32px     →  Streamlit nativo (não replicar)
```

### Tipografia / Hero
```
React                          Streamlit
─────────────────────────────────────────────────────
<div className="serif">     →  font-family:var(--font-serif) no HTML inline
<div className="mono">      →  font-family:var(--font-mono) no HTML inline
hero_section(title, saldo,  →  hero_section() de core/styles.py
  ganhos, gastos, subtitle)
```

### KPI Cards
```
React                          Streamlit
─────────────────────────────────────────────────────
<KPICard label value sub    →  stat_card(label, value, sub, tone)
  tone="pos"/>                 injetado via st.markdown(..., unsafe_allow_html=True)

4 KPIs em linha             →  c1,c2,c3,c4 = st.columns(4, gap="small")
                               st.markdown(stat_card(...), unsafe_allow_html=True)
```

### Budget bars / Progress bars
```
React                          Streamlit
─────────────────────────────────────────────────────
<div style={{height:6,      →  bar_track(gasto, limite, tone)
  background:...}}>             de core/styles.py
  <div style={{width:pct%}}/>
```

### Transaction rows
```
React                          Streamlit
─────────────────────────────────────────────────────
<TxRow tx={tx}/>            →  tx_row(category, name, date_str,
                                  subcategory, amount, tone, notes)
                               de core/styles.py
                               Agrupe em: st.markdown(f'<div class="k-card">'
                                 + rows_html + '</div>', unsafe_allow_html=True)
```

### Charts (Recharts → Plotly)
```
React                          Streamlit
─────────────────────────────────────────────────────
<PieChart> + <Pie hole=.62> →  px.pie(df, hole=0.62, color_discrete_map=CAT_COLORS)
<BarChart barmode="group">  →  px.bar(df, barmode="group")
<LineChart>/<AreaChart>     →  px.line() ou go.Scatter(fill="tozeroy")
<LineChart markers>         →  px.line(markers=True)

Sempre aplicar após criar o fig:
fig.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor ="rgba(0,0,0,0)",
    font_family  ="Geist Sans, Inter, sans-serif",
    font_color   ="#94A3B8",
    margin       =dict(t=8,b=8,l=0,r=0),
)
st.plotly_chart(fig, use_container_width=True)
```

### Tabs
```
React                          Streamlit
─────────────────────────────────────────────────────
tab buttons custom styled   →  tab1, tab2, tab3 = st.tabs(["Label1","Label2","Label3"])
onClick setState            →  with tab1: ... with tab2: ...
```

### Modais
```
React                          Streamlit
─────────────────────────────────────────────────────
<div className="modal-bg">  →  @st.dialog("Título", width="large")
  <div className="modal">      def meu_modal():
    ...                            ...
  </div>                     if st.button("Abrir"):
</div>                           meu_modal()

backdrop-filter: blur()     →  Streamlit cuida automaticamente
animações de entrada        →  não replicar (Streamlit não suporta)
```

### Inputs
```
React                          Streamlit
─────────────────────────────────────────────────────
<input className="k-input"> →  st.text_input(), st.number_input()
<select className="k-select">→  st.selectbox()
<textarea>                  →  st.text_area()
focus brass glow            →  já definido no KLIPPER_CSS
```

### Action buttons
```
React                          Streamlit
─────────────────────────────────────────────────────
<button className="btn-p">  →  st.button("Label", type="primary")
<button className="btn-g">  →  st.button("Label", type="secondary")
btn-sm (padding menor)      →  st.button tamanho padrão (não tem sm)
```

### Chips / Badges / Pills
```
React                          Streamlit
─────────────────────────────────────────────────────
<button className="chip">   →  chip(text, tone) de core/styles.py
status badges inline        →  HTML inline com cores das CSS variables
```

### Score gauge (SVG circular)
```
React                          Streamlit
─────────────────────────────────────────────────────
<svg><circle strokeDasharray →  score_circle(score) de core/styles.py
  .../></svg>                   ou go.Indicator(mode="gauge+number")
```

---

## Cores — mapeamento direto

| Mockup (T.xxx)    | CSS Variable       | Tailwind           |
|---|---|---|
| T.brass           | var(--brass)       | text-brass         |
| T.emerald         | var(--emerald)     | —                  |
| T.rust            | var(--rust)        | —                  |
| T.electric        | var(--electric)    | —                  |
| T.warn            | var(--warn)        | —                  |
| T.ink             | var(--ink)         | —                  |
| T.ink3            | var(--ink-3)       | —                  |
| T.ink4            | var(--ink-4)       | —                  |
| T.card            | var(--card)        | bg-klipper-surface |
| T.border          | var(--rule)        | —                  |
| T.border2         | var(--rule-2)      | —                  |

---

## Limitações do Streamlit que NÃO replicar

- Backdrop blur nos modais → Streamlit cuida
- CSS transitions e hover states → definidos no KLIPPER_CSS
- Sidebar animation → nativa do Streamlit
- Body `position: fixed` → nunca usar em Streamlit
- Custom scrollbar → já definido no KLIPPER_CSS

---

## Sessão modelo para implementar uma página

```
Sessão Klipper. Leia CLAUDE.md + CLAUDE-ux.md + CLAUDE-mockup-bridge.md.

Tarefa: implementar [NOME DA PÁGINA]
Arquivo alvo: pages/[X_Pagina.py]
Referência visual: /add design_handoff_klipper/mockup/klipper-mockup-v2.jsx
  → componente alvo: function [NomePagina]() (linha X a Y do mockup)

Regras:
- O mockup React é a verdade visual
- CLAUDE-mockup-bridge.md mapeia cada elemento React → equivalente Streamlit
- Cores e tokens: sempre de core/styles.py ou CSS variables
- Charts: Plotly com dark theme padrão (ver bridge)
- Modais: @st.dialog (não st.expander)
- Testes TDD primeiro: tests/test_[pagina]_sprint7.py

Não toque em outros arquivos sem avisar.
Ciclo: Red → Green → Refactor.
```

---

## Ordem recomendada de implementação

| Sprint | Página | Componente no mockup | Complexidade |
|---|---|---|---|
| 1 | `1_Dashboard.py` | `function Dashboard()` | ✅ já feito |
| 2 | `7_Orcamento.py` | `function Orcamento()` | Média |
| 3 | `2_Transacoes.py` | `function Transacoes()` | Alta |
| 4 | `3_Investimentos.py` | `function Investimentos()` | Alta |
| 5 | `6_Contas.py` | `function Contas()` | Média |
| 6 | `5_AI_Consilium.py` | `function AIConsilium()` | Média |
| 7 | `10_Saude.py` | `function Saude()` | Alta |
