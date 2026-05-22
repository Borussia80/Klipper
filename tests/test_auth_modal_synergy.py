"""
Testes de sinergia modal — autenticação + enrollment TOTP.

Invariante central: o fluxo de enrollment TOTP via settings dialog
NÃO deve alterar auth_mfa_step nem invalidar a sessão de um usuário
já autenticado. auth_* e settings_enroll_* são namespaces distintos.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest


# ── Fixtures ──────────────────────────────────────────────────────────────────

class _FakeSession(dict):
    """Dict que emula st.session_state (suporta .get/.pop/.keys/del)."""
    pass


@pytest.fixture()
def session() -> _FakeSession:
    return _FakeSession()


@pytest.fixture(autouse=True)
def mock_streamlit(session, monkeypatch):
    """Substitui st.session_state e funções de UI por fakes."""
    import streamlit as st

    monkeypatch.setattr(st, "session_state", session)
    monkeypatch.setattr(st, "rerun",   MagicMock())
    monkeypatch.setattr(st, "error",   MagicMock())
    monkeypatch.setattr(st, "success", MagicMock())
    monkeypatch.setattr(st, "info",    MagicMock())
    monkeypatch.setattr(st, "warning", MagicMock())
    return st


@pytest.fixture()
def logged_in_session(session) -> _FakeSession:
    """Sessão com usuário autenticado (sem MFA pendente)."""
    session["auth_user"] = {"id": "user-abc", "email": "teste@klipper.app"}
    return session


@pytest.fixture()
def mfa_pending_session(session) -> _FakeSession:
    """Sessão com MFA pendente (pós-login, aguardando código TOTP)."""
    session["auth_user"] = {"id": "user-abc", "email": "teste@klipper.app"}
    session["auth_mfa_step"] = "verify"
    session["auth_factor_id"] = "factor-123"
    session["auth_challenge_id"] = "challenge-456"
    return session


def _fake_supabase_client(
    *,
    enroll_id: str = "factor-new",
    enroll_secret: str = "SECRETBASE32",
    enroll_qr: str = "aGVsbG8=",
    verify_raises: Exception | None = None,
) -> MagicMock:
    """Retorna um mock do client Supabase configurado para enrollment."""
    totp_resp = MagicMock()
    totp_resp.totp.qr_code = enroll_qr
    totp_resp.totp.secret = enroll_secret
    totp_resp.id = enroll_id

    challenge_resp = MagicMock()
    challenge_resp.id = "challenge-789"

    client = MagicMock()
    client.auth.mfa.enroll.return_value = totp_resp
    client.auth.mfa.challenge.return_value = challenge_resp

    if verify_raises:
        client.auth.mfa.verify.side_effect = verify_raises
    else:
        client.auth.mfa.verify.return_value = MagicMock()

    client.auth.sign_out.return_value = None
    return client


# ── _is_authenticated ─────────────────────────────────────────────────────────

class TestIsAuthenticated:

    def test_retorna_true_com_usuario_e_sem_mfa_step(self, logged_in_session):
        from core.auth import _is_authenticated
        assert _is_authenticated() is True

    def test_retorna_false_sem_usuario(self, session):
        from core.auth import _is_authenticated
        assert _is_authenticated() is False

    def test_retorna_false_com_mfa_step_verify(self, mfa_pending_session):
        from core.auth import _is_authenticated
        assert _is_authenticated() is False

    def test_settings_enroll_keys_nao_afetam_autenticacao(self, logged_in_session):
        """settings_enroll_* devem ser invisíveis para _is_authenticated."""
        from core.auth import _is_authenticated
        logged_in_session["settings_enroll_factor_id"] = "factor-new"
        logged_in_session["settings_enroll_qr"] = "aGVsbG8="
        logged_in_session["settings_enroll_secret"] = "SECRETBASE32"
        assert _is_authenticated() is True

    def test_ausencia_de_auth_user_retorna_false(self, session):
        from core.auth import _is_authenticated
        session["auth_mfa_step"] = "verify"  # sem auth_user
        assert _is_authenticated() is False


# ── cancel_totp_enrollment ────────────────────────────────────────────────────

class TestCancelTotpEnrollment:

    def test_remove_apenas_settings_enroll_keys(self, logged_in_session):
        """cancel_totp_enrollment limpa settings_enroll_* e preserva auth_*."""
        from core.auth import cancel_totp_enrollment

        logged_in_session["settings_enroll_factor_id"] = "factor-xyz"
        logged_in_session["settings_enroll_qr"] = "aGVsbG8="
        logged_in_session["settings_enroll_secret"] = "SUPERSECRET"

        cancel_totp_enrollment()

        assert "settings_enroll_factor_id" not in logged_in_session
        assert "settings_enroll_qr" not in logged_in_session
        assert "settings_enroll_secret" not in logged_in_session

    def test_preserva_sessao_autenticada_apos_cancelar(self, logged_in_session):
        """Usuário continua autenticado após cancelar enrollment."""
        from core.auth import _is_authenticated, cancel_totp_enrollment

        logged_in_session["settings_enroll_factor_id"] = "factor-xyz"
        cancel_totp_enrollment()

        assert _is_authenticated() is True

    def test_cancelar_sem_enrollment_em_curso_e_idempotente(self, logged_in_session):
        """cancel_totp_enrollment não falha se chamada sem enrollment ativo."""
        from core.auth import _is_authenticated, cancel_totp_enrollment
        cancel_totp_enrollment()  # não deve levantar exceção
        assert _is_authenticated()

    def test_nao_remove_auth_keys(self, mfa_pending_session):
        """cancel_totp_enrollment não deve alterar auth_* keys."""
        from core.auth import cancel_totp_enrollment

        mfa_pending_session["settings_enroll_factor_id"] = "factor-xyz"
        cancel_totp_enrollment()

        assert mfa_pending_session.get("auth_mfa_step") == "verify"
        assert mfa_pending_session.get("auth_factor_id") == "factor-123"
        assert mfa_pending_session.get("auth_challenge_id") == "challenge-456"


# ── start_totp_enrollment (sinergia) ─────────────────────────────────────────

class TestStartTotpEnrollmentSinergy:

    def test_enrollment_usa_settings_keys_nao_auth_mfa_step(self, logged_in_session):
        """INVARIANTE CENTRAL: enrollment via settings nunca toca em auth_mfa_step."""
        from core.auth import start_totp_enrollment

        client = _fake_supabase_client()
        with patch("core.auth._supabase", return_value=client):
            start_totp_enrollment()

        assert "auth_mfa_step" not in logged_in_session
        assert logged_in_session.get("settings_enroll_factor_id") == "factor-new"

    def test_usuario_continua_autenticado_durante_enrollment(self, logged_in_session):
        """_is_authenticated() deve retornar True enquanto enrollment está em curso."""
        from core.auth import _is_authenticated, start_totp_enrollment

        client = _fake_supabase_client()
        with patch("core.auth._supabase", return_value=client):
            start_totp_enrollment()

        assert _is_authenticated() is True

    def test_enrollment_preenche_qr_e_secret(self, logged_in_session):
        from core.auth import start_totp_enrollment

        client = _fake_supabase_client(
            enroll_qr="cXJfY29kZQ==", enroll_secret="MYBASE32SECRET"
        )
        with patch("core.auth._supabase", return_value=client):
            start_totp_enrollment()

        assert logged_in_session["settings_enroll_qr"] == "cXJfY29kZQ=="
        assert logged_in_session["settings_enroll_secret"] == "MYBASE32SECRET"

    def test_enrollment_com_supabase_falho_nao_seta_settings_keys(self, logged_in_session):
        """Se Supabase falhar, nenhuma chave de enrollment é gravada."""
        from core.auth import start_totp_enrollment

        client = MagicMock()
        client.auth.mfa.enroll.side_effect = RuntimeError("network error")

        with patch("core.auth._supabase", return_value=client):
            start_totp_enrollment()

        assert "settings_enroll_factor_id" not in logged_in_session


# ── confirm_totp_enrollment ───────────────────────────────────────────────────

class TestConfirmTotpEnrollment:

    def _setup_enrollment(self, session):
        session["settings_enroll_factor_id"] = "factor-new"
        session["settings_enroll_qr"] = "aGVsbG8="
        session["settings_enroll_secret"] = "SECRETBASE32"

    def test_confirmacao_bem_sucedida_limpa_settings_keys(self, logged_in_session):
        from core.auth import confirm_totp_enrollment

        self._setup_enrollment(logged_in_session)
        client = _fake_supabase_client()

        with patch("core.auth._supabase", return_value=client):
            ok, err = confirm_totp_enrollment("123456")

        assert ok is True
        assert err == ""
        assert "settings_enroll_factor_id" not in logged_in_session

    def test_confirmacao_bem_sucedida_preserva_sessao(self, logged_in_session):
        """Após confirmar enrollment, usuário continua autenticado."""
        from core.auth import _is_authenticated, confirm_totp_enrollment

        self._setup_enrollment(logged_in_session)
        client = _fake_supabase_client()

        with patch("core.auth._supabase", return_value=client):
            ok, _ = confirm_totp_enrollment("123456")

        assert ok is True
        assert _is_authenticated() is True

    def test_codigo_incorreto_retorna_false_com_mensagem(self, logged_in_session):
        from core.auth import confirm_totp_enrollment

        self._setup_enrollment(logged_in_session)
        client = _fake_supabase_client(verify_raises=RuntimeError("invalid code"))

        with patch("core.auth._supabase", return_value=client):
            ok, err = confirm_totp_enrollment("000000")

        assert ok is False
        assert "incorreto" in err.lower()

    def test_codigo_incorreto_nao_altera_settings_keys(self, logged_in_session):
        """Falha na verificação mantém enrollment ativo para nova tentativa."""
        from core.auth import confirm_totp_enrollment

        self._setup_enrollment(logged_in_session)
        client = _fake_supabase_client(verify_raises=RuntimeError("bad code"))

        with patch("core.auth._supabase", return_value=client):
            confirm_totp_enrollment("000000")

        assert logged_in_session.get("settings_enroll_factor_id") == "factor-new"

    def test_sem_factor_id_em_sessao_retorna_false(self, logged_in_session):
        """confirm_totp_enrollment sem factor_id em sessão retorna erro limpo."""
        from core.auth import confirm_totp_enrollment

        with patch("core.auth._supabase", return_value=MagicMock()):
            ok, err = confirm_totp_enrollment("123456")

        assert ok is False
        assert len(err) > 0


# ── logout ────────────────────────────────────────────────────────────────────

class TestLogout:

    def test_logout_limpa_todas_auth_keys(self, logged_in_session):
        from core.auth import logout

        logged_in_session["auth_factor_id"] = "factor-abc"
        logged_in_session["auth_challenge_id"] = "challenge-xyz"

        client = MagicMock()
        with patch("core.auth._supabase", return_value=client):
            logout()

        auth_keys = [k for k in logged_in_session if k.startswith("auth_")]
        assert auth_keys == [], f"auth_* keys remanescentes: {auth_keys}"

    def test_logout_com_supabase_falho_ainda_limpa_sessao(self, logged_in_session):
        """logout() deve limpar sessão mesmo se sign_out falhar."""
        from core.auth import _is_authenticated, logout

        client = MagicMock()
        client.auth.sign_out.side_effect = RuntimeError("network error")

        with patch("core.auth._supabase", return_value=client):
            logout()

        assert _is_authenticated() is False

    def test_logout_nao_remove_settings_enroll_keys(self, logged_in_session):
        """_logout não deve interferir com keys de outras origens."""
        from core.auth import logout

        logged_in_session["settings_enroll_factor_id"] = "factor-xyz"

        client = MagicMock()
        with patch("core.auth._supabase", return_value=client):
            logout()

        # settings_enroll_* não começa com "auth_", não deve ser removida
        assert logged_in_session.get("settings_enroll_factor_id") == "factor-xyz"


# ── Ciclo completo ────────────────────────────────────────────────────────────

class TestCicloCompletoEnrollment:

    def test_ciclo_iniciar_confirmar_usuario_permanece_autenticado(self, logged_in_session):
        """
        Ciclo completo: usuário logado → inicia enrollment → confirma →
        permanece autenticado e sem resíduo de settings_enroll_*.
        """
        from core.auth import (
            _is_authenticated,
            confirm_totp_enrollment,
            start_totp_enrollment,
        )

        assert _is_authenticated()

        client = _fake_supabase_client()
        with patch("core.auth._supabase", return_value=client):
            start_totp_enrollment()
            assert _is_authenticated(), "autenticação perdida após iniciar enrollment"

            ok, _ = confirm_totp_enrollment("123456")

        assert ok is True
        assert _is_authenticated(), "autenticação perdida após confirmar enrollment"
        assert "settings_enroll_factor_id" not in logged_in_session

    def test_ciclo_iniciar_cancelar_usuario_permanece_autenticado(self, logged_in_session):
        """
        Ciclo: usuário logado → inicia enrollment → cancela →
        permanece autenticado sem residual.
        """
        from core.auth import (
            _is_authenticated,
            cancel_totp_enrollment,
            start_totp_enrollment,
        )

        client = _fake_supabase_client()
        with patch("core.auth._supabase", return_value=client):
            start_totp_enrollment()

        assert _is_authenticated()
        cancel_totp_enrollment()

        assert _is_authenticated()
        assert "settings_enroll_factor_id" not in logged_in_session

    def test_auth_mfa_step_nunca_e_definido_pelo_settings_enrollment(self, logged_in_session):
        """
        Nenhuma função do ciclo de settings enrollment toca em auth_mfa_step.
        auth_mfa_step só é definido pelo fluxo de LOGIN com TOTP já cadastrado.
        """
        from core.auth import (
            cancel_totp_enrollment,
            confirm_totp_enrollment,
            start_totp_enrollment,
        )

        client = _fake_supabase_client()
        with patch("core.auth._supabase", return_value=client):
            start_totp_enrollment()
            assert "auth_mfa_step" not in logged_in_session

            confirm_totp_enrollment("123456")
            assert "auth_mfa_step" not in logged_in_session

        logged_in_session["settings_enroll_factor_id"] = "factor-x"
        cancel_totp_enrollment()
        assert "auth_mfa_step" not in logged_in_session
