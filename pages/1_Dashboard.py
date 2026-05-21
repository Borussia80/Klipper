"""Home — O dia em dinheiro · feed financeiro."""

from __future__ import annotations

import calendar
from datetime import date

import plotly.express as px
import streamlit as st

from core.analytics import calcular_saldo_mensal, calcular_top_categorias
from core.behavioral import calcular_score_financeiro, detectar_alertas_padrao
from core.installment_engine import calcular_comprometimento_mensal
from core.m2_governance import verificar_limites, hard_fail, CAIXA_MIN_PCT
from core.repositories import (
    InvestmentRepository, TransactionRepository,
    InstallmentRepository, BudgetRepository,
)
from core.styles import (
    inject_css, fmt_brl, fmt_pct, kicker, k_card, k_card_with_header,
    stat_card, feed_row, mood_chip, chip, bar_track, section_header,
    sidebar_brand, sidebar_engines, sidebar_user, load_page_icon,
)
from models.transaction import TransactionType

st.set_page_config(page_title="Home · Klipper", page_icon=load_page_icon(), layout="wide")
inject_css()

# ── Sidebar ────────────────────────────────────────────────────────────────────
hoje = date.today()
ano = hoje.year
mes = hoje.month

tx_repo   = TransactionRepository()
inv_repo  = InvestmentRepository()
inst_repo = InstallmentRepository()
bud_repo  = BudgetRepository()

with st.spinner(""):
    try:
        transacoes   = tx_repo.list_by_month(ano, mes)
        portfolio    = inv_repo.get_portfolio()
        installments = inst_repo.list_active()
        budgets      = bud_repo.list_by_month(ano, mes)
    except Exception as e:
        st.error(f"Erro ao conectar ao banco: {e}")
        st.stop()

transacoes_3m: list = []
for delta in range(1, 4):
    m_prev, y_prev = mes - delta, ano
    while m_prev < 1:
        m_prev += 12; y_prev -= 1
    try:
        transacoes_3m.extend(tx_repo.list_by_month(y_prev, m_prev))
    except Exception:
        pass

saldo           = calcular_saldo_mensal(transacoes, ano, mes)
total_portfolio = sum(inv.current_value for inv in portfolio)
total_ativos    = saldo.total_ganhos + total_portfolio
caixa_pct       = (saldo.saldo / total_ativos * 100) if total_ativos > 0 else 0.0
comp_mes        = calcular_comprometimento_mensal(installments).get(hoje.strftime("%Y-%m"), 0.0)

# M2 violations count
alertas_m2 = verificar_limites(portfolio, caixa_disponivel=saldo.saldo)
violations  = sum(1 for a in alertas_m2 if a.is_hard_fail)

score = calcular_score_financeiro(
    transacoes=transacoes, budgets=budgets, installments=installments,
    taxa_poupanca_atual=saldo.taxa_poupanca, meta_poupanca=20.0,
    caixa_pct=caixa_pct, transacoes_3_meses=transacoes_3m,
)

# Sidebar content
with st.sidebar:
    st.markdown(sidebar_brand(), unsafe_allow_html=True)
    total_inv = total_portfolio + saldo.saldo
    snap_html = f"""<div style="margin:4px 12px 6px;padding:12px 14px;
      background:var(--surface-2);border:1px solid var(--rule);
      border-radius:var(--radius-sm);position:relative;overflow:hidden;cursor:pointer">
      <div style="position:absolute;inset:-1px;
        background:radial-gradient(circle at top left,var(--brass-soft),transparent 70%);pointer-events:none"></div>
      <div style="font-size:9.5px;letter-spacing:0.15em;text-transform:uppercase;color:var(--ink-3)">Patrimônio</div>
      <div class="mono" style="font-size:19px;line-height:1;color:var(--ink);font-variant-numeric:tabular-nums;margin-top:4px">{fmt_brl(total_inv, compact=True)}</div>
      <div style="display:flex;gap:8px;margin-top:4px;font-size:10px;color:var(--ink-3);font-family:var(--font-sans)">
        <span style="width:4px;height:4px;border-radius:50%;background:var(--moss);display:inline-block;align-self:center"></span>
        caixa <span class="mono">{caixa_pct:.0f}%</span>
        <span style="width:4px;height:4px;border-radius:50%;background:var(--brass);display:inline-block;align-self:center;margin-left:6px"></span>
        <span>{len(portfolio)} posições</span>
      </div>
    </div>"""
    st.markdown(snap_html, unsafe_allow_html=True)
    st.markdown(sidebar_engines(violations=violations), unsafe_allow_html=True)
    st.markdown(sidebar_user(), unsafe_allow_html=True)

