"""core/auth.py — Autenticação Supabase com TOTP opcional (MFA AAL2)."""

from __future__ import annotations

import logging
import os

import streamlit as st

log = logging.getLogger(__name__)

# ── Supabase client ────────────────────────────────────────────────────────────

def _supabase():
    from supabase import create_client
    url = os.environ.get("SUPABASE_URL", "")
    key = os.environ.get("SUPABASE_KEY", "")
    if not url or not key:
        raise EnvironmentError("SUPABASE_URL e SUPABASE_KEY devem estar definidos.")
    return create_client(url, key)


# ── Estado de sessão ───────────────────────────────────────────────────────────
# auth_user          : dict | None  — dados do usuário (id, email)
# auth_mfa_step      : str | None   — "verify" | "enroll" | None
# auth_factor_id     : str | None   — ID do fator TOTP
# auth_challenge_id  : str | None   — ID do desafio MFA atual


def require_auth() -> None:
    """
    Verifica autenticação. Deve ser chamada após st.set_page_config() e inject_css().

    Se não autenticado: renderiza formulário de login e interrompe a página (st.stop()).
    Se aguardando TOTP: renderiza verificação e interrompe.
    Se autenticado: retorna imediatamente (sem overhead).
    """
    if _is_authenticated():
        return

    mfa_step = st.session_state.get("auth_mfa_step")
    if mfa_step == "verify":
        _render_totp_verify()
        st.stop()
    elif mfa_step == "enroll":
        _render_totp_enroll()
        st.stop()
    else:
        _render_login()
        st.stop()


def _is_authenticated() -> bool:
    return bool(st.session_state.get("auth_user")) and not st.session_state.get("auth_mfa_step")


# ── Login ──────────────────────────────────────────────────────────────────────

def _render_login() -> None:
    _login_container()


def _login_container() -> None:
    st.markdown("""
<div style="max-width:380px;margin:64px auto 0">
  <div style="text-align:center;margin-bottom:32px">
    <div style="font-family:var(--font-sans);font-size:22px;font-weight:600;color:var(--ink)">
      Klipper
    </div>
    <div style="font-family:var(--font-sans);font-size:12px;color:var(--ink-3);margin-top:4px;
      letter-spacing:0.12em;text-transform:uppercase">Wealth · operating system</div>
  </div>
</div>
""", unsafe_allow_html=True)

    with st.form("login_form"):
        email = st.text_input("E-mail", placeholder="seu@email.com")
        password = st.text_input("Senha", type="password", placeholder="••••••••")
        submitted = st.form_submit_button("Entrar", type="primary", use_container_width=True)

    if submitted:
        if not email or not password:
            st.error("Preencha e-mail e senha.")
            return
        _do_login(email.strip(), password)


def _do_login(email: str, password: str) -> None:
    try:
        client = _supabase()
        resp = client.auth.sign_in_with_password({"email": email, "password": password})
        user = resp.user

        st.session_state["auth_user"] = {"id": user.id, "email": user.email}

        # Verifica se há fatores TOTP cadastrados
        factors_resp = client.auth.mfa.list_factors()
        totp_factors = [
            f for f in (factors_resp.totp or [])
            if getattr(f, "status", None) == "verified"
        ]

        if totp_factors:
            factor_id = totp_factors[0].id
            challenge = client.auth.mfa.challenge({"factor_id": factor_id})
            st.session_state["auth_mfa_step"] = "verify"
            st.session_state["auth_factor_id"] = factor_id
            st.session_state["auth_challenge_id"] = challenge.id
            st.rerun()
        else:
            # Sem TOTP cadastrado — login direto (single-factor)
            st.session_state.pop("auth_mfa_step", None)
            st.rerun()

    except Exception as e:
        log.warning("Falha de login para %s: %s", email, e)
        st.error("E-mail ou senha incorretos.")


# ── TOTP — Verificação ─────────────────────────────────────────────────────────

def _render_totp_verify() -> None:
    st.markdown("""
<div style="max-width:380px;margin:64px auto 0;text-align:center">
  <div style="font-family:var(--font-sans);font-size:18px;font-weight:600;color:var(--ink);
    margin-bottom:8px">Verificação em dois fatores</div>
  <div style="font-family:var(--font-sans);font-size:12px;color:var(--ink-3);margin-bottom:24px">
    Abra o aplicativo autenticador e informe o código de 6 dígitos.
  </div>
</div>
""", unsafe_allow_html=True)

    with st.form("mfa_verify_form"):
        code = st.text_input("Código TOTP", max_chars=6, placeholder="000000")
        col1, col2 = st.columns(2)
        with col1:
            verify = st.form_submit_button("Verificar", type="primary", use_container_width=True)
        with col2:
            cancel = st.form_submit_button("Cancelar", use_container_width=True)

    if cancel:
        _logout()
        st.rerun()

    if verify:
        if not code or len(code) < 6:
            st.error("Código deve ter 6 dígitos.")
            return
        _do_totp_verify(code.strip())


