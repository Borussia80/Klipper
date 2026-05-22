"""Saúde · Klipper — tratamento TEA, reembolsos e fluxo com operadora."""

from __future__ import annotations

import html as _html
from datetime import date
from decimal import Decimal

import streamlit as st

from core.health_repository import (
    HealthProfessionalRepository,
    HealthSessionRepository,
    ReimbursementRequestRepository,
)
from core.auth import require_auth
from core.styles import (
    chip, fmt_brl, inject_css, k_card_with_header, load_page_icon,
    section_header, sidebar_user, sidebar_ai_qa, render_navigation, stat_card,
)
from models.health import (
    SPECIALTY_LABELS, STATUS_COLORS, STATUS_LABELS,
    HealthProfessional, HealthSession, ReimbursementRequest,
    ReimbursementStatus, Specialty,
)

st.set_page_config(page_title="Saúde · Klipper", page_icon=load_page_icon(), layout="wide")
inject_css()
require_auth()

prof_repo    = HealthProfessionalRepository()
session_repo = HealthSessionRepository()
req_repo     = ReimbursementRequestRepository()

hoje = date.today()

# ── Carregar dados ─────────────────────────────────────────────────────────────
try:
    profissionais  = prof_repo.list_active()
    sessoes_ano    = session_repo.list_by_year(hoje.year)
    sessoes_pend   = session_repo.list_pending(year=hoje.year)
    solicitacoes   = req_repo.list_all()
    db_ok          = True
except Exception as e:
    st.warning(f"Banco indisponível — {e}")
    profissionais, sessoes_ano, sessoes_pend, solicitacoes = [], [], [], []
    db_ok = False

# ── Índices auxiliares ─────────────────────────────────────────────────────────
prof_by_id: dict[str, HealthProfessional] = {p.id: p for p in profissionais}

def _prof_label(pid: str) -> str:
    p = prof_by_id.get(pid)
    if not p:
        return pid[:8]
    return f"{p.name} · {SPECIALTY_LABELS.get(p.specialty.value, p.specialty.value)}"

# ── KPIs ───────────────────────────────────────────────────────────────────────
total_pago_ano   = sum(s.amount_paid for s in sessoes_ano)
total_reembolsado = sum(
    (r.amount_received or Decimal(0))
    for r in solicitacoes
    if r.status in (ReimbursementStatus.REEMBOLSADO, ReimbursementStatus.PARCIAL)
)
# Saldo a reaver: sessões sem solicitação + gaps de solicitações abertas
saldo_a_reaver = sum(s.amount_paid for s in sessoes_pend if s.session_date.year == hoje.year)
saldo_a_reaver += sum(
    r.gap for r in solicitacoes
    if r.status in (ReimbursementStatus.PENDENTE, ReimbursementStatus.PARCIAL)
)
n_sem_solicitacao = len(sessoes_pend)

# ── Layout ────────────────────────────────────────────────────────────────────
nav_col, content_col = st.columns([1, 4])

with nav_col:
    st.markdown("""
<style>
section[data-testid="column"]:first-child {
    padding: 0.5rem 0.25rem !important;
    min-width: 80px;
}
section[data-testid="column"]:first-child button,
section[data-testid="column"]:first-child a {
    width: 100%;
    text-align: left;
    padding: 0.4rem 0.5rem;
    margin-bottom: 0.15rem;
    font-size: 0.82rem;
}
</style>
""", unsafe_allow_html=True)
    render_navigation()
    sidebar_user()
    sidebar_ai_qa()