# ── Anti-BS narrative ──────────────────────────────────────────────────────────
alertas_pad = detectar_alertas_padrao(transacoes, transacoes_3m) if transacoes_3m else []
impulsos    = [a for a in alertas_pad]

antiBs_text = ""
if impulsos:
    cats = ", ".join(a.category for a in impulsos[:2])
    antiBs_text = f"Gastos acima da média em {cats}. Orçamento sob tensão — revise antes do próximo aporte."
elif saldo.taxa_poupanca >= 20:
    antiBs_text = "Fluxo equilibrado. Taxa de poupança dentro da meta. Aporte pode ser mantido."
else:
    antiBs_text = "Taxa de poupança abaixo de 20%. Reforce caixa antes de novos aportes."

# ── Topbar ─────────────────────────────────────────────────────────────────────
mes_nome = calendar.month_name[mes].capitalize()
dia_semana = ["segunda", "terça", "quarta", "quinta", "sexta", "sábado", "domingo"][hoje.weekday()]
st.markdown(f"""<div style="display:flex;align-items:flex-start;justify-content:space-between;
  margin-bottom:20px;padding-bottom:16px;border-bottom:1px solid var(--rule)">
  <div>
    <div style="font-family:var(--font-sans);font-size:22px;font-weight:600;color:var(--ink)">Home</div>
    <div style="font-family:var(--font-sans);font-size:11px;letter-spacing:0.10em;
      text-transform:uppercase;color:var(--ink-3);margin-top:2px">{dia_semana}, {hoje.day} {mes_nome[:3].lower()}</div>
  </div>
  <div style="display:flex;align-items:center;gap:8px;font-family:var(--font-mono);
    font-size:11px;color:var(--ink-3)">
    <span style="width:5px;height:5px;border-radius:50%;background:var(--brass);
      box-shadow:0 0 8px var(--brass-glow);display:inline-block"></span>
    22°54′S · 43°10′W · {hoje.strftime("%d/%m/%Y")}
  </div>
</div>""", unsafe_allow_html=True)

# ── Hero strip ─────────────────────────────────────────────────────────────────
gastos_hoje  = sum(t.amount for t in transacoes if t.type == TransactionType.GASTO and t.date == hoje)
ganhos_hoje  = sum(t.amount for t in transacoes if t.type == TransactionType.GANHO and t.date == hoje)
liquido_hoje = ganhos_hoje - gastos_hoje

hero_left = f"""
{kicker(f"O dia em dinheiro · {dia_semana}, {hoje.day} {mes_nome[:3].lower()}")}
<div style="display:flex;align-items:baseline;gap:14px;margin-top:8px">
  <span class="mono" style="font-size:36px;line-height:1;color:var(--ink);font-variant-numeric:tabular-nums"
    >{fmt_brl(liquido_hoje)}</span>
  <span class="mono muted" style="font-size:12px">líquido hoje</span>
</div>
<div style="display:flex;gap:18px;margin-top:14px">
  <div style="display:flex;align-items:center;gap:8px">
    <span style="width:22px;height:22px;border-radius:50%;display:flex;align-items:center;
      justify-content:center;background:rgba(123,198,138,0.12);color:var(--moss);
      font-family:var(--font-mono);font-size:12px;font-weight:600">↗</span>
    <div>
      <div style="font-size:9.5px;letter-spacing:0.14em;text-transform:uppercase;color:var(--ink-3);font-weight:600">entrou</div>
      <div class="mono" style="font-size:13px;color:var(--moss);font-weight:500">{fmt_brl(ganhos_hoje, compact=True)}</div>
    </div>
  </div>
  <div style="display:flex;align-items:center;gap:8px">
    <span style="width:22px;height:22px;border-radius:50%;display:flex;align-items:center;
      justify-content:center;background:var(--surface-2);color:var(--ink-2);
      font-family:var(--font-mono);font-size:12px;font-weight:600">↙</span>
    <div>
      <div style="font-size:9.5px;letter-spacing:0.14em;text-transform:uppercase;color:var(--ink-3);font-weight:600">saiu</div>
      <div class="mono" style="font-size:13px;color:var(--ink);font-weight:500">{fmt_brl(gastos_hoje, compact=True)}</div>
    </div>
  </div>
  <div style="display:flex;align-items:center;gap:8px">
    <span style="width:22px;height:22px;border-radius:50%;display:flex;align-items:center;
      justify-content:center;background:var(--brass-soft);color:var(--brass);
      font-family:var(--font-mono);font-size:12px;font-weight:600">◈</span>
    <div>
      <div style="font-size:9.5px;letter-spacing:0.14em;text-transform:uppercase;color:var(--ink-3);font-weight:600">parcelas/mês</div>
      <div class="mono" style="font-size:13px;color:var(--brass);font-weight:500">{fmt_brl(comp_mes, compact=True)}</div>
    </div>
  </div>
</div>
<div style="border-top:1px solid var(--rule);margin-top:14px;padding-top:14px">
  <div class="serif" style="font-style:italic;font-size:13.5px;color:var(--ink-2);line-height:1.5">
    "{antiBs_text}"
  </div>
  <div class="mono" style="font-size:10px;color:var(--ink-4);margin-top:6px">↳ narrativa Anti-BS · {hoje.strftime("%H:%M")}</div>
</div>
"""