def _do_totp_verify(code: str) -> None:
    try:
        client = _supabase()
        client.auth.mfa.verify({
            "factor_id": st.session_state["auth_factor_id"],
            "challenge_id": st.session_state["auth_challenge_id"],
            "code": code,
        })
        st.session_state.pop("auth_mfa_step", None)
        st.session_state.pop("auth_factor_id", None)
        st.session_state.pop("auth_challenge_id", None)
        st.rerun()
    except Exception as e:
        log.warning("Falha na verificação TOTP: %s", e)
        st.error("Código incorreto ou expirado.")


# ── TOTP — Cadastro ────────────────────────────────────────────────────────────

def start_totp_enrollment() -> None:
    """Inicia fluxo de cadastro de TOTP (chamar de settings dialog)."""
    try:
        client = _supabase()
        enroll = client.auth.mfa.enroll({"factor_type": "totp", "friendly_name": "Klipper"})
        st.session_state["auth_mfa_step"] = "enroll"
        st.session_state["auth_enroll_factor_id"] = enroll.id
        st.session_state["auth_enroll_qr"] = enroll.totp.qr_code   # base64 PNG
        st.session_state["auth_enroll_secret"] = enroll.totp.secret
        st.rerun()
    except Exception as e:
        st.error(f"Erro ao iniciar cadastro 2FA: {e}")


def _render_totp_enroll() -> None:
    qr_b64 = st.session_state.get("auth_enroll_qr", "")
    secret = st.session_state.get("auth_enroll_secret", "")

    st.markdown("""
<div style="max-width:420px;margin:40px auto 0;text-align:center">
  <div style="font-family:var(--font-sans);font-size:18px;font-weight:600;color:var(--ink);
    margin-bottom:8px">Ativar autenticação em dois fatores</div>
  <div style="font-family:var(--font-sans);font-size:12px;color:var(--ink-3);margin-bottom:20px">
    Escaneie o QR code com Google Authenticator, Authy ou similar.
  </div>
</div>
""", unsafe_allow_html=True)

    if qr_b64:
        st.markdown(
            f'<div style="text-align:center;margin-bottom:16px">'
            f'<img src="data:image/png;base64,{qr_b64}" width="200" '
            f'style="border-radius:8px;border:4px solid white" alt="QR Code TOTP"></div>',
            unsafe_allow_html=True,
        )
    if secret:
        st.markdown(
            f'<div style="text-align:center;font-family:var(--font-mono);font-size:12px;'
            f'color:var(--ink-3);margin-bottom:20px">Chave manual: <strong>{secret}</strong></div>',
            unsafe_allow_html=True,
        )

    with st.form("mfa_enroll_form"):
        code = st.text_input("Código de confirmação (6 dígitos)", max_chars=6, placeholder="000000")
        col1, col2 = st.columns(2)
        with col1:
            confirm = st.form_submit_button("Confirmar 2FA", type="primary", use_container_width=True)
        with col2:
            cancel = st.form_submit_button("Cancelar", use_container_width=True)

    if cancel:
        _cancel_enrollment()
        st.rerun()

    if confirm:
        if not code or len(code) < 6:
            st.error("Código deve ter 6 dígitos.")
            return
        _do_totp_enroll_confirm(code.strip())


def _do_totp_enroll_confirm(code: str) -> None:
    try:
        factor_id = st.session_state["auth_enroll_factor_id"]
        client = _supabase()
        challenge = client.auth.mfa.challenge({"factor_id": factor_id})
        client.auth.mfa.verify({
            "factor_id": factor_id,
            "challenge_id": challenge.id,
            "code": code,
        })
        _cancel_enrollment()
        st.success("2FA ativado com sucesso!")
        st.rerun()
    except Exception as e:
        log.warning("Falha na confirmação de enrollment TOTP: %s", e)
        st.error("Código incorreto. Tente novamente.")


def _cancel_enrollment() -> None:
    for key in ("auth_mfa_step", "auth_enroll_factor_id", "auth_enroll_qr", "auth_enroll_secret"):
        st.session_state.pop(key, None)


# ── Logout ─────────────────────────────────────────────────────────────────────

def logout() -> None:
    """Encerra a sessão e limpa o estado."""
    try:
        _supabase().auth.sign_out()
    except Exception:
        pass
    _logout()


def _logout() -> None:
    for key in list(st.session_state.keys()):
        if key.startswith("auth_"):
            del st.session_state[key]


# ── Settings helpers ───────────────────────────────────────────────────────────

def current_user_email() -> str:
    user = st.session_state.get("auth_user", {})
    return user.get("email", "roberto.milet@gmail.com")


def has_totp() -> bool:
    """Verifica se o usuário tem TOTP cadastrado."""
    try:
        factors = _supabase().auth.mfa.list_factors()
        return bool(
            factors.totp and any(
                getattr(f, "status", None) == "verified" for f in factors.totp
            )
        )
    except Exception:
        return False


def unenroll_totp() -> None:
    """Remove o fator TOTP cadastrado."""
    try:
        client = _supabase()
        factors = client.auth.mfa.list_factors()
        for f in (factors.totp or []):
            client.auth.mfa.unenroll({"factor_id": f.id})
    except Exception as e:
        raise RuntimeError(f"Erro ao remover 2FA: {e}") from e
