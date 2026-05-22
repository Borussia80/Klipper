"""Consilium · Klipper — M4 AI multi-provider com contexto WikiAgent."""

from __future__ import annotations

import os
from typing import Any

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from core.anti_bs import PERGUNTA_OBRIGATORIA
from core.m3_context import Confidence, MarketRegime
from core.repositories import InvestmentRepository, DecisionRepository
from core.auth import require_auth
from core.styles import (
    inject_css, section_header, k_card_with_header,
    sidebar_brand, sidebar_engines, sidebar_user, sidebar_nav, chip, load_page_icon,
)

st.set_page_config(page_title="Consilium · Klipper", page_icon=load_page_icon(), layout="wide")
inject_css()
require_auth()

PROVIDERS = {
    "auto (Claude → Gemini → GPT-4o → Qwen)": "auto",
    "Claude (Anthropic)": "claude",
    "Gemini (Google)": "gemini",
    "GPT-4o (OpenAI)": "gpt4o",
    "Qwen (DashScope)": "qwen",
    "Kimi (Moonshot)": "kimi",
}

MODEL_MAP = {
    "claude":  "claude-sonnet-4-6",
    "gemini":  "gemini/gemini-2.0-flash",
    "gpt4o":   "gpt-4o",
    "qwen":    "openai/qwen-plus",
    "kimi":    "openai/moonshot-v1-8k",
}

PROVIDER_CHIPS = {
    "claude": "brass", "gemini": "pos", "gpt4o": "", "qwen": "", "kimi": "",
}

SYSTEM_PROMPT = """Você é M4 — Auditoria Histórica do WikiAgent Financeiro Klipper.

Diretrizes absolutas:
- Matemática ancora. Narrativa sem evidência quantitativa não altera decisão.
- Contexto modula risco — nunca compra ativo sozinho.
- Sem verborreia. Resposta máxima: 300 palavras.
- Declarar incerteza SEMPRE que dados forem insuficientes.
- Reportar riscos antes de oportunidades.
- P/VP sozinho não valida ativo. DY alto exige validação de sustentabilidade.

WikiAgent M1 Thresholds:
- Score ≥ 0.60 → COMPRAR | 0.30–0.59 → MANTER | < 0.30 → REDUZIR

M2 Limites (Beginner Mode):
- Max por ativo: 10% | Max por tese/setor: 25% | Caixa mínimo: 20%

Anti-BS pergunta obrigatória: "{pergunta}"
""".format(pergunta=PERGUNTA_OBRIGATORIA)


def _resolve_model(provider_key: str) -> str:
    if provider_key == "auto":
        for p in ["claude", "gemini", "gpt4o", "qwen", "kimi"]:
            key_env = {
                "claude": "ANTHROPIC_API_KEY",
                "gemini": "GOOGLE_API_KEY",
                "gpt4o": "OPENAI_API_KEY",
                "qwen": "DASHSCOPE_API_KEY",
                "kimi": "MOONSHOT_API_KEY",
            }[p]
            if os.environ.get(key_env):
                return MODEL_MAP[p]
        return MODEL_MAP["gemini"]
    return MODEL_MAP.get(provider_key, MODEL_MAP["claude"])


def _chamar_litellm(model: str, mensagem: str) -> str:
    try:
        import litellm
        litellm.drop_params = True
        resp = litellm.completion(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": mensagem},
            ],
            max_tokens=600,
            temperature=0.3,
        )
        return resp.choices[0].message.content or ""
    except ImportError:
        return "LiteLLM não instalado. Execute: pip install litellm"
    except Exception as e:
        return f"Erro ao consultar {model}: {e}"


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(sidebar_brand(), unsafe_allow_html=True)
    sidebar_nav()

    st.markdown(
        '<div style="padding:6px 12px 2px;font-family:var(--font-sans);font-size:9.5px;'
        'letter-spacing:0.16em;text-transform:uppercase;color:var(--ink-4);font-weight:600">'
        'M4 · Provider</div>',
        unsafe_allow_html=True,
    )
    provider_label   = st.selectbox("Provider", list(PROVIDERS.keys()),
                                     label_visibility="collapsed")
    provider_key     = PROVIDERS[provider_label]
    regime           = st.selectbox("Regime M3 atual", [r.value for r in MarketRegime],
                                     label_visibility="collapsed")
    confidence       = st.selectbox("Confidence", [c.value for c in Confidence], index=2,
                                     label_visibility="collapsed")

    st.markdown(
        '<div style="padding:8px 12px;font-family:var(--font-mono);font-size:10px;color:var(--ink-4)">'
        'Configure API keys no arquivo <code>.env</code></div>',
        unsafe_allow_html=True,
    )
    st.markdown(sidebar_engines(), unsafe_allow_html=True)
    sidebar_user()

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown(section_header("Consilium · M4", "auditoria histórica · multi-provider"), unsafe_allow_html=True)

