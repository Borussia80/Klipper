"""M4 — AI Consilium: análise multi-provider com contexto WikiAgent."""

from __future__ import annotations

import os
from typing import Any

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="AI Consilium · Klipper", page_icon="🤖", layout="wide")
st.title("🤖 AI Consilium — M4")
st.caption(
    "Matemática ancora. Contexto modula risco. "
    "Narrativa sem evidência não altera decisão. Sem verborreia. Declarar incerteza."
)

from core.anti_bs import PERGUNTA_OBRIGATORIA
from core.m3_context import Confidence, MarketRegime
from core.repositories import InvestmentRepository, DecisionRepository

# --- Provider selector ---
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
        return MODEL_MAP["gemini"]  # fallback
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


# --- Sidebar config ---
with st.sidebar:
    st.subheader("Configuração M4")
    provider_label = st.selectbox("Provider", list(PROVIDERS.keys()))
    provider_key = PROVIDERS[provider_label]
    regime = st.selectbox("Regime M3 atual", [r.value for r in MarketRegime])
    confidence = st.selectbox("Confidence", [c.value for c in Confidence], index=2)
    st.divider()
    st.caption("Configure as API keys no arquivo `.env`")

# --- Tabs por caso de uso ---
tab1, tab2, tab3, tab4 = st.tabs([
    "Análise de Tese",
    "Atualizar Regime M3",
    "Auditar Decision Template",
    "Análise de Portfólio",
])

# ──────────────────────────────────────────────────────────────
# Tab 1 — Análise de Tese
# ──────────────────────────────────────────────────────────────
with tab1:
    st.subheader("Análise de Tese de Investimento")

    col1, col2 = st.columns([1, 2])
    with col1:
        ticker_t1 = st.text_input("Ticker", key="t1_ticker").upper()
        score_m1 = st.number_input("Score M1", 0.0, 1.0, step=0.01, format="%.4f", key="t1_score")
        dy = st.number_input("DY 12m (%)", 0.0, 50.0, step=0.1, key="t1_dy")
        pvp = st.number_input("P/VP", 0.0, 5.0, step=0.01, format="%.4f", key="t1_pvp")
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
                model = _resolve_model(provider_key)
                resposta = _chamar_litellm(model, prompt)

            st.divider()
            st.markdown(f"**Resposta M4 ({model}):**")
            st.markdown(resposta)

# ──────────────────────────────────────────────────────────────
# Tab 2 — Atualizar Regime M3
# ──────────────────────────────────────────────────────────────
with tab2:
    st.subheader("Atualizar Regime M3")
    st.caption("Cole contexto de mercado atual. A IA sugere o regime e confidence.")

    contexto_mercado = st.text_area("Contexto de mercado (notícias, dados, eventos)", height=200, key="t2_ctx")

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
                model = _resolve_model(provider_key)
                resposta = _chamar_litellm(model, prompt)

            st.divider()
            st.markdown(f"**Sugestão M4 ({model}):**")
            st.markdown(resposta)

# ──────────────────────────────────────────────────────────────
# Tab 3 — Auditar Decision Template
# ──────────────────────────────────────────────────────────────
with tab3:
    st.subheader("Auditar Decision Template")

    try:
        decisions = DecisionRepository().list_all()
        if decisions:
            dec_labels = {
                f"{d.ticker} — {d.date} — {d.outcome.value if d.outcome else 'N/A'}": d
                for d in decisions
            }
            sel_label = st.selectbox("Selecione uma decisão para auditar", list(dec_labels.keys()))
            dec_sel = dec_labels[sel_label]

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
                    model = _resolve_model(provider_key)
                    resposta = _chamar_litellm(model, prompt)

                st.divider()
                st.markdown(f"**Auditoria M4 ({model}):**")
                st.markdown(resposta)
        else:
            st.info("Nenhuma decisão no Journal ainda.")
    except Exception as e:
        st.error(f"Erro ao carregar decisions: {e}")

# ──────────────────────────────────────────────────────────────
# Tab 4 — Análise de Portfólio
# ──────────────────────────────────────────────────────────────
with tab4:
    st.subheader("Análise de Portfólio Completo")

    try:
        portfolio = InvestmentRepository().get_portfolio()
        if portfolio:
            total = sum(inv.current_value for inv in portfolio)
            resumo = "\n".join([
                f"- {inv.ticker} ({inv.type.value}): {inv.current_value:.2f} "
                f"({inv.current_value/total*100:.1f}%) | DY: {inv.dy_12m:.1f}% | "
                f"P/VP: {inv.pvp:.2f} | Liquidez: R${inv.liquidity_daily:,.0f} | Setor: {inv.sector}"
                for inv in portfolio
            ])

            st.text(f"Portfólio carregado: {len(portfolio)} ativos | Total: R${total:,.2f}")

            if st.button("Analisar portfólio com M4", type="primary", key="btn_t4"):
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
                    model = _resolve_model(provider_key)
                    resposta = _chamar_litellm(model, prompt)

                st.divider()
                st.markdown(f"**Análise M4 ({model}):**")
                st.markdown(resposta)
        else:
            st.info("Portfólio vazio. Adicione ativos na página Investimentos.")
    except Exception as e:
        st.error(f"Erro ao carregar portfólio: {e}")
