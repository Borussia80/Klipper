from __future__ import annotations

import streamlit as st

FINTECH_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
}

:root {
    --primary: #1E293B;
    --accent: #6366F1;
    --success: #10B981;
    --danger: #EF4444;
    --warning: #F59E0B;
    --surface: #F8FAFC;
    --card-bg: #FFFFFF;
    --border: #E2E8F0;
    --text-primary: #0F172A;
    --text-secondary: #64748B;
}

.klipper-card {
    background: var(--card-bg);
    border-radius: 12px;
    padding: 20px 24px;
    border: 1px solid var(--border);
    box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    margin-bottom: 12px;
}

.metric-card {
    background: linear-gradient(135deg, var(--card-bg) 0%, #F1F5F9 100%);
    border-radius: 16px;
    padding: 20px 20px 16px;
    border: 1px solid var(--border);
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    text-align: center;
}
.metric-label {
    font-size: 12px;
    font-weight: 600;
    color: var(--text-secondary);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 6px;
}
.metric-value {
    font-size: 26px;
    font-weight: 700;
    color: var(--text-primary);
    line-height: 1.1;
}
.metric-value.success { color: var(--success); }
.metric-value.danger  { color: var(--danger); }
.metric-value.accent  { color: var(--accent); }
.metric-sub {
    font-size: 11px;
    color: var(--text-secondary);
    margin-top: 4px;
}

.badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
}
.badge-comprar { background: #D1FAE5; color: #065F46; }
.badge-manter  { background: #FEF3C7; color: #92400E; }
.badge-reduzir { background: #FEE2E2; color: #991B1B; }
.badge-pago    { background: #D1FAE5; color: #065F46; }
.badge-pendente{ background: #FEF3C7; color: #92400E; }
.badge-agendado{ background: #DBEAFE; color: #1E40AF; }

.budget-bar-wrap { margin: 4px 0 12px; }
.budget-bar-bg {
    background: var(--border);
    border-radius: 4px;
    height: 8px;
    overflow: hidden;
}
.budget-bar-fill {
    height: 8px;
    border-radius: 4px;
    transition: width 0.3s ease;
}
.budget-ok      { background: var(--success); }
.budget-alerta  { background: var(--warning); }
.budget-estouro { background: var(--danger); }

.score-circle {
    width: 120px;
    height: 120px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-direction: column;
    margin: 0 auto;
    font-weight: 700;
    border: 6px solid var(--border);
}
.score-num {
    font-size: 36px;
    line-height: 1;
}
.score-label {
    font-size: 11px;
    color: var(--text-secondary);
    margin-top: 2px;
}

.pm-badge {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 12px;
    font-size: 11px;
    font-weight: 600;
    background: #EEF2FF;
    color: #4338CA;
}

.section-title {
    font-size: 16px;
    font-weight: 700;
    color: var(--text-primary);
    margin: 20px 0 10px;
    padding-bottom: 6px;
    border-bottom: 2px solid var(--accent);
    display: inline-block;
}
</style>
"""


def inject_css() -> None:
    st.markdown(FINTECH_CSS, unsafe_allow_html=True)


def metric_card(titulo: str, valor: str, subtitulo: str = "", cor: str = "") -> None:
    cor_class = f" {cor}" if cor else ""
    sub_html = f'<div class="metric-sub">{subtitulo}</div>' if subtitulo else ""
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{titulo}</div>
            <div class="metric-value{cor_class}">{valor}</div>
            {sub_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def budget_bar(category: str, gasto: float, limite: float) -> None:
    pct = min((gasto / limite * 100) if limite > 0 else 0, 100)
    status = "estouro" if pct >= 100 else "alerta" if pct >= 80 else "ok"
    st.markdown(
        f"""
        <div class="budget-bar-wrap">
            <div style="display:flex;justify-content:space-between;font-size:13px;margin-bottom:4px">
                <span style="font-weight:600">{category}</span>
                <span style="color:var(--text-secondary)">R$ {gasto:,.2f} / R$ {limite:,.2f}</span>
            </div>
            <div class="budget-bar-bg">
                <div class="budget-bar-fill budget-{status}" style="width:{pct:.1f}%"></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def score_circle(score: int) -> None:
    if score >= 80:
        color = "#10B981"
    elif score >= 50:
        color = "#F59E0B"
    else:
        color = "#EF4444"
    st.markdown(
        f"""
        <div class="score-circle" style="border-color:{color};">
            <span class="score-num" style="color:{color}">{score}</span>
            <span class="score-label">/ 100</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def payment_badge(method: str) -> str:
    icons = {
        "PIX": "⚡ PIX",
        "CARTAO_CREDITO": "💳 Crédito",
        "CARTAO_DEBITO": "💳 Débito",
        "DINHEIRO": "💵 Dinheiro",
        "TED": "🏦 TED",
        "BOLETO": "🧾 Boleto",
        "TRANSFERENCIA": "↔ Transf.",
    }
    label = icons.get(method, method)
    return f'<span class="pm-badge">{label}</span>'


def fmt_brl(valor: float) -> str:
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