# Provider pills
active_key = provider_key if provider_key != "auto" else "claude"
provider_pills = " ".join(
    chip(f"{'◉ ' if k == active_key else ''}{k}", PROVIDER_CHIPS.get(k, ""))
    for k in ["claude", "gemini", "gpt4o", "qwen", "kimi"]
)
st.markdown(
    f'<div style="display:flex;gap:6px;flex-wrap:wrap;margin-bottom:16px;align-items:center">'
    f'<span class="mono muted" style="font-size:10px;letter-spacing:0.12em;text-transform:uppercase">provider</span>'
    f'{provider_pills}'
    f'</div>',
    unsafe_allow_html=True,
)

st.markdown(
    f'<div class="mono muted" style="font-size:10px;font-style:italic;margin-bottom:20px">'
    f'{PERGUNTA_OBRIGATORIA}</div>',
    unsafe_allow_html=True,
)

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "Análise de Tese",
    "Atualizar Regime M3",
    "Auditar Decision",
    "Análise de Portfólio",
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — Análise de Tese
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    col1, col2 = st.columns([1, 2], gap="large")
    with col1:
        ticker_t1 = st.text_input("Ticker", key="t1_ticker").upper()
        score_m1  = st.number_input("Score M1", 0.0, 1.0, step=0.01, format="%.4f", key="t1_score")
        dy        = st.number_input("DY 12m (%)", 0.0, 50.0, step=0.1, key="t1_dy")
        pvp       = st.number_input("P/VP", 0.0, 5.0, step=0.01, format="%.4f", key="t1_pvp")
    with col2:
        tese = st.text_area("Descreva a tese de investimento", height=150, key="t1_tese")

    if st.button("Analisar tese", type="primary", key="btn_t1"):
        if not tese:
            st.error("Descreva a tese primeiro.")
        else:
            prompt = f"""
Ativo: {ticker_t1}
Score M1: {score_m1:.4f}
DY 12m: {dy:.1f}%
P/VP: {pvp:.4f}
Regime M3: {regime} (Confidence: {confidence})

Tese do investidor:
{tese}

Análise M4 solicitada:
1. A tese tem suporte quantitativo (M1 score)?
2. Quais riscos Anti-BS identificados?
3. O regime M3 altera a prudência? Como?
4. Decisão recomendada: COMPRAR / MANTER / REDUZIR?
5. Declare incerteza onde dados são insuficientes.
"""
            with st.spinner("Consultando M4..."):
                model    = _resolve_model(provider_key)
                resposta = _chamar_litellm(model, prompt)

            tese_preview = tese[:220] + ("…" if len(tese) > 220 else "")
            resp_html = (
                f'<div class="serif" style="font-style:italic;font-size:16px;color:var(--ink);'
                f'line-height:1.55;margin-bottom:16px;padding-bottom:14px;border-bottom:1px solid var(--rule)">'
                f'&#8220;{tese_preview}&#8221;</div>'
                f'<div style="font-family:var(--font-sans);font-size:13px;color:var(--ink-2);'
                f'line-height:1.65;white-space:pre-wrap">{resposta}</div>'
                f'<div style="margin-top:14px;font-family:var(--font-mono);font-size:10px;color:var(--ink-4)">'
                f'model: {model}</div>'
            )
            st.markdown(k_card_with_header("Resposta M4", resp_html, model, gilt=True), unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — Atualizar Regime M3
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown(
        '<div style="font-family:var(--font-sans);font-size:12px;color:var(--ink-3);margin-bottom:12px">'
        'Cole contexto de mercado atual. A IA sugere o regime e confidence.</div>',
        unsafe_allow_html=True,
    )
    contexto_mercado = st.text_area(
        "Contexto de mercado (notícias, dados, eventos)", height=200, key="t2_ctx",
        label_visibility="collapsed",
    )

    if st.button("Sugerir regime", type="primary", key="btn_t2"):
        if not contexto_mercado:
            st.error("Cole contexto de mercado primeiro.")
        else:
            prompt = f"""
Contexto de mercado atual:
{contexto_mercado}

Com base neste contexto, indique:
1. Regime M3 mais adequado: RISK_ON | RISK_OFF | CREDIT_STRESS | LIQUIDITY_CRISIS | EUPHORIA
2. Confidence: VERY_LOW | LOW | MODERATE | HIGH | CRITICAL
3. Justificativa em 3 pontos máximo (dados concretos).
4. Declare incerteza se contexto for insuficiente.

Formato da resposta:
REGIME: [regime]
CONFIDENCE: [confidence]
JUSTIFICATIVA: [3 pontos]
INCERTEZA: [o que não foi possível avaliar]
"""
            with st.spinner("Consultando M4..."):
                model    = _resolve_model(provider_key)
                resposta = _chamar_litellm(model, prompt)

            resp_html = f"""<div style="font-family:var(--font-mono);font-size:13px;color:var(--ink-2);
  line-height:1.7;white-space:pre-wrap">{resposta}</div>
<div style="margin-top:14px;font-family:var(--font-mono);font-size:10px;color:var(--ink-4)">
  model: {model}
</div>"""
            st.markdown(k_card_with_header("Sugestão M4", resp_html, model, gilt=True), unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — Auditar Decision Template
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    try:
        decisions = DecisionRepository().list_all()
        if decisions:
            dec_labels = {
                f"{d.ticker} — {d.date} — {d.outcome.value if d.outcome else 'N/A'}": d
                for d in decisions
            }
            sel_label = st.selectbox("Selecione uma decisão para auditar", list(dec_labels.keys()),
                                      label_visibility="collapsed")
            dec_sel   = dec_labels[sel_label]

            if st.button("Auditar com M4", type="primary", key="btn_t3"):
                prompt = f"""
Decision Record para auditoria:
Ticker: {dec_sel.ticker}
Score M1: {dec_sel.score_m1}
Regime: {dec_sel.regime} | Confidence: {dec_sel.confidence}
Fragility: {dec_sel.fragility}
Decisão: {dec_sel.outcome.value if dec_sel.outcome else 'N/A'}
Invalidação: {dec_sel.invalidation_condition}

Tese: {dec_sel.thesis}
Risco: {dec_sel.risk}
Expectativa: {dec_sel.expectation}
Cenário alternativo: {dec_sel.alternative_scenario}

Auditoria M4:
1. A decisão tem suporte quantitativo suficiente?
2. Gaps identificados no Decision Template?
3. A condição de invalidação é clara e objetiva?
4. Aprovado / Revisão necessária / Bloqueado?
5. Declare incerteza onde aplicável.
"""
                with st.spinner("Auditando..."):
                    model    = _resolve_model(provider_key)
                    resposta = _chamar_litellm(model, prompt)

                resp_html = f"""<div style="font-family:var(--font-sans);font-size:13px;color:var(--ink-2);
  line-height:1.65;white-space:pre-wrap">{resposta}</div>
<div style="margin-top:14px;font-family:var(--font-mono);font-size:10px;color:var(--ink-4)">
  model: {model}
</div>"""
                st.markdown(k_card_with_header("Auditoria M4", resp_html, model, gilt=True), unsafe_allow_html=True)
        else:
            st.markdown(
                '<div style="padding:48px 0;text-align:center;color:var(--ink-4)">nenhuma decisão no Journal ainda</div>',
                unsafe_allow_html=True,
            )
    except Exception as e:
        st.error(f"Erro ao carregar decisions: {e}")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — Análise de Portfólio
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    try:
        portfolio = InvestmentRepository().get_portfolio()
        if portfolio:
            total = sum(inv.current_value for inv in portfolio)

            # Summary HTML
            pos_rows = "".join(
                f'<div style="display:flex;justify-content:space-between;font-family:var(--font-sans);'
                f'font-size:12px;padding:6px 0;border-top:1px solid var(--rule)">'
                f'<span style="color:var(--ink-2)">{inv.ticker} ({inv.type.value})</span>'
                f'<span class="mono" style="color:var(--ink)">{inv.current_value/total*100:.1f}% · '
                f'DY {inv.dy_12m:.1f}% · P/VP {inv.pvp:.2f}</span>'
                f'</div>'
                for inv in portfolio
            )
            st.markdown(k_card_with_header(
                "Portfólio", pos_rows,
                f"{len(portfolio)} ativos · total R$ {total:,.0f}",
            ), unsafe_allow_html=True)

            if st.button("Analisar portfólio com M4", type="primary", key="btn_t4"):
                resumo = "\n".join([
                    f"- {inv.ticker} ({inv.type.value}): {inv.current_value:.2f} "
                    f"({inv.current_value/total*100:.1f}%) | DY: {inv.dy_12m:.1f}% | "
                    f"P/VP: {inv.pvp:.2f} | Liquidez: R${inv.liquidity_daily:,.0f} | Setor: {inv.sector}"
                    for inv in portfolio
                ])
                prompt = f"""
Portfólio atual (regime: {regime}, confidence: {confidence}):
{resumo}

Análise M4 solicitada:
1. Concentração: algum ativo ou setor viola M2 (>10% / >25%)?
2. Ativos frágeis: baixa liquidez, DY suspeito, crédito ruim?
3. Sugestão de rebalanceamento (máximo 3 ações concretas)?
4. Coerência do portfólio com regime M3 atual?
5. Declare incerteza onde dados são insuficientes.
"""
                with st.spinner("Analisando portfólio..."):
                    model    = _resolve_model(provider_key)
                    resposta = _chamar_litellm(model, prompt)

                resp_html = f"""<div style="font-family:var(--font-sans);font-size:13px;color:var(--ink-2);
  line-height:1.65;white-space:pre-wrap">{resposta}</div>
<div style="margin-top:14px;font-family:var(--font-mono);font-size:10px;color:var(--ink-4)">
  model: {model}
</div>"""
                st.markdown(k_card_with_header("Análise M4", resp_html, model, gilt=True), unsafe_allow_html=True)
        else:
            st.markdown(
                '<div style="padding:48px 0;text-align:center;color:var(--ink-4)">portfólio vazio · adicione ativos na página Patrimônio</div>',
                unsafe_allow_html=True,
            )
    except Exception as e:
        st.error(f"Erro ao carregar portfólio: {e}")