hero_mid = f"""
{kicker(f"{mes_nome[:3]} · até hoje")}
<div class="k-grid k-cols-2" style="margin-top:8px;gap:14px">
  <div class="k-metric">
    <span class="k-metric-l">Entradas</span>
    <span class="k-metric-v pos" style="font-size:22px">{fmt_brl(saldo.total_ganhos, compact=True)}</span>
  </div>
  <div class="k-metric">
    <span class="k-metric-l">Saídas</span>
    <span class="k-metric-v" style="font-size:22px">{fmt_brl(saldo.total_gastos, compact=True)}</span>
  </div>
</div>
<div style="margin-top:14px">
  <div style="height:8px;border-radius:var(--radius-pill);overflow:hidden;
    background:var(--surface-2);border:1px solid var(--rule)">
    <div style="height:100%;width:{min(saldo.taxa_poupanca, 100):.0f}%;
      background:linear-gradient(90deg,var(--sea),var(--moss));border-radius:var(--radius-pill)"></div>
  </div>
  <div style="display:flex;justify-content:space-between;margin-top:6px;font-size:10px;
    font-family:var(--font-sans);color:var(--ink-4)">
    <span>poupança atual</span>
    <span class="mono {'pos' if saldo.taxa_poupanca >= 20 else 'neg'}">{fmt_pct(saldo.taxa_poupanca)}</span>
  </div>
</div>
"""

score_color = "#10B981" if score.total >= 80 else "#F59E0B" if score.total >= 60 else "#D87C6A"
streak_days = score.total // 10

hero_right = f"""
{kicker("Comportamento · score")}
<div style="display:flex;align-items:center;gap:14px;margin-top:8px">
  <div style="position:relative;width:56px;height:56px;flex-shrink:0">
    <svg viewBox="0 0 56 56" style="width:56px;height:56px">
      <circle cx="28" cy="28" r="24" fill="none" stroke="var(--rule)" stroke-width="3"/>
      <circle cx="28" cy="28" r="24" fill="none" stroke="{score_color}" stroke-width="3"
        stroke-dasharray="{score.total / 100 * 150.8:.1f} 150.8"
        stroke-linecap="round" transform="rotate(-90 28 28)"/>
    </svg>
    <div style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center;
      font-family:var(--font-serif);font-size:18px;color:{score_color}">{score.total}</div>
  </div>
  <div style="min-width:0;flex:1">
    <div style="font-family:var(--font-sans);font-size:13px;color:var(--ink);font-weight:500;line-height:1.3">
      {"Excelente" if score.total >= 80 else "Bom" if score.total >= 60 else "Atenção" if score.total >= 40 else "Crítico"} — score financeiro
    </div>
    <div class="muted" style="font-size:11px;margin-top:4px">Meta: 80+ pts · {score.total}/100</div>
  </div>
</div>
<div style="margin-top:14px;padding-top:14px;border-top:1px solid var(--rule);
  display:grid;grid-template-columns:1fr 1fr;gap:10px">
  <div>
    <div class="muted" style="font-size:10px;letter-spacing:0.1em;text-transform:uppercase;font-weight:600">poupança</div>
    <div class="serif {'pos' if score.atingiu_meta_poupanca else 'neg'}" style="font-size:16px"
      >{"✓ meta" if score.atingiu_meta_poupanca else "✗ abaixo"}</div>
  </div>
  <div>
    <div class="muted" style="font-size:10px;letter-spacing:0.1em;text-transform:uppercase;font-weight:600">caixa M2</div>
    <div class="serif {'pos' if score.caixa_m2_ok else 'neg'}" style="font-size:16px"
      >{"✓ ok" if score.caixa_m2_ok else "✗ baixo"}</div>
  </div>
</div>
"""

