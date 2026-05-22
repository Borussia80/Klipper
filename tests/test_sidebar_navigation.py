from __future__ import annotations

from pathlib import Path
from unittest.mock import Mock

import pytest

import core.styles as styles


def test_sidebar_nav_items_cover_all_product_pages():
    paths = [item.path for item in styles.SIDEBAR_NAV_ITEMS]

    assert paths == [
        "pages/1_Dashboard.py",
        "pages/2_Transacoes.py",
        "pages/6_Contas.py",
        "pages/7_Orcamento.py",
        "pages/3_Investimentos.py",
        "pages/8_Posicoes.py",
        "pages/9_Portfolio.py",
        "pages/4_Decisoes.py",
        "pages/12_Sobre.py",
        "pages/5_AI_Consilium.py",
        "pages/10_Saude.py",
        "pages/11_Extratos.py",
    ]


def test_sidebar_nav_paths_exist_in_repo():
    repo_root = Path(styles.__file__).resolve().parents[1]

    missing = [
        item.path for item in styles.SIDEBAR_NAV_ITEMS
        if not (repo_root / item.path).exists()
    ]

    assert missing == []


def test_sidebar_nav_renders_every_item(monkeypatch):
    rendered: list[tuple[str, str]] = []

    monkeypatch.setattr(styles.st, "markdown", Mock())
    monkeypatch.setattr(
        styles.st,
        "page_link",
        lambda path, label: rendered.append((path, label)),
    )

    styles.sidebar_nav()

    assert rendered == [
        (item.path, f"{item.icon}  {item.label}")
        for item in styles.SIDEBAR_NAV_ITEMS
    ]


def test_sidebar_nav_fails_loudly_when_streamlit_rejects_path(monkeypatch):
    monkeypatch.setattr(styles.st, "markdown", Mock())

    def reject_page_link(path: str, label: str) -> None:
        raise RuntimeError(f"invalid page path: {path}")

    monkeypatch.setattr(styles.st, "page_link", reject_page_link)

    with pytest.raises(RuntimeError, match="invalid page path"):
        styles.sidebar_nav()


def test_pages_require_auth_before_rendering_sidebar():
    repo_root = Path(styles.__file__).resolve().parents[1]
    offenders: list[str] = []

    for page in sorted((repo_root / "pages").glob("*.py")):
        text = page.read_text()
        auth_pos = text.find("require_auth()")
        sidebar_pos = text.find("with st.sidebar")
        if auth_pos != -1 and sidebar_pos != -1 and sidebar_pos < auth_pos:
            offenders.append(page.relative_to(repo_root).as_posix())

    assert offenders == []


def test_css_hides_native_streamlit_nav_and_keeps_custom_page_links():
    css = styles.KLIPPER_CSS

    assert '[data-testid="stSidebarNavItems"]' in css
    assert 'display: none !important' in css
    assert '[data-testid="stPageLink-NavLink"]' in css
