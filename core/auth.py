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
# auth_user               : dict | None  — dados do usuário (id, email)
# auth_mfa_step           : str | None   — "verify" | None
# auth_factor_id          : str | None   — ID do fator TOTP (verificação no login)
# auth_challenge_id       : str | None   — ID do desafio MFA atual
# settings_enroll_*       : str | None   — estado do enrollment via settings dialog


def require_auth() -> None:
    """
    Verifica autenticação. Deve ser chamada após st.set_page_config() e inject_css().

    Se não autenticado: popula o sidebar com brand (para ficar sempre visível),
    renderiza formulário de login na área principal e interrompe (st.stop()).
    Se autenticado: retorna imediatamente.
    """
    if _ensure_e2e_auth_user() or _is_authenticated():
        return

    if st.session_state.get("auth_mfa_step") == "verify":
        _render_totp_verify()
    else:
        _render_login()
    st.stop()


def _is_authenticated() -> bool:
    return bool(st.session_state.get("auth_user")) and not st.session_state.get("auth_mfa_step")


def _e2e_auth_enabled() -> bool:
    return os.environ.get("KLIPPER_E2E_AUTH") == "1"


def _ensure_e2e_auth_user() -> bool:
    if not _e2e_auth_enabled():
        return False
    st.session_state["auth_user"] = {
        "id": "e2e-user",
        "email": "e2e@klipper.local",
    }
    st.session_state.pop("auth_mfa_step", None)
    st.session_state.pop("auth_factor_id", None)
    st.session_state.pop("auth_challenge_id", None)
    return True


# ── Login ──────────────────────────────────────────────────────────────────────

def _render_login() -> None:
    _login_container()


def _login_container() -> None:
    from core.styles import _brand_b64, brand_icon_img

    lockup_uri = _brand_b64("klipper-lockup-dark.png")
    brand_html = (
        f'<img src="{lockup_uri}" class="k-auth-lockup" alt="Klipper">'
        if lockup_uri else
        f'<div class="k-auth-mark">{brand_icon_img(42)}<span>Klipper</span></div>'
    )

    st.markdown(f"""
<style>
[data-testid="stMainBlockContainer"] {{
  max-width:none !important;
  padding:0 !important;
}}
[data-testid="stAppViewContainer"] > .main {{
  background:var(--bg) !important;
}}
[data-testid="stForm"]:has([data-testid="stTextInput"]) {{
  width:min(100%, 390px);
  margin:-50vh 72px 0 auto;
  background:transparent !important;
  border:none !important;
  box-shadow:none !important;
  padding:0 !important;
}}
@media (max-width: 980px) {{
  [data-testid="stForm"]:has([data-testid="stTextInput"]) {{
    width:auto;
    margin:-8px 28px 0;
  }}
}}
</style>
<div class="k-auth-shell">
  <section class="k-auth-brand">
    <div class="k-auth-ambient"></div>
    <div class="k-auth-brand-inner">
      {brand_html}
      <div class="k-auth-kicker">Private wealth operating system</div>
      <h1>Discipline compounds wealth.</h1>
      <p>
        Mathematics anchors decisions. Context shapes risk. Klipper turns capital,
        commitments and behavior into one calm operating layer.
      </p>
      <div class="k-auth-proof">
        <span>Quant</span><span>Governance</span><span>Anti-BS</span><span>Fragility</span>
      </div>
    </div>
    <div class="k-auth-footer">
      <span>Clarity over noise</span>
      <span>43°10'W</span>
    </div>
  </section>
  <section class="k-auth-panel">
    <div class="k-auth-form-head">
      <div class="k-auth-kicker">Access layer</div>
      <h2>Enter Klipper</h2>
      <p>Your financial command center for capital, risk and discipline.</p>
    </div>
  </section>
</div>
""", unsafe_allow_html=True)

    with st.form("login_form"):
        email = st.text_input("E-mail", placeholder="seu@email.com")
        password = st.text_input("Senha", type="password", placeholder="••••••••")
        submitted = st.form_submit_button(
            "Access Wealth OS",
            type="primary",
            use_container_width=True,
        )

    st.markdown("""
<div class="k-auth-after">
  <span>Protected access</span>
  <span>Minimal surface. Maximum signal.</span>
</div>
""", unsafe_allow_html=True)

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
<style>
[data-testid="stMainBlockContainer"] { max-width:460px !important; padding-top:96px !important; }
</style>
<div class="k-auth-mfa">
  <div class="k-auth-kicker">Second factor</div>
  <h2>Verify access</h2>
  <p>Abra o aplicativo autenticador e informe o código de 6 dígitos.</p>
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
    """Inicia cadastro de TOTP a partir do settings dialog. Não altera auth_mfa_step."""
    try:
        client = _supabase()
        enroll = client.auth.mfa.enroll({"factor_type": "totp", "friendly_name": "Klipper"})
        st.session_state["settings_enroll_factor_id"] = enroll.id
        st.session_state["settings_enroll_qr"] = enroll.totp.qr_code   # base64 PNG
        st.session_state["settings_enroll_secret"] = enroll.totp.secret
        st.rerun()
    except Exception as e:
        log.warning("Erro ao iniciar cadastro TOTP: %s", e)
        st.error(f"Erro ao iniciar cadastro 2FA: {e}")


def confirm_totp_enrollment(code: str) -> tuple[bool, str]:
    """Confirma o código TOTP do enrollment em curso. Retorna (ok, mensagem_erro)."""
    try:
        factor_id = st.session_state["settings_enroll_factor_id"]
        client = _supabase()
        challenge = client.auth.mfa.challenge({"factor_id": factor_id})
        client.auth.mfa.verify({
            "factor_id": factor_id,
            "challenge_id": challenge.id,
            "code": code,
        })
        cancel_totp_enrollment()
        return True, ""
    except Exception as e:
        log.warning("Falha na confirmação de enrollment TOTP: %s", e)
        return False, "Código incorreto. Tente novamente."


def cancel_totp_enrollment() -> None:
    """Cancela enrollment em curso e limpa chaves de sessão."""
    for key in ("settings_enroll_factor_id", "settings_enroll_qr", "settings_enroll_secret"):
        st.session_state.pop(key, None)


# ── Logout ─────────────────────────────────────────────────────────────────────

def logout() -> None:
    """Encerra a sessão e limpa o estado."""
    try:
        _supabase().auth.sign_out()
    except Exception as e:
        log.warning("Erro ao fazer sign_out no Supabase: %s", e)
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