col1, col2, col3 = st.columns([1.4, 1, 1])
with col1:
    st.markdown(f'<div class="k-card gilt"><div class="k-card-b">{hero_left}</div></div>',
                unsafe_allow_html=True)
with col2:
    st.markdown(f'<div class="k-card"><div class="k-card-b">{hero_mid}</div></div>',
                unsafe_allow_html=True)
with col3:
    st.markdown(f'<div class="k-card"><div class="k-card-b">{hero_right}</div></div>',
                unsafe_allow_html=True)

# ── Main grid — feed + rail ────────────────────────────────────────────────────
st.markdown(section_header("Feed financeiro", "ao vivo · todos os fluxos"), unsafe_allow_html=True)

col_feed, col_rail = st.columns([1.7, 1])

with col_feed:
    if not transacoes:
        st.markdown('<div class="k-card"><div class="k-card-b"><span class="muted">Nenhuma transação no período.</span></div></div>',
                    unsafe_allow_html=True)
    else:
        # Group by date
        from collections import defaultdict
        by_date: dict = defaultdict(list)
        for t in transacoes[:40]:
            by_date[t.date].append(t)

        feed_html = '<div class="k-feed">'
        for d, txs in sorted(by_date.items(), reverse=True):
            d_label = "hoje" if d == hoje else "ontem" if (hoje - d).days == 1 else d.strftime("%d/%m")
            net = sum((t.amount if t.type == TransactionType.GANHO else -t.amount) for t in txs)
            net_str = fmt_brl(net, compact=True)
            net_cls = "pos" if net >= 0 else "neg"
            feed_html += f"""<div class="k-feed-day">
  <div class="k-feed-day-h">{d_label}
    <span class="sub">{len(txs)} lançamento{"s" if len(txs) > 1 else ""}</span>
    <span class="sub mono {net_cls}">{net_str}</span>
  </div>
  <div class="k-feed-list">"""
            for t in txs:
                is_in = t.type == TransactionType.GANHO
                icon_map = {
                    "Alimentação": "◉", "Transporte": "➜", "Saúde": "♥",
                    "Lazer": "✦", "Moradia": "⌂", "Educação": "✎",
                    "Investimento": "◈", "Renda": "↗", "Freelance": "⌘", "Outros": "·",
                }
                icon = "↗" if is_in else icon_map.get(t.category.value, "·")
                icon_cls = "in" if is_in else "invest" if t.category.value == "Investimento" else "out"
                val_cls  = "pos" if is_in else "invest" if t.category.value == "Investimento" else ""
                val_sign = "+" if is_in else "−"
                meta_parts = [
                    f'<span class="mono" style="font-size:10.5px">{t.date.strftime("%H:%M") if hasattr(t.date, "strftime") else ""}</span>',
                    f'<span class="dot" style="width:3px;height:3px;background:var(--ink-4);border-radius:50%;display:inline-block"></span>',
                    f"<span>{t.category.value}</span>",
                    f'<span class="k-chip" style="padding:1px 6px;font-size:9px">{t.payment_method.value}</span>',
                ]
                feed_html += feed_row(
                    icon=icon, icon_cls=icon_cls,
                    title=t.notes[:40] if t.notes else t.category.value,
                    meta=" ".join(meta_parts),
                    value=f"{val_sign} {fmt_brl(t.amount, compact=True)}",
                    val_cls=val_cls,
                )
            feed_html += "</div></div>"
        feed_html += "</div>"
        st.markdown(f'<div class="k-card"><div class="k-card-b">{feed_html}</div></div>',
                    unsafe_allow_html=True)