with content_col:
    # ── Novo profissional form inline ─────────────────────────────────────────
    with st.expander("+ Novo profissional"):
        with st.form("form_prof"):
            pf1, pf2 = st.columns(2)
            with pf1:
                nome_p    = st.text_input("Nome*")
                espec_p   = st.selectbox("Especialidade*", options=list(SPECIALTY_LABELS.keys()),
                                         format_func=lambda k: SPECIALTY_LABELS[k])
            with pf2:
                conselho_p = st.text_input("N.º conselho (CRP / CREFITO / CRM…)")
            if st.form_submit_button("Cadastrar", use_container_width=True):
                if not nome_p:
                    st.error("Nome obrigatório")
                elif db_ok:
                    try:
                        prof_repo.create(HealthProfessional(
                            name=nome_p,
                            specialty=Specialty(espec_p),
                            council_number=conselho_p or None,
                        ))
                        st.success("Profissional cadastrado.")
                        st.rerun()
                    except Exception as ex:
                        st.error(str(ex))

    # ── Topbar ─────────────────────────────────────────────────────────────────
    st.markdown("""
<div style="display:flex;align-items:baseline;gap:14px;margin-bottom:4px">
  <span style="font-family:var(--font-sans);font-size:26px;font-weight:600;
    color:var(--ink);letter-spacing:-0.02em">Saúde</span>
  <span style="font-family:var(--font-sans);font-size:11px;letter-spacing:0.16em;
    text-transform:uppercase;color:var(--ink-3);font-weight:500">Pedro · TEA</span>
</div>
<div style="font-family:var(--font-sans);font-size:12px;color:var(--ink-3);
  margin-bottom:24px;line-height:1.5">
  Atendimentos pagos · solicitações de reembolso · fluxo com a operadora
</div>
""", unsafe_allow_html=True)

    # ── KPI strip ─────────────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(stat_card("Pago em " + str(hoje.year), fmt_brl(total_pago_ano),
                               sub=f"{len(sessoes_ano)} sessões"), unsafe_allow_html=True)
    with c2:
        st.markdown(stat_card("Reembolsado", fmt_brl(total_reembolsado),
                               sub="no ano", tone="pos"), unsafe_allow_html=True)
    with c3:
        tone = "warn" if saldo_a_reaver > 0 else ""
        st.markdown(stat_card("A reaver", fmt_brl(saldo_a_reaver),
                               sub="pendente + parcial", tone=tone), unsafe_allow_html=True)
    with c4:
        tone4 = "warn" if n_sem_solicitacao > 0 else ""
        st.markdown(stat_card("Sem solicitação", str(n_sem_solicitacao),
                               sub="sessões em aberto", tone=tone4), unsafe_allow_html=True)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # ── Tabs ───────────────────────────────────────────────────────────────────
    tab_sess, tab_sol, tab_prof = st.tabs(["Sessões", "Solicitações de reembolso", "Profissionais"])


    # ═══════════════════════════════════════════════════════════════════════════
    # TAB 1 — SESSÕES
    # ═══════════════════════════════════════════════════════════════════════════
    with tab_sess:

        # Filtros compactos
        fc1, fc2, fc3 = st.columns([2, 2, 1])
        with fc1:
            opcoes_prof = {"": "Todos os profissionais"} | {p.id: p.name for p in profissionais}
            filtro_prof = st.selectbox("Profissional", options=list(opcoes_prof.keys()),
                                        format_func=lambda k: opcoes_prof[k],
                                        label_visibility="collapsed")
        with fc2:
            filtro_status = st.selectbox(
                "Status",
                options=["todos", "sem_solicitacao", "em_solicitacao"],
                format_func={"todos": "Todos", "sem_solicitacao": "Sem solicitação",
                             "em_solicitacao": "Em solicitação"}.get,
                label_visibility="collapsed",
            )
        with fc3:
            filtro_ano = st.selectbox("Ano", options=[hoje.year, hoje.year - 1],
                                       label_visibility="collapsed")

        # Aplicar filtros
        sessoes_filtradas = session_repo.list_by_year(filtro_ano) if db_ok else []
        if filtro_prof:
            sessoes_filtradas = [s for s in sessoes_filtradas if s.professional_id == filtro_prof]
        if filtro_status == "sem_solicitacao":
            sessoes_filtradas = [s for s in sessoes_filtradas if s.is_pending]
        elif filtro_status == "em_solicitacao":
            sessoes_filtradas = [s for s in sessoes_filtradas if not s.is_pending]

        # Feed de sessões
        req_by_id = {r.id: r for r in solicitacoes}

        if not sessoes_filtradas:
            st.markdown('<div class="muted" style="padding:24px 0;text-align:center;font-size:13px">'
                        'Nenhuma sessão encontrada.</div>', unsafe_allow_html=True)
        else:
            rows_html = ""
            for s in sessoes_filtradas:
                prof_nome  = prof_by_id.get(s.professional_id)
                prof_label = _html.escape(prof_nome.name) if prof_nome else "—"
                spec_label = _html.escape(SPECIALTY_LABELS.get(
                    prof_nome.specialty.value, "")) if prof_nome else ""
                nf_html = (f' · NF {_html.escape(s.nf_number)}' if s.nf_number else "")
                nota_html = (
                    f'<div class="k-feed-note" style="margin-top:4px">{_html.escape(s.notes)}</div>'
                    if s.notes else ""
                )

                if s.is_pending:
                    badge = '<span style="font-size:9px;letter-spacing:0.08em;padding:2px 6px;' \
                            'border-radius:4px;background:rgba(244,213,141,0.1);' \
                            'border:1px solid rgba(244,213,141,0.3);color:var(--lantern)">SEM SOL.</span>'
                else:
                    req = req_by_id.get(s.reimbursement_request_id or "")
                    st_val = req.status.value if req else "?"
                    color  = STATUS_COLORS.get(st_val, "var(--ink-3)")
                    label  = STATUS_LABELS.get(st_val, st_val)
                    badge  = (f'<span style="font-size:9px;letter-spacing:0.08em;padding:2px 6px;'
                              f'border-radius:4px;background:{color}18;'
                              f'border:1px solid {color}50;color:{color}">{label.upper()}</span>')

                rows_html += f"""
<div class="k-feed-row" style="grid-template-columns:auto 1fr auto;gap:14px;align-items:start">
  <div style="padding-top:2px">{badge}</div>
  <div class="k-feed-body">
    <div class="k-feed-title">{prof_label}
      <span style="font-size:11px;color:var(--ink-3);font-weight:400"> · {spec_label}</span>
    </div>
    <div class="k-feed-meta">
      <span class="mono">{s.session_date.strftime("%d/%m/%Y")}</span>{nf_html}
    </div>
    {nota_html}
  </div>
  <div class="k-feed-val">{fmt_brl(s.amount_paid)}</div>
</div>"""

            st.markdown(f'<div class="k-feed">{rows_html}</div>', unsafe_allow_html=True)

        # ── Nova sessão ────────────────────────────────────────────────────────
        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
        with st.expander("+ Registrar nova sessão"):
            if not profissionais:
                st.info("Cadastre pelo menos um profissional usando o formulário acima antes de registrar sessões.")
            else:
                with st.form("form_sessao"):
                    sc1, sc2 = st.columns(2)
                    with sc1:
                        prof_sel = st.selectbox("Profissional*",
                                                 options=[p.id for p in profissionais],
                                                 format_func=lambda pid: (
                                                     f"{prof_by_id[pid].name} — "
                                                     f"{SPECIALTY_LABELS.get(prof_by_id[pid].specialty.value, '')}"
                                                     if pid in prof_by_id else pid))
                        data_sess = st.date_input("Data da sessão*", value=hoje)
                    with sc2:
                        valor_sess = st.number_input("Valor pago (R$)*", min_value=0.01, step=10.0, format="%.2f")
                        nf_sess    = st.text_input("N.º NF / recibo")
                    obs_sess = st.text_area("Observações", height=68)
                    if st.form_submit_button("Registrar sessão", use_container_width=True):
                        if not prof_sel or valor_sess <= 0:
                            st.error("Profissional e valor são obrigatórios.")
                        elif db_ok:
                            try:
                                session_repo.create(HealthSession(
                                    professional_id=prof_sel,
                                    session_date=data_sess,
                                    amount_paid=valor_sess,
                                    nf_number=nf_sess or None,
                                    notes=obs_sess or None,
                                ))
                                st.success("Sessão registrada.")
                                st.rerun()
                            except Exception as ex:
                                st.error(str(ex))


    # ═══════════════════════════════════════════════════════════════════════════
    # TAB 2 — SOLICITAÇÕES DE REEMBOLSO
    # ═══════════════════════════════════════════════════════════════════════════
    with tab_sol:

        # ── Lista de solicitações ─────────────────────────────────────────────
        if not solicitacoes:
            st.markdown('<div class="muted" style="padding:24px 0;text-align:center;font-size:13px">'
                        'Nenhuma solicitação registrada.</div>', unsafe_allow_html=True)
        else:
            st.markdown(section_header("Histórico", f"{len(solicitacoes)} solicitações"),
                        unsafe_allow_html=True)
            for req in solicitacoes:
                st_val  = req.status.value
                color   = STATUS_COLORS.get(st_val, "var(--ink-3)")
                label   = STATUS_LABELS.get(st_val, st_val)
                prot_html = (
                    f'<span class="mono" style="color:var(--sea)">#{_html.escape(req.protocol_number)}</span>'
                    if req.protocol_number else
                    '<span style="color:var(--ink-4);font-size:11px">sem protocolo</span>'
                )
                recv_html = fmt_brl(req.amount_received) if req.amount_received is not None else "—"
                gap_html  = (
                    f'<span class="mono warn" style="font-size:11px"> · gap {fmt_brl(req.gap)}</span>'
                    if req.gap > 0 else ""
                )
                nota_html = (
                    f'<div style="font-family:var(--font-serif);font-style:italic;'
                    f'font-size:12px;color:var(--ink-3);margin-top:6px">{_html.escape(req.notes)}</div>'
                    if req.notes else ""
                )

                st.markdown(f"""
<div class="k-feed-row" style="grid-template-columns:auto 1fr auto auto;
     gap:14px;align-items:start;margin-bottom:6px">
  <div style="padding-top:2px">
    <span style="font-size:9px;letter-spacing:0.08em;padding:2px 6px;border-radius:4px;
      background:{color}18;border:1px solid {color}50;color:{color}">{label.upper()}</span>
  </div>
  <div class="k-feed-body">
    <div class="k-feed-title">{_prof_label(req.professional_id)}</div>
    <div class="k-feed-meta">
      <span class="mono">{req.request_date.strftime("%d/%m/%Y")}</span> · {prot_html}
    </div>
    {nota_html}
  </div>
  <div style="text-align:right;flex-shrink:0">
    <div class="k-feed-val">{fmt_brl(req.amount_requested)}</div>
    <div style="font-family:var(--font-mono);font-size:11px;color:var(--ink-3);margin-top:2px">
      recebido: <span style="color:var(--moss)">{recv_html}</span>{gap_html}
    </div>
  </div>
</div>""", unsafe_allow_html=True)

        # ── Atualizar solicitação ─────────────────────────────────────────────
        sol_abertas = [r for r in solicitacoes
                       if r.status in (ReimbursementStatus.PENDENTE, ReimbursementStatus.PARCIAL)]
        if sol_abertas:
            st.markdown(section_header("Atualizar solicitação aberta"), unsafe_allow_html=True)
            with st.form("form_update_sol"):
                req_sel_id = st.selectbox(
                    "Solicitação*",
                    options=[r.id for r in sol_abertas],
                    format_func=lambda rid: (
                        f"{_prof_label(next((r.professional_id for r in sol_abertas if r.id == rid), ''))} "
                        f"· {next((r.request_date.strftime('%d/%m/%Y') for r in sol_abertas if r.id == rid), '')}"
                        f" · {fmt_brl(next((r.amount_requested for r in sol_abertas if r.id == rid), 0))}"
                    ),
                )
                uc1, uc2 = st.columns(2)
                with uc1:
                    novo_status = st.selectbox("Novo status*",
                                                options=[s.value for s in ReimbursementStatus],
                                                format_func=lambda v: STATUS_LABELS.get(v, v))
                    protocolo_u = st.text_input("Protocolo da operadora (se ainda não informado)")
                with uc2:
                    valor_recebido = st.number_input("Valor recebido (R$)", min_value=0.0,
                                                      step=10.0, format="%.2f")
                obs_u = st.text_area("Glosa / observações", height=68)
                if st.form_submit_button("Atualizar", use_container_width=True):
                    if db_ok:
                        try:
                            req_repo.update_status(
                                req_id=req_sel_id,
                                status=ReimbursementStatus(novo_status),
                                protocol_number=protocolo_u or None,
                                amount_received=valor_recebido if valor_recebido > 0 else None,
                                notes=obs_u or None,
                            )
                            st.success("Solicitação atualizada.")
                            st.rerun()
                        except Exception as ex:
                            st.error(str(ex))

        # ── Nova solicitação ──────────────────────────────────────────────────
        st.markdown(section_header("Nova solicitação de reembolso"), unsafe_allow_html=True)

        if not profissionais:
            st.info("Cadastre profissionais primeiro.")
        elif not sessoes_pend:
            st.info("Não há sessões sem solicitação. Registre atendimentos na aba Sessões.")
        else:
            with st.form("form_nova_sol"):
                nc1, nc2 = st.columns(2)
                with nc1:
                    profs_com_pend = list({s.professional_id for s in sessoes_pend
                                           if s.professional_id in prof_by_id})
                    prof_sol = st.selectbox(
                        "Profissional*",
                        options=profs_com_pend,
                        format_func=lambda pid: (
                            f"{prof_by_id[pid].name} — "
                            f"{SPECIALTY_LABELS.get(prof_by_id[pid].specialty.value, '')}"
                            if pid in prof_by_id else pid),
                    )
                    data_sol = st.date_input("Data da solicitação*", value=hoje)
                with nc2:
                    protocolo_n = st.text_input("Protocolo da operadora (pode preencher depois)")

                # Sessões disponíveis do profissional selecionado
                sess_do_prof = [s for s in sessoes_pend if s.professional_id == prof_sol]
                sess_opcoes  = {s.id: (f"{s.session_date.strftime('%d/%m/%Y')} · "
                                        f"{fmt_brl(s.amount_paid)}"
                                        + (f" · NF {s.nf_number}" if s.nf_number else ""))
                                for s in sess_do_prof}
                sel_sess_ids = st.multiselect(
                    "Sessões a incluir*",
                    options=list(sess_opcoes.keys()),
                    format_func=lambda sid: sess_opcoes.get(sid, sid),
                    default=list(sess_opcoes.keys()),
                )
                total_sol = sum(s.amount_paid for s in sess_do_prof if s.id in sel_sess_ids)

                st.markdown(
                    f'<div style="font-family:var(--font-sans);font-size:12px;color:var(--ink-3);'
                    f'margin-top:4px">Total solicitado: '
                    f'<span class="mono" style="color:var(--ink)">{fmt_brl(total_sol)}</span></div>',
                    unsafe_allow_html=True,
                )
                if st.form_submit_button("Criar solicitação", use_container_width=True):
                    if not sel_sess_ids:
                        st.error("Selecione ao menos uma sessão.")
                    elif db_ok:
                        try:
                            nova_req = ReimbursementRequest(
                                professional_id=prof_sol,
                                request_date=data_sol,
                                protocol_number=protocolo_n or None,
                                amount_requested=total_sol,
                            )
                            req_repo.create(nova_req)
                            session_repo.attach_to_request(sel_sess_ids, nova_req.id)
                            st.success(
                                f"Solicitação criada — {len(sel_sess_ids)} sessões · {fmt_brl(total_sol)}"
                            )
                            st.rerun()
                        except Exception as ex:
                            st.error(str(ex))


    # ═══════════════════════════════════════════════════════════════════════════
    # TAB 3 — PROFISSIONAIS
    # ═══════════════════════════════════════════════════════════════════════════
    with tab_prof:

        if not profissionais:
            st.markdown(
                '<div class="muted" style="padding:32px 0;text-align:center;font-size:13px">'
                'Nenhum profissional cadastrado. Use o formulário acima para adicionar.</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(section_header("Profissionais ativos", f"{len(profissionais)} cadastrados"),
                        unsafe_allow_html=True)

            for p in profissionais:
                spec_label  = _html.escape(SPECIALTY_LABELS.get(p.specialty.value, p.specialty.value))
                conselho_html = (
                    f'<span class="mono" style="font-size:11px;color:var(--ink-3)">'
                    f' · {_html.escape(p.council_number)}</span>'
                    if p.council_number else ""
                )
                # Sessões e valores do profissional
                sess_prof = [s for s in sessoes_ano if s.professional_id == p.id]
                total_prof = sum(s.amount_paid for s in sess_prof)
                n_sess     = len(sess_prof)

                st.markdown(f"""
<div class="k-feed-row" style="grid-template-columns:auto 1fr auto;gap:16px">
  <div style="width:40px;height:40px;border-radius:50%;display:flex;
    align-items:center;justify-content:center;font-family:var(--font-sans);
    font-size:14px;font-weight:600;background:var(--brass-soft);
    border:1px solid var(--rule-brass);color:var(--brass)">
    {_html.escape(p.name[0].upper())}
  </div>
  <div class="k-feed-body">
    <div class="k-feed-title">{_html.escape(p.name)}{conselho_html}</div>
    <div class="k-feed-meta">{spec_label}</div>
  </div>
  <div style="text-align:right">
    <div class="k-feed-val">{fmt_brl(total_prof)}</div>
    <div style="font-family:var(--font-mono);font-size:11px;color:var(--ink-3);margin-top:2px">
      {n_sess} sessão{'ões' if n_sess != 1 else ''} em {hoje.year}
    </div>
  </div>
</div>""", unsafe_allow_html=True)