with col_rail:
    # Insights
    top_cat = calcular_top_categorias(transacoes)
    insights = []
    if top_cat:
        biggest = top_cat[0]
        insights.append(("▲", "neg", biggest.category,
                         f"{fmt_brl(biggest.total)} · {biggest.percentual:.0f}% dos gastos"))
    if score.atingiu_meta_poupanca:
        insights.append(("✓", "pos", "Poupança em dia", f"{saldo.taxa_poupanca:.1f}% · meta ≥ 20%"))
    if violations > 0:
        insights.append(("!", "neg", "M2 alerta", f"{violations} violação{'ões' if violations > 1 else ''} detectada(s)"))
    if alertas_pad:
        a = alertas_pad[0]
        insights.append(("↑", "warn", f"{a.category} acima da média",
                         f"{fmt_brl(a.gasto_atual)} vs média {fmt_brl(a.media_3m)}"))
    if not insights:
        insights.append(("◉", "pos", "Tudo dentro do esperado", "Sem alertas no período"))

    ins_rows = ""
    for icon, tone, title, body in insights[:4]:
        color = {"pos": "var(--moss)", "neg": "var(--rust)", "warn": "var(--lantern)"}.get(tone, "var(--sea)")
        bg    = {"pos": "rgba(123,198,138,0.08)", "neg": "rgba(216,124,106,0.08)",
                 "warn": "rgba(244,213,141,0.08)"}.get(tone, "rgba(127,179,200,0.08)")
        ins_rows += f"""<div style="display:grid;grid-template-columns:24px 1fr;gap:10px;align-items:flex-start">
  <div style="width:24px;height:24px;border-radius:50%;display:flex;align-items:center;justify-content:center;
    font-family:var(--font-mono);font-size:13px;font-weight:600;color:{color};background:{bg};border:1px solid {color}">
    {icon}</div>
  <div>
    <div style="font-family:var(--font-sans);font-size:12.5px;color:var(--ink);font-weight:500;line-height:1.3">{title}</div>
    <div class="serif" style="font-size:12px;font-style:italic;color:var(--ink-3);margin-top:3px;line-height:1.45">{body}</div>
  </div>
</div>"""

    st.markdown(k_card_with_header(
        "Insights", f'<div style="display:flex;flex-direction:column;gap:12px;margin-top:6px">{ins_rows}</div>',
        hint="comportamento · 7d", gilt=True,
    ), unsafe_allow_html=True)

    # Patrimônio glance
    total_str = fmt_brl(total_portfolio + saldo.saldo, compact=True)
    st.markdown(k_card_with_header(
        "Patrimônio",
        f"""<div style="display:flex;align-items:center;justify-content:space-between;margin-top:4px">
  <div>
    <div class="mono" style="font-size:26px;line-height:1;color:var(--ink);font-variant-numeric:tabular-nums">{total_str}</div>
    <div class="mono" style="font-size:11px;color:var(--ink-3);margin-top:4px">{len(portfolio)} posições ativas</div>
  </div>
</div>
<div style="display:flex;gap:8px;margin-top:12px;flex-wrap:wrap">
  {chip(f"FII {fmt_brl(total_portfolio, compact=True)}", "brass")}
  {chip(f"Caixa {caixa_pct:.0f}%", "pos" if caixa_pct >= 20 else "neg")}
  {chip(f"Score {score.total}", "pos" if score.total >= 60 else "warn")}
</div>""",
        hint="snapshot · ver completo →",
    ), unsafe_allow_html=True)

    # Parcelamentos
    if installments:
        comp_map = calcular_comprometimento_mensal(installments)
        next_months = sorted(comp_map.keys())[:3]
        if next_months:
            rows_parc = ""
            for mk in next_months:
                rows_parc += f"""<div style="display:flex;justify-content:space-between;padding:8px 0;
                  border-top:1px solid var(--rule)">
                  <span class="mono muted" style="font-size:11px">{mk}</span>
                  <span class="mono brass-c" style="font-size:13px">{fmt_brl(comp_map[mk])}</span>
                </div>"""
            st.markdown(k_card_with_header(
                "Comprometimento futuro",
                f'<div style="margin-top:4px">{rows_parc}</div>',
                hint="parcelas ativas",
            ), unsafe_allow_html=True)
