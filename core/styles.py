"""core/styles.py — Klipper nautical theme for Streamlit."""

from __future__ import annotations

import functools
import html as _html_mod
import re
from dataclasses import dataclass

import streamlit as st

html_escape = _html_mod.escape

# ──────────────────────────────────────────────────────────────────────────────
# CSS
# ──────────────────────────────────────────────────────────────────────────────

KLIPPER_CSS = """
<style>
/* ── Fonts ─────────────────────────────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Geist:wght@300;400;500;600;700&family=Inter+Tight:ital,wght@0,300;0,400;0,500;0,600;0,700;1,400&family=Instrument+Serif:ital@0;1&family=JetBrains+Mono:wght@400;500;600&display=swap');

/* ── Design tokens v3.0 ──────────────────────────────────────────────────────── */
:root {
  /* Colour layers — dark default */
  --bg:             #020617;
  --bg-deep:        #020617;
  --bg-2:           #07111D;
  --surface:        #07111D;
  --card:           #0D1726;
  --layer-active:   #132238;
  --layer-crit:     #1B2B45;

  /* Legacy surface aliases — kept for existing code */
  --surface-1:      rgba(255,255,255,0.03);
  --surface-2:      rgba(255,255,255,0.05);
  --surface-3:      rgba(255,255,255,0.08);
  --surface-tint:   rgba(59,130,246,0.04);

  /* Ink scale */
  --ink:            #F1F5F9;
  --ink-2:          #CBD5E1;
  --ink-3:          #94A3B8;
  --ink-4:          #475569;

  /* Borders */
  --rule:           rgba(255,255,255,0.07);
  --rule-2:         rgba(255,255,255,0.12);
  --rule-brass:     rgba(217,178,111,0.18);

  /* Brand & semantic palette */
  --brass:          #D9B26F;
  --brass-soft:     rgba(217,178,111,0.12);
  --brass-glow:     rgba(217,178,111,0.28);
  --sea:            #7FB3C8;
  --electric:       #3B82F6;
  --copper:         #F97316;
  --moss:           #34D399;
  --emerald:        #10B981;
  --emerald-soft:   rgba(16,185,129,0.12);
  --emerald-glow:   rgba(16,185,129,0.22);
  --rust:           #F87171;
  --lantern:        #FCD34D;

  /* Semantic states */
  --pos:            #10B981;
  --neg:            #F87171;
  --neg-expense:    #F87171;
  --warn:           #F59E0B;
  --accent:         #3B82F6;
  --danger:         #EF4444;
  --success:        #10B981;

  /* Gradients & shadows */
  --hero-bg:        linear-gradient(145deg, #020617 0%, #07111D 60%, #0D1726 100%);
  --hero-accent:    rgba(59,130,246,0.07);
  --shadow-1:       0 1px 0 rgba(255,255,255,0.03) inset, 0 4px 16px rgba(0,0,0,0.45);
  --shadow-2:       0 1px 0 rgba(255,255,255,0.04) inset, 0 10px 30px rgba(0,0,0,0.55);
  --glow-accent:    0 0 0 1px rgba(59,130,246,0.18), 0 0 24px rgba(59,130,246,0.08);
  --glow-brass:     0 0 0 1px rgba(217,178,111,0.12), 0 0 24px rgba(217,178,111,0.06);

  /* Fonts — Sprint 01 */
  --font-sans:      'Geist', 'Inter Tight', 'Inter', system-ui, sans-serif;
  --font-mono:      'JetBrains Mono', 'Geist Mono', 'IBM Plex Mono', monospace;
  --font-serif:     'Instrument Serif', Georgia, serif;

  /* Spacing tokens — Sprint 01 */
  --space-xs:  4px;
  --space-sm:  8px;
  --space-md:  12px;
  --space-lg:  16px;
  --space-xl:  24px;
  --space-xxl: 32px;

  /* Border radius — Sprint 01 */
  --radius-xs:    6px;
  --radius-sm:    10px;
  --radius-input: 14px;
  --radius:       16px;
  --radius-card:  20px;
  --radius-lg:    24px;
  --radius-hero:  28px;
  --radius-pill:  999px;
  --radius-fab:   999px;

  /* Transitions */
  --ease:    cubic-bezier(0.2,0.7,0.2,1);
  --t-fast:  120ms;
  --t-base:  180ms;
  --t-slow:  300ms;
}

/* ── Light mode v1 — professional neutral ───────────────────────────────────── */
@media (prefers-color-scheme: light) {
  :root {
    --bg:             #F4F7FA;
    --bg-deep:        #EBF0F5;
    --bg-2:           #FFFFFF;
    --surface:        #F9FAFB;
    --card:           #FFFFFF;
    --layer-active:   #EFF6FF;
    --layer-crit:     #DBEAFE;
    --surface-1:      rgba(0,0,0,0.02);
    --surface-2:      rgba(0,0,0,0.04);
    --surface-3:      rgba(0,0,0,0.07);
    --surface-tint:   rgba(29,78,216,0.03);
    --ink:            #111827;
    --ink-2:          #374151;
    --ink-3:          #6B7280;
    --ink-4:          #9CA3AF;
    --rule:           #E5E7EB;
    --rule-2:         #D1D5DB;
    --rule-brass:     rgba(29,78,216,0.12);
    --electric:       #1D4ED8;
    --accent:         #1D4ED8;
    --pos:            #10B981;
    --neg:            #EF4444;
    --neg-expense:    #EF4444;
    --warn:           #F59E0B;
    --danger:         #EF4444;
    --success:        #10B981;
    --hero-bg:        linear-gradient(145deg, #EFF6FF 0%, #F4F7FA 60%, #FFFFFF 100%);
    --hero-accent:    rgba(29,78,216,0.05);
    --shadow-1:       0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04);
    --shadow-2:       0 4px 12px rgba(0,0,0,0.08), 0 2px 4px rgba(0,0,0,0.04);
    --glow-accent:    0 0 0 1px rgba(29,78,216,0.14);
    --glow-brass:     0 0 0 1px rgba(29,78,216,0.10);
    --brass:          #B45309;
    --moss:           #059669;
    --emerald:        #059669;
    --emerald-soft:   rgba(5,150,105,0.10);
    --rust:           #EF4444;
    --lantern:        #D97706;
  }
}

@keyframes k-fade-up {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}
@keyframes k-gradient-drift {
  0%, 100% { transform: translate3d(-2%, -1%, 0) scale(1); opacity: 0.72; }
  50% { transform: translate3d(3%, 2%, 0) scale(1.06); opacity: 0.95; }
}

/* ── Streamlit global overrides ─────────────────────────────────────────────── */
html, body, [data-testid="stApp"] {
  background: var(--bg) !important;
  color: var(--ink) !important;
  font-family: var(--font-sans) !important;
  font-size: 13.5px !important;
  -webkit-font-smoothing: antialiased !important;
}

/* ambient radial glow */
[data-testid="stApp"]::before {
  content: '';
  position: fixed; inset: 0; z-index: 0; pointer-events: none;
  background:
    radial-gradient(circle at 18% -10%, rgba(217,178,111,0.07), transparent 45%),
    radial-gradient(circle at 90% 110%, rgba(127,179,200,0.06), transparent 55%);
  opacity: 0.9;
}

/* header */
[data-testid="stHeader"] {
  background: transparent !important;
  border-bottom: none !important;
}

/* ── Sidebar nativa ──────────────────────────────────────────────────────────── */
[data-testid="stSidebarNavSeparator"] { display: none !important; }
section[data-testid="stSidebar"] {
  background: var(--bg-deep) !important;
  border-right: 1px solid var(--rule-2) !important;
  min-width: 220px !important;
}
section[data-testid="stSidebar"] > div {
  background: var(--bg-deep) !important;
  padding: 0 !important;
}
/* botões page_link na sidebar */
section[data-testid="stSidebar"] a[data-testid="stPageLink"] {
  color: var(--ink-3) !important;
  font-family: var(--font-sans) !important;
  font-size: 12.5px !important;
  border-radius: var(--radius-xs) !important;
  padding: 0.35rem 0.5rem !important;
  transition: background 0.15s, color 0.15s !important;
}
section[data-testid="stSidebar"] a[data-testid="stPageLink"]:hover {
  background: var(--surface-2) !important;
  color: var(--ink) !important;
}
section[data-testid="stSidebar"] a[data-testid="stPageLink"][aria-current="page"] {
  background: var(--emerald-soft) !important;
  color: var(--emerald) !important;
}

/* ── Hero section ────────────────────────────────────────────────────────────── */
.k-hero {
  background: var(--hero-bg);
  border-radius: var(--radius-lg);
  padding: 28px 24px 32px;
  margin-bottom: 0;
  position: relative;
  overflow: hidden;
  border: 1px solid rgba(0,200,150,0.10);
}
.k-hero::before {
  content: '';
  position: absolute;
  top: -30%; left: -10%;
  width: 60%; height: 180%;
  background: radial-gradient(ellipse, rgba(0,200,150,0.13) 0%, transparent 70%);
  pointer-events: none;
}
.k-hero::after {
  content: '';
  position: absolute;
  bottom: -20%; right: -5%;
  width: 40%; height: 120%;
  background: radial-gradient(ellipse, rgba(77,141,255,0.07) 0%, transparent 65%);
  pointer-events: none;
}
.k-hero-balance {
  font-family: var(--font-serif);
  font-size: 38px;
  line-height: 1;
  letter-spacing: -0.02em;
  color: var(--ink);
  font-variant-numeric: tabular-nums;
  margin: 6px 0 16px;
}
.k-hero-kicker {
  font-family: var(--font-mono);
  font-size: 9px;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: var(--emerald);
  font-weight: 600;
}
.k-hero-stats-row {
  display: flex;
  align-items: center;
  gap: 20px;
}
.k-hero-stat {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.k-hero-stat-label {
  font-family: var(--font-sans);
  font-size: 10px;
  color: var(--ink-4);
  letter-spacing: 0.04em;
}
.k-hero-stat-val {
  font-family: var(--font-mono);
  font-size: 15px;
  font-weight: 600;
}
.k-hero-divider {
  width: 1px;
  background: rgba(255,255,255,0.08);
  align-self: stretch;
  margin: 0 4px;
}
.k-hero-progress-track {
  height: 4px;
  background: rgba(255,255,255,0.06);
  border-radius: 2px;
  overflow: hidden;
  margin-top: 18px;
}
.k-hero-progress-fill {
  height: 100%;
  border-radius: 2px;
  transition: width 0.4s var(--ease);
}

/* ── Rising card (conteúdo abaixo do hero) ───────────────────────────────────── */
.k-rising-card {
  background: var(--surface-1);
  border: 1px solid var(--rule);
  border-radius: var(--radius-lg);
  padding: 20px;
  margin-top: 12px;
}

/* ── Transaction row (referencial style) ─────────────────────────────────────── */
.k-tx-row {
  display: grid;
  grid-template-columns: 40px 1fr auto;
  align-items: center;
  gap: 12px;
  padding: 10px 0;
  border-top: 1px solid var(--rule);
}
.k-tx-row:first-child { border-top: none; padding-top: 0; }
.k-tx-icon {
  width: 38px; height: 38px;
  border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
  font-size: 15px;
  flex-shrink: 0;
}
.k-tx-body { min-width: 0; }
.k-tx-name {
  font-family: var(--font-sans);
  font-size: 13px;
  font-weight: 500;
  color: var(--ink);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.k-tx-meta {
  font-family: var(--font-sans);
  font-size: 10.5px;
  color: var(--emerald);
  margin-top: 1px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.k-tx-notes {
  font-family: var(--font-sans);
  font-size: 10px;
  color: var(--ink-4);
  margin-top: 1px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.k-tx-amount {
  font-family: var(--font-mono);
  font-size: 13px;
  font-weight: 600;
  text-align: right;
  white-space: nowrap;
}
.k-tx-amount.pos { color: var(--emerald); }
.k-tx-amount.neg { color: var(--electric); }
.k-tx-amount.warn { color: var(--warn); }

/* ── main content area ───────────────────────────────────────────────────────── */
[data-testid="stMainBlockContainer"] {
  padding-top: 16px !important;
  padding-bottom: 80px !important;
}
.main .block-container { max-width: 1440px !important; }

/* typography in markdown */
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li {
  color: var(--ink-2);
  font-family: var(--font-sans);
}

/* metrics */
[data-testid="metric-container"] {
  background: var(--surface-2) !important;
  border: 1px solid var(--rule) !important;
  border-radius: var(--radius) !important;
  padding: 16px 20px !important;
  box-shadow: var(--shadow-1) !important;
}
[data-testid="metric-container"] label {
  font-family: var(--font-sans) !important;
  font-size: 10.5px !important;
  letter-spacing: 0.12em !important;
  text-transform: uppercase !important;
  color: var(--ink-3) !important;
  font-weight: 600 !important;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
  font-family: var(--font-mono) !important;
  font-size: 26px !important;
  color: var(--ink) !important;
}

/* buttons */
.stButton > button {
  background: var(--surface-2) !important;
  border: 1px solid var(--rule) !important;
  color: var(--ink) !important;
  font-family: var(--font-sans) !important;
  font-size: 12px !important;
  border-radius: var(--radius-pill) !important;
  padding: 7px 14px !important;
  transition: all 140ms var(--ease) !important;
}
.stButton > button:hover {
  background: var(--surface-3) !important;
  border-color: var(--rule-2) !important;
}
.stButton > button[kind="primary"] {
  background: linear-gradient(180deg, var(--brass), #B8923D) !important;
  color: #1A1106 !important;
  border-color: transparent !important;
  font-weight: 600 !important;
  box-shadow: var(--glow-brass) !important;
}
.stButton > button[kind="primary"]:hover { filter: brightness(1.1) !important; }

/* inputs — seletores alto nível + BaseWeb (Streamlit usa ambos dependendo da versão) */
.stTextInput input,
.stNumberInput input,
.stTextArea textarea,
[data-baseweb="input"] input,
[data-baseweb="textarea"] textarea {
  background: var(--surface-2) !important;
  border: 1px solid var(--rule) !important;
  color: var(--ink) !important;
  border-radius: var(--radius-input) !important;
  font-family: var(--font-sans) !important;
}
/* container BaseWeb dos inputs (wraps o input real) */
[data-baseweb="input"],
[data-baseweb="textarea"] {
  background: var(--surface-2) !important;
  border: 1px solid var(--rule) !important;
  border-radius: var(--radius-sm) !important;
}
.stTextInput input:focus,
.stNumberInput input:focus,
.stTextArea textarea:focus,
[data-baseweb="input"] input:focus,
[data-baseweb="textarea"] textarea:focus {
  border-color: var(--brass) !important;
  box-shadow: 0 0 0 1px var(--brass) !important;
  outline: none !important;
}
/* Sprint 01B: placeholder accessibility — WCAG AA against dark bg */
.stTextInput input::placeholder,
.stNumberInput input::placeholder,
.stTextArea textarea::placeholder,
[data-baseweb="input"] input::placeholder {
  color: var(--ink-4) !important;
  opacity: 1 !important;
}
/* Sprint 01B: input focus glow — brass accent + shadow */
.stTextInput input:focus,
.stNumberInput input:focus,
.stTextArea textarea:focus {
  border-color: var(--brass) !important;
  box-shadow: 0 0 8px rgba(217,167,74,0.20) !important;
}
.stSelectbox [data-baseweb="select"] {
  background: var(--surface-2) !important;
  border: 1px solid var(--rule) !important;
  border-radius: var(--radius-sm) !important;
}
.stSelectbox [data-baseweb="select"] > div { background: transparent !important; color: var(--ink) !important; }
/* dropdown popover */
[data-baseweb="popover"] [role="listbox"],
[data-baseweb="menu"] {
  background: var(--surface-2) !important;
  border: 1px solid var(--rule) !important;
}
[data-baseweb="menu"] li { color: var(--ink) !important; }
[data-baseweb="menu"] li:hover { background: var(--surface-3, #1E3347) !important; }

/* form */
[data-testid="stForm"] {
  background: var(--surface-1) !important;
  border: 1px solid var(--rule) !important;
  border-radius: var(--radius) !important;
  padding: 20px !important;
}

/* dataframe */
[data-testid="stDataFrame"] { border-radius: var(--radius) !important; overflow: hidden !important; }

/* tabs */
[data-testid="stTabs"] [role="tablist"] {
  background: var(--surface-1) !important;
  border: 1px solid var(--rule) !important;
  border-radius: var(--radius-pill) !important;
  padding: 4px !important;
  gap: 4px !important;
}
[data-testid="stTabs"] [role="tab"] {
  border-radius: var(--radius-pill) !important;
  font-family: var(--font-sans) !important;
  font-size: 12px !important;
  color: var(--ink-3) !important;
  padding: 6px 14px !important;
  border: none !important;
}
[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
  background: var(--surface-3) !important;
  color: var(--ink) !important;
}

/* expander */
[data-testid="stExpander"] {
  background: var(--surface-1) !important;
  border: 1px solid var(--rule) !important;
  border-radius: var(--radius) !important;
}
[data-testid="stExpander"] summary { color: var(--ink-2) !important; font-family: var(--font-sans) !important; }

/* divider */
hr { border-color: var(--rule) !important; }

/* spinner */
[data-testid="stSpinner"] { color: var(--brass) !important; }

/* alerts */
[data-testid="stAlert"] {
  background: rgba(244,213,141,0.06) !important;
  border: 1px solid rgba(244,213,141,0.25) !important;
  border-radius: var(--radius-sm) !important;
  color: var(--lantern) !important;
}
[data-testid="stAlert"][data-type="error"] {
  background: rgba(216,124,106,0.06) !important;
  border-color: rgba(216,124,106,0.25) !important;
  color: var(--rust) !important;
}
[data-testid="stAlert"][data-type="success"] {
  background: rgba(123,198,138,0.06) !important;
  border-color: rgba(123,198,138,0.25) !important;
  color: var(--moss) !important;
}

/* plotly chart backgrounds */
[data-testid="stPlotlyChart"] { border-radius: var(--radius) !important; overflow: hidden !important; }

/* download button */
[data-testid="stDownloadButton"] button {
  background: var(--surface-1) !important;
  border: 1px solid var(--rule) !important;
  color: var(--ink-2) !important;
  border-radius: var(--radius-pill) !important;
  font-size: 11px !important;
}

/* selectbox dropdown */
[data-baseweb="popover"] [data-baseweb="menu"] {
  background: var(--bg-2) !important;
  border: 1px solid var(--rule-2) !important;
  border-radius: var(--radius-sm) !important;
}
[data-baseweb="popover"] [role="option"] {
  background: transparent !important;
  color: var(--ink-2) !important;
  font-family: var(--font-sans) !important;
}
[data-baseweb="popover"] [role="option"]:hover { background: var(--surface-2) !important; color: var(--ink) !important; }

/* labels */
label { color: var(--ink-3) !important; font-family: var(--font-sans) !important; font-size: 11.5px !important; }

/* toggle */
[data-testid="stCheckbox"] label, [data-baseweb="checkbox"] span { color: var(--ink-2) !important; }

/* ── Nautical UI classes ─────────────────────────────────────────────────────── */
.k-card {
  background: var(--surface-2);
  border: 1px solid var(--rule);
  border-radius: var(--radius);
  box-shadow: var(--shadow-1);
  position: relative; overflow: hidden;
  -webkit-backdrop-filter: blur(8px) saturate(140%);
  backdrop-filter: blur(8px) saturate(140%);
  margin-bottom: 16px;
  animation: k-fade-up 220ms var(--ease) both;
}
.k-card.gilt::before {
  content: ''; position: absolute; top: 0; left: 16px; right: 16px; height: 1px;
  background: linear-gradient(90deg, transparent, var(--brass), transparent);
  opacity: 0.5;
}
.k-card-h {
  padding: 16px 20px 12px;
  display: flex; align-items: flex-start; justify-content: space-between; gap: 16px;
  border-bottom: 1px solid var(--rule);
}
.k-card-t {
  font-family: var(--font-sans); font-size: 16px; color: var(--ink);
  font-weight: 600; margin: 0;
}
.k-card-b { padding: 16px 20px 18px; }

.k-kicker {
  font-family: var(--font-sans);
  font-size: 9.5px; letter-spacing: 0.16em; text-transform: uppercase;
  color: var(--brass); margin-bottom: 6px; font-weight: 600; display: block;
}

.k-metric { display: flex; flex-direction: column; gap: 4px; }
.k-metric-l {
  font-family: var(--font-sans); font-size: 10.5px; letter-spacing: 0.12em;
  text-transform: uppercase; color: var(--ink-3); font-weight: 600;
}
.k-metric-v {
  font-family: var(--font-mono); font-size: 28px; line-height: 1.05;
  color: var(--ink);
  font-variant-numeric: tabular-nums;
}
.k-metric-v.pos { color: var(--moss); }
.k-metric-v.neg { color: var(--rust); }
.k-metric-v.brass { color: var(--brass); }
.k-metric-d { font-family: var(--font-mono); font-size: 11.5px; color: var(--ink-3); }
.k-metric-d.pos { color: var(--pos); }
.k-metric-d.neg { color: var(--neg); }

.k-feed { display: flex; flex-direction: column; }
.k-feed-day {
  display: grid; grid-template-columns: 88px 1fr; gap: 16px;
  padding: 14px 0; border-top: 1px solid var(--rule);
}
.k-feed-day:first-child { border-top: none; padding-top: 8px; }
.k-feed-day-h {
  font-family: var(--font-sans); font-size: 11px; letter-spacing: 0.14em;
  text-transform: uppercase; color: var(--ink-3); padding-top: 6px; font-weight: 600;
}
.k-feed-day-h .sub {
  display: block; font-family: var(--font-mono); font-size: 10px;
  color: var(--ink-4); margin-top: 4px; letter-spacing: 0.04em; text-transform: none;
}
.k-feed-list { display: flex; flex-direction: column; gap: 6px; }
.k-feed-row {
  display: grid; grid-template-columns: 36px 1fr auto; gap: 12px;
  padding: 12px 14px;
  background: var(--surface-1); border: 1px solid transparent;
  border-radius: var(--radius-sm); align-items: center;
  transition: all 140ms var(--ease);
}
.k-feed-row:hover {
  background: var(--surface-2); border-color: var(--rule-2);
  transform: translateX(2px);
}
.k-feed-icon {
  width: 36px; height: 36px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-family: var(--font-mono); font-size: 14px; font-weight: 600;
  background: var(--surface-2); border: 1px solid var(--rule);
}
.k-feed-icon.in    { color: var(--moss);  border-color: rgba(123,198,138,0.4); background: rgba(123,198,138,0.08); }
.k-feed-icon.out   { color: var(--ink-2); }
.k-feed-icon.invest{ color: var(--brass); border-color: var(--rule-brass); background: var(--brass-soft); }
.k-feed-body { display: flex; flex-direction: column; gap: 3px; min-width: 0; }
.k-feed-title {
  font-family: var(--font-sans); font-size: 13px; color: var(--ink);
  font-weight: 500; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.k-feed-meta {
  font-family: var(--font-sans); font-size: 11px; color: var(--ink-3);
  display: flex; align-items: center; gap: 8px; flex-wrap: wrap;
}
.k-feed-note {
  font-family: var(--font-serif); font-size: 12px; font-style: italic;
  color: var(--ink-3); line-height: 1.4;
}
.k-feed-val {
  font-family: var(--font-mono); font-size: 14px; text-align: right;
  color: var(--ink); white-space: nowrap; font-weight: 500;
  font-variant-numeric: tabular-nums;
}
.k-feed-val.pos    { color: var(--moss); }
.k-feed-val.invest { color: var(--brass); }

.k-mood {
  display: inline-flex; align-items: center; padding: 2px 7px;
  font-family: var(--font-sans); font-size: 9.5px; font-weight: 500;
  letter-spacing: 0.06em; border-radius: var(--radius-pill);
  background: var(--surface-2); color: var(--ink-3); border: 1px solid var(--rule);
}
.k-mood.planejado  { color: var(--moss);   border-color: rgba(123,198,138,0.3); }
.k-mood.necessario { color: var(--sea);    border-color: rgba(127,179,200,0.3); }
.k-mood.prazer     { color: var(--brass);  border-color: var(--rule-brass); }
.k-mood.impulso    { color: var(--copper); border-color: rgba(224,136,85,0.4); background: rgba(224,136,85,0.08); }
.k-mood.renda      { color: var(--moss);   border-color: rgba(123,198,138,0.4); background: rgba(123,198,138,0.08); }
.k-mood.obrigatorio{ color: var(--ink-3); }
.k-mood.social     { color: var(--sea);    border-color: rgba(127,179,200,0.3); }
.k-mood.saude      { color: var(--lantern);border-color: rgba(244,213,141,0.3); }
.k-mood.recorrente { color: var(--ink-3); }
.k-mood.investimento{ color: var(--brass); border-color: var(--rule-brass); background: var(--brass-soft); }

.k-chip {
  display: inline-flex; align-items: center; gap: 5px;
  padding: 3px 8px; border-radius: var(--radius-pill);
  background: var(--surface-1); border: 1px solid var(--rule);
  font-family: var(--font-sans); font-size: 10.5px; color: var(--ink-2); font-weight: 500;
}
.k-chip.pos  { color: var(--moss);    border-color: rgba(123,198,138,0.3); background: rgba(123,198,138,0.06); }
.k-chip.neg  { color: var(--rust);    border-color: rgba(216,124,106,0.3); background: rgba(216,124,106,0.06); }
.k-chip.warn { color: var(--lantern); border-color: rgba(244,213,141,0.3); background: rgba(244,213,141,0.06); }
.k-chip.brass{ color: var(--brass);   border-color: var(--rule-brass); background: var(--brass-soft); }

.k-grid { display: grid; gap: 16px; }
.k-cols-2 { grid-template-columns: repeat(2,1fr); }
.k-cols-3 { grid-template-columns: repeat(3,1fr); }
.k-cols-4 { grid-template-columns: repeat(4,1fr); }

.k-stat-card {
  background: var(--surface-2);
  border: 1px solid var(--rule);
  border-radius: var(--radius);
  box-shadow: var(--shadow-1);
  padding: 16px 18px;
  display: flex; flex-direction: column; gap: 4px;
  transition: border-color 160ms var(--ease), background 160ms var(--ease), transform 160ms var(--ease);
}
.k-stat-card:hover {
  background: var(--surface-3);
  border-color: var(--rule-2);
  transform: translateY(-1px);
}

.k-operating-hero {
  position: relative;
  overflow: hidden;
  border: 1px solid var(--rule);
  border-radius: var(--radius-lg);
  background:
    radial-gradient(circle at 8% 0%, rgba(77,141,255,0.10), transparent 36%),
    radial-gradient(circle at 92% 18%, rgba(217,178,111,0.09), transparent 34%),
    linear-gradient(135deg, rgba(255,255,255,0.035), rgba(255,255,255,0.012));
  padding: 28px 32px;
  margin: 8px 0 24px;
  box-shadow: 0 1px 0 rgba(255,255,255,0.04) inset, 0 18px 48px rgba(0,0,0,0.22);
  animation: k-fade-up 220ms var(--ease) both;
}
.k-operating-hero::before {
  content: '';
  position: absolute;
  left: 32px; right: 32px; top: 0; height: 1px;
  background: linear-gradient(90deg, transparent, rgba(77,141,255,0.42), rgba(217,178,111,0.34), transparent);
}
.k-operating-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 32px;
  align-items: end;
  position: relative;
  z-index: 1;
}
.k-operating-title {
  margin: 10px 0 10px;
  font-family: var(--font-sans);
  font-size: clamp(30px, 4vw, 52px);
  line-height: 0.98;
  letter-spacing: -0.045em;
  font-weight: 600;
  color: var(--ink);
}
.k-operating-copy {
  max-width: 680px;
  margin: 0;
  font-family: var(--font-sans);
  font-size: 14px;
  line-height: 1.65;
  color: var(--ink-2);
}
.k-operating-signals {
  display: grid;
  grid-template-columns: repeat(3, minmax(116px, 1fr));
  gap: 10px;
  min-width: 420px;
}
.k-signal {
  border: 1px solid var(--rule);
  border-radius: var(--radius-sm);
  background: rgba(255,255,255,0.025);
  padding: 12px 13px;
}
.k-signal-label {
  font-family: var(--font-sans);
  font-size: 9px;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--ink-4);
  font-weight: 600;
}
.k-signal-value {
  margin-top: 7px;
  font-family: var(--font-mono);
  font-size: 18px;
  line-height: 1;
  color: var(--ink);
  font-variant-numeric: tabular-nums;
}
.k-decision-brief {
  display: grid;
  gap: 10px;
}
.k-brief-item {
  display: grid;
  grid-template-columns: 7px 1fr;
  gap: 10px;
  align-items: start;
  padding: 10px 0;
  border-top: 1px solid var(--rule);
}
.k-brief-item:first-child { border-top: none; padding-top: 0; }
.k-brief-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  margin-top: 6px;
  background: var(--brass);
  box-shadow: 0 0 10px var(--brass-glow);
}
.k-brief-title {
  font-family: var(--font-sans);
  font-size: 13px;
  color: var(--ink);
  font-weight: 500;
}
.k-brief-copy {
  margin-top: 3px;
  font-family: var(--font-sans);
  font-size: 12px;
  line-height: 1.45;
  color: var(--ink-3);
}

.k-wallet {
  display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 18px; margin-bottom: 28px;
}
.k-cardobj {
  position: relative; aspect-ratio: 1.586/1;
  border-radius: 18px; padding: 18px 20px;
  display: flex; flex-direction: column; justify-content: space-between;
  overflow: hidden;
  box-shadow: 0 12px 32px rgba(0,0,0,0.45), 0 1px 0 rgba(255,255,255,0.08) inset;
  transition: transform 200ms var(--ease), box-shadow 200ms var(--ease);
  cursor: pointer;
}
.k-cardobj::before {
  content: ''; position: absolute; inset: 0;
  background: radial-gradient(circle at 80% 0%, rgba(255,255,255,0.18), transparent 60%);
  pointer-events: none;
}
.k-cardobj.selected {
  transform: translateY(-3px);
  box-shadow: 0 22px 56px rgba(0,0,0,0.55), 0 0 0 1px var(--brass), var(--glow-brass);
}
.k-cardobj:hover { transform: translateY(-3px); box-shadow: 0 22px 56px rgba(0,0,0,0.55); }
.k-card-chip {
  width: 32px; height: 24px; border-radius: 4px;
  background: linear-gradient(135deg, #C9A05E, #8C6A35);
  position: absolute; top: 56px; left: 22px;
  box-shadow: 0 1px 0 rgba(255,255,255,0.2) inset;
}
.k-card-num {
  font-family: var(--font-mono); font-size: 15px;
  letter-spacing: 0.18em; opacity: 0.95; margin-top: auto;
}

.k-parcela {
  padding: 16px 18px;
  background: var(--surface-1); border: 1px solid var(--rule);
  border-radius: var(--radius-sm); margin-bottom: 10px;
  transition: all 160ms var(--ease);
}
.k-parcela:hover { background: var(--surface-2); border-color: var(--rule-2); }
.k-parcela-fill {
  height: 8px;
  background: linear-gradient(90deg, #987D4E, var(--brass));
  border-radius: var(--radius-pill);
  box-shadow: 0 0 8px var(--brass-glow);
}

.k-engine-row {
  display: grid; grid-template-columns: 24px 1fr auto; align-items: center; gap: 8px;
  font-family: var(--font-sans); font-size: 11.5px; color: var(--ink-2); padding: 4px 0;
}
.k-engine-row .eid {
  font-family: var(--font-mono); font-size: 9px; letter-spacing: 0.06em;
  padding: 2px 4px; border-radius: 3px;
  background: rgba(0,0,0,0.25); border: 1px solid var(--rule);
  text-align: center;
}
.k-engine-row .pulse {
  width: 6px; height: 6px; border-radius: 50%; position: relative;
}
.k-engine-row.ok   .pulse { background: var(--moss); }
.k-engine-row.ok   .eid   { color: var(--moss); border-color: rgba(123,198,138,0.3); }
.k-engine-row.neg  .pulse { background: var(--rust); }
.k-engine-row.neg  .eid   { color: var(--rust); }
.k-engine-row.warn .pulse { background: var(--lantern); }

@keyframes k-pulse {
  0%   { transform: scale(0.6); opacity: 0.6; }
  100% { transform: scale(2.2); opacity: 0; }
}
.k-engine-row .pulse::after {
  content: ''; position: absolute; inset: -3px; border-radius: 50%;
  border: 1px solid currentColor; opacity: 0.3;
  animation: k-pulse 2s ease-out infinite;
}
.k-engine-row.ok   .pulse::after { color: var(--moss); }
.k-engine-row.neg  .pulse::after { color: var(--rust); }

.k-bar-track {
  height: 6px; border-radius: var(--radius-pill);
  background: var(--surface-2); border: 1px solid var(--rule);
  overflow: hidden; margin-top: 8px;
}
.k-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #AE8E59, var(--brass));
  border-radius: var(--radius-pill);
  box-shadow: 0 0 8px var(--brass-glow);
}
.k-bar-fill.pos  { background: var(--moss); box-shadow: none; }
.k-bar-fill.warn { background: var(--lantern); box-shadow: none; }
.k-bar-fill.neg  { background: var(--rust); box-shadow: none; }

.k-gov-row {
  display: flex; align-items: center; justify-content: space-between;
  padding: 10px 0; border-top: 1px solid var(--rule);
}
.k-gov-row:first-child { border-top: none; padding-top: 0; }

.k-sec-h {
  display: flex; align-items: baseline; justify-content: space-between;
  margin: 24px 0 14px;
}
.k-sec-h .t {
  font-family: var(--font-sans); font-size: 19px; font-weight: 600;
  color: var(--ink);
}
.k-sec-h .s {
  font-family: var(--font-sans); font-size: 11px; letter-spacing: 0.10em;
  text-transform: uppercase; color: var(--ink-3); font-weight: 500;
}

.muted  { color: var(--ink-3) !important; }
.dim    { color: var(--ink-4) !important; }
.serif  { font-family: var(--font-serif) !important; }
.mono   { font-family: var(--font-mono) !important; font-variant-numeric: tabular-nums; }
.pos    { color: var(--pos) !important; }
.neg    { color: var(--neg) !important; }
.warn   { color: var(--warn) !important; }
.brass-c{ color: var(--brass) !important; }

/* fragility gauge */
.k-frag-gauge { text-align: center; }

/* page headings — General Sans 600 */
[data-testid="stMainBlockContainer"] h1,
[data-testid="stMainBlockContainer"] h2 {
  font-family: var(--font-sans) !important;
  font-weight: 600 !important;
  color: var(--ink) !important;
  letter-spacing: -0.01em !important;
}

/* Streamlit column gap */
[data-testid="stHorizontalBlock"] { gap: 16px !important; }

/* hide streamlit branding */
#MainMenu, footer { visibility: hidden !important; }
[data-testid="stToolbar"] { display: none !important; }

/* sidebar expand button — always visible */
button[data-testid="collapsedControl"],
section[data-testid="stSidebarCollapsedControl"] {
  display: flex !important;
  z-index: 999999 !important;
}

/* ── Inline page navigation (column-based) ───────────────────────────────── */
[data-testid="stSidebarNavItems"] {
  display: none !important;
}
[data-testid="stPageLink-NavLink"] {
  padding: 9px 14px !important;
  border-radius: var(--radius-xs) !important;
  font-family: var(--font-sans) !important;
  font-size: 13px !important;
  color: var(--ink-3) !important;
  margin: 2px 0 !important;
  transition: background 150ms, color 150ms !important;
  letter-spacing: 0.01em !important;
  border-left: 2px solid transparent !important;
  display: block !important;
  width: 100% !important;
}
[data-testid="stPageLink-NavLink"]:hover {
  background: var(--surface-2) !important;
  color: var(--ink) !important;
}
[data-testid="stPageLink-NavLink"][aria-current="page"] {
  background: var(--brass-soft) !important;
  color: var(--brass) !important;
  border-left: 2px solid var(--brass) !important;
  font-weight: 600 !important;
}
.k-sidenav-section {
  font-family: var(--font-sans); font-size: 9.5px; letter-spacing: 0.18em;
  text-transform: uppercase; color: var(--ink-4); padding: 8px 4px 4px;
  font-weight: 600;
}

/* ── Inline nav column container ─────────────────────────────────────────── */
.k-nav-col {
  background: linear-gradient(180deg, #0E202D 0%, #0C1E2B 100%);
  border-right: 1px solid var(--rule);
  min-height: 100vh;
  padding: 12px 8px 24px;
  position: sticky;
  top: 0;
  overflow-y: auto;
}

/* ── Auth login button — electric blue ───────────────────────────────────── */
[data-testid="stForm"] .stButton > button[kind="primary"],
.stButton > button[kind="primary"].k-auth-submit {
  background: #6366F1 !important;
  border-color: transparent !important;
  color: #fff !important;
  font-weight: 600 !important;
  box-shadow: 0 0 0 1px rgba(99,102,241,0.3), 0 0 24px rgba(99,102,241,0.18) !important;
}

/* ── Spending Plan hero ──────────────────────────────────────────────────── */
.k-spending-hero {
  background: var(--surface-1);
  border: 1px solid var(--rule-brass);
  border-radius: var(--radius);
  padding: 20px 24px 18px;
  position: relative; overflow: hidden;
  margin-bottom: 20px;
}
.k-spending-hero::before {
  content: '';
  position: absolute; inset: -1px;
  background: radial-gradient(circle at top left, var(--brass-soft), transparent 60%);
  pointer-events: none;
}
.k-spending-amount {
  font-family: var(--font-mono);
  font-size: 40px; line-height: 1;
  font-variant-numeric: tabular-nums; font-weight: 600;
}
.k-spending-rate {
  font-family: var(--font-sans); font-size: 12px;
  color: var(--brass); margin-top: 4px;
  letter-spacing: 0.06em; text-transform: uppercase; font-weight: 600;
}
.k-spend-track {
  height: 6px; background: var(--surface-2);
  border-radius: var(--radius-pill); overflow: hidden;
  position: relative; margin-top: 14px;
}

/* ── Category badge (Simplifi-style colored circle) ─────────────────────── */
.k-cat-badge {
  width: 36px; height: 36px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-family: var(--font-sans); font-size: 13px; font-weight: 700;
  flex-shrink: 0;
}

/* ── Kira AI widget ─────────────────────────────────────────────────────── */
.k-kira-header {
  display: flex; align-items: center; gap: 8px;
  padding: 10px 14px 8px;
  border-bottom: 1px solid var(--rule);
}
.k-kira-dot {
  width: 7px; height: 7px; border-radius: 50%;
  background: var(--brass); box-shadow: 0 0 6px var(--brass-glow);
  animation: k-pulse 2s infinite;
}
@keyframes k-pulse {
  0%, 100% { opacity: 1; } 50% { opacity: 0.4; }
}
.k-kira-label {
  font-family: var(--font-sans); font-size: 11px;
  color: var(--brass); font-weight: 600; letter-spacing: 0.12em;
  text-transform: uppercase;
}
.k-kira-bubble {
  background: var(--surface-2); border: 1px solid var(--rule);
  border-radius: var(--radius-sm); padding: 10px 12px;
  font-family: var(--font-sans); font-size: 12.5px;
  color: var(--ink-2); line-height: 1.55; white-space: pre-wrap;
}
.k-kira-bubble.user {
  background: var(--brass-soft); border-color: var(--rule-brass);
  color: var(--ink); text-align: right;
}

/* ── Accounts rail ───────────────────────────────────────────────────────── */
.k-acc-row {
  display: flex; align-items: center; gap: 10px;
  padding: 9px 0; border-bottom: 1px solid var(--rule);
}
.k-acc-row:last-child { border-bottom: none; }
.k-acc-dot {
  width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0;
}
.k-acc-name {
  font-family: var(--font-sans); font-size: 12.5px; color: var(--ink); font-weight: 500;
  flex: 1; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.k-acc-sub {
  font-family: var(--font-sans); font-size: 10px; color: var(--ink-4);
  margin-top: 1px;
}
.k-acc-val {
  font-family: var(--font-mono); font-size: 13px;
  color: var(--ink); font-variant-numeric: tabular-nums;
  white-space: nowrap; font-weight: 500;
}

/* ── Sprint 02: Card hierarchy ──────────────────────────────────────────── */

/* TYPE A — ACTION CARD  (CTAs, quick-add, pix rápido) */
.k-card-action {
  background: linear-gradient(135deg, var(--electric) 0%, #2563EB 100%);
  border: none; border-radius: var(--radius-card);
  padding: var(--space-xl); cursor: pointer;
  box-shadow: 0 4px 24px rgba(59,130,246,0.30);
  transition: transform 120ms, box-shadow 120ms;
  position: relative; overflow: hidden;
}
.k-card-action::before {
  content: ''; position: absolute; inset: 0;
  background: radial-gradient(circle at 80% 20%, rgba(255,255,255,0.12), transparent 60%);
  pointer-events: none;
}
.k-card-action:hover { transform: translateY(-2px); box-shadow: 0 8px 32px rgba(59,130,246,0.38); }
.k-card-action .label {
  font-family: var(--font-sans); font-size: 11px; font-weight: 600;
  letter-spacing: 0.10em; text-transform: uppercase; color: rgba(255,255,255,0.75);
  margin-bottom: 6px;
}
.k-card-action .value {
  font-family: var(--font-mono); font-size: 28px; font-weight: 700;
  color: #fff; letter-spacing: -0.02em; font-variant-numeric: tabular-nums;
}
.k-card-action .sub {
  font-family: var(--font-sans); font-size: 11px; color: rgba(255,255,255,0.65);
  margin-top: 4px;
}

/* TYPE B — KPI CARD  (métricas hero: saldo, entradas, saídas) */
.k-card-kpi {
  background: var(--card);
  border: 1px solid var(--rule-2);
  border-radius: var(--radius-card);
  padding: var(--space-xl);
  transition: border-color 150ms;
}
.k-card-kpi:hover { border-color: rgba(255,255,255,0.18); }
.k-card-kpi .label {
  font-family: var(--font-sans); font-size: 11px; font-weight: 500;
  letter-spacing: 0.10em; text-transform: uppercase; color: var(--ink-4);
  margin-bottom: 8px;
}
.k-card-kpi .value {
  font-family: var(--font-mono); font-size: 26px; font-weight: 600;
  color: var(--ink); letter-spacing: -0.02em; font-variant-numeric: tabular-nums;
  line-height: 1.1;
}
.k-card-kpi .delta {
  font-family: var(--font-sans); font-size: 11px; margin-top: 6px;
  display: flex; align-items: center; gap: 4px;
}
.k-card-kpi .delta.pos { color: var(--pos); }
.k-card-kpi .delta.neg { color: var(--neg); }
.k-card-kpi .delta.warn { color: var(--warn); }

/* TYPE C — ANALYTICS CARD  (charts, donut, barras) */
.k-card-analytics {
  background: var(--surface);
  border: 1px solid var(--rule);
  border-radius: var(--radius-card);
  padding: var(--space-xl) var(--space-xl) var(--space-md);
  overflow: hidden;
}
.k-card-analytics .k-card-h {
  margin-bottom: var(--space-md);
}

/* TYPE D — CONTEXT CARD  (alertas, WikiAgent, Kira) */
.k-card-context {
  background: linear-gradient(135deg,
    rgba(217,178,111,0.06) 0%,
    rgba(217,178,111,0.02) 100%);
  border: 1px solid var(--rule-brass);
  border-radius: var(--radius-card);
  padding: var(--space-xl);
}
.k-card-context .k-card-t { color: var(--brass); }

/* ── Sprint 03: Bottom navigation (mobile) ──────────────────────────────── */
.k-bottom-nav {
  display: none;
  position: fixed; bottom: 0; left: 0; right: 0; z-index: 9990;
  grid-template-columns: repeat(5, 1fr);
  background: rgba(7,17,29,0.92);
  border-top: 1px solid var(--rule-2);
  backdrop-filter: blur(20px) saturate(140%);
  -webkit-backdrop-filter: blur(20px) saturate(140%);
  padding: 8px 4px max(12px, env(safe-area-inset-bottom));
  height: 72px;
}
.k-bottom-nav a, .k-bnav-item {
  display: flex; flex-direction: column; align-items: center;
  gap: 3px; padding: 0 4px;
  font-family: var(--font-sans); font-size: 10px; letter-spacing: 0.02em;
  color: var(--ink-4); text-decoration: none;
  transition: color 120ms; cursor: pointer;
  min-width: 44px; min-height: 44px; justify-content: center;
  border-radius: var(--radius-xs);
}
.k-bottom-nav a:hover, .k-bnav-item:hover,
.k-bottom-nav a.active, .k-bnav-item.active {
  color: var(--brass);
}
.k-bottom-nav .icon { font-size: 20px; line-height: 1; }

/* ── FAB — global quick-add ──────────────────────────────────────────────── */
.k-fab {
  display: none;
  position: fixed; bottom: 84px; right: 20px; z-index: 9991;
  width: 56px; height: 56px; border-radius: var(--radius-fab);
  background: linear-gradient(135deg, var(--electric) 0%, #2563EB 100%);
  border: none; cursor: pointer;
  box-shadow: 0 4px 20px rgba(59,130,246,0.45);
  align-items: center; justify-content: center;
  font-size: 24px; color: #fff;
  transition: transform 150ms, box-shadow 150ms;
}
.k-fab:hover { transform: scale(1.08); box-shadow: 0 8px 28px rgba(59,130,246,0.55); }
.k-fab:active { transform: scale(0.95); }


/* ── Segmented control (tab-style switch) ───────────────────────────────── */
.k-seg-ctrl {
  display: inline-flex; border-radius: var(--radius-input);
  background: var(--surface-1); border: 1px solid var(--rule);
  padding: 3px; gap: 2px;
}
.k-seg-ctrl .seg {
  padding: 6px 16px; border-radius: calc(var(--radius-input) - 3px);
  font-family: var(--font-sans); font-size: 13px; font-weight: 500;
  color: var(--ink-3); cursor: pointer; transition: all 120ms;
  min-width: 80px; text-align: center;
}
.k-seg-ctrl .seg.active {
  background: var(--card); color: var(--ink);
  box-shadow: 0 1px 4px rgba(0,0,0,0.25);
}
.k-seg-ctrl .seg:hover:not(.active) { color: var(--ink-2); }

/* ── Bottom sheet (modal drawer from bottom on mobile) ──────────────────── */
.k-bottom-sheet {
  position: fixed; bottom: 0; left: 0; right: 0; z-index: 9995;
  background: var(--card); border-top: 1px solid var(--rule-2);
  border-radius: var(--radius-hero) var(--radius-hero) 0 0;
  padding: 0 var(--space-xl) max(28px, env(safe-area-inset-bottom));
  box-shadow: 0 -8px 40px rgba(0,0,0,0.45);
  max-height: 92vh; overflow-y: auto;
}
.k-bottom-sheet .handle {
  width: 36px; height: 4px; border-radius: 2px;
  background: var(--rule-2); margin: 12px auto 20px;
}

/* ── Premium auth shell ──────────────────────────────────────────────────── */
.k-auth-shell {
  min-height: 100vh;
  display: grid;
  grid-template-columns: minmax(0, 1.1fr) minmax(420px, 0.9fr);
  background:
    radial-gradient(circle at 20% 18%, rgba(77,141,255,0.12), transparent 34%),
    radial-gradient(circle at 0% 100%, rgba(217,178,111,0.10), transparent 40%),
    linear-gradient(135deg, var(--bg-deep), var(--bg) 54%, #0A1827);
  overflow: hidden;
}
.k-auth-brand {
  min-height: 100vh;
  position: relative;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 72px 72px 48px;
  border-right: 1px solid var(--rule);
}
.k-auth-ambient {
  position: absolute;
  inset: -20%;
  background:
    radial-gradient(circle at 28% 34%, rgba(77,141,255,0.16), transparent 28%),
    radial-gradient(circle at 56% 70%, rgba(217,178,111,0.10), transparent 34%);
  filter: blur(32px);
  animation: k-gradient-drift 12s var(--ease) infinite;
  pointer-events: none;
}
.k-auth-brand-inner,
.k-auth-footer {
  position: relative;
  z-index: 1;
}
.k-auth-lockup {
  height: 56px;
  width: auto;
  display: block;
  margin-bottom: 88px;
}
.k-auth-mark {
  display: inline-flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 88px;
  font-family: var(--font-sans);
  font-size: 24px;
  font-weight: 600;
  color: var(--ink);
}
.k-auth-kicker {
  font-family: var(--font-sans);
  font-size: 10px;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: var(--brass);
  font-weight: 600;
}
.k-auth-brand h1 {
  max-width: 620px;
  margin: 16px 0 18px;
  font-family: var(--font-sans);
  font-size: clamp(42px, 5vw, 72px);
  line-height: 0.95;
  letter-spacing: -0.045em;
  color: var(--ink);
  font-weight: 600;
}
.k-auth-brand p {
  max-width: 540px;
  margin: 0;
  font-family: var(--font-sans);
  font-size: 15px;
  line-height: 1.7;
  color: var(--ink-2);
}
.k-auth-proof {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 32px;
}
.k-auth-proof span {
  padding: 6px 10px;
  border-radius: var(--radius-xs);
  border: 1px solid var(--rule);
  background: rgba(255,255,255,0.03);
  font-family: var(--font-mono);
  font-size: 10px;
  color: var(--ink-3);
  letter-spacing: 0.04em;
}
.k-auth-footer {
  display: flex;
  justify-content: space-between;
  gap: 24px;
  font-family: var(--font-mono);
  font-size: 10px;
  color: var(--ink-4);
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
.k-auth-panel {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 72px;
}
.k-auth-form-head {
  width: min(100%, 390px);
  margin-bottom: 24px;
}
.k-auth-form-head h2,
.k-auth-mfa h2 {
  margin: 10px 0 8px;
  font-family: var(--font-sans);
  font-size: 30px;
  line-height: 1.05;
  letter-spacing: -0.03em;
  color: var(--ink);
  font-weight: 600;
}
.k-auth-form-head p,
.k-auth-mfa p {
  margin: 0;
  font-family: var(--font-sans);
  font-size: 13px;
  line-height: 1.6;
  color: var(--ink-3);
}
.k-auth-after {
  width: min(100%, 390px);
  margin: 16px 72px 0 auto;
  display: flex;
  justify-content: space-between;
  gap: 16px;
  font-family: var(--font-mono);
  font-size: 10px;
  color: var(--ink-4);
  text-transform: uppercase;
  letter-spacing: 0.08em;
}
.k-auth-mfa {
  text-align: left;
  margin-bottom: 24px;
}
@media (max-width: 980px) {
  .k-auth-shell { grid-template-columns: 1fr; }
  .k-auth-brand {
    min-height: auto;
    padding: 44px 28px 32px;
    border-right: none;
    border-bottom: 1px solid var(--rule);
  }
  .k-auth-lockup, .k-auth-mark { margin-bottom: 48px; }
  .k-auth-panel {
    min-height: auto;
    justify-content: flex-start;
    padding: 32px 28px 24px;
  }
  .k-auth-after {
    width: auto;
    margin: 16px 28px 40px;
    flex-direction: column;
  }
}

/* ── Sprint 09: Premium empty state ────────────────────────────────────── */
.k-empty-state {
  display: flex; flex-direction: column; align-items: center;
  justify-content: center; text-align: center;
  padding: var(--space-xxl) var(--space-xl);
  border: 1px dashed var(--rule-2);
  border-radius: var(--radius-card);
  background: var(--surface-1);
  min-height: 200px;
}
.k-empty-state .icon {
  font-size: 40px; line-height: 1; margin-bottom: var(--space-lg);
  opacity: 0.5;
}
.k-empty-state .title {
  font-family: var(--font-sans); font-size: 16px; font-weight: 600;
  color: var(--ink-2); margin-bottom: var(--space-sm);
}
.k-empty-state .sub {
  font-family: var(--font-sans); font-size: 13px; color: var(--ink-4);
  max-width: 320px; line-height: 1.55;
}

/* ── Sprint 07: Radar strip ─────────────────────────────────────────────── */
.k-radar-strip {
  background: linear-gradient(135deg,
    rgba(248,113,113,0.08) 0%,
    rgba(248,113,113,0.04) 100%);
  border: 1px solid rgba(248,113,113,0.25);
  border-left: 3px solid var(--rust);
  border-radius: var(--radius-card);
  padding: var(--space-lg) var(--space-xl);
  margin-bottom: var(--space-xl);
}
.k-radar-strip.warn {
  background: linear-gradient(135deg,
    rgba(245,158,11,0.08) 0%,
    rgba(245,158,11,0.04) 100%);
  border-color: rgba(245,158,11,0.25);
  border-left-color: var(--warn);
}
.k-radar-strip.ok {
  background: linear-gradient(135deg,
    rgba(16,185,129,0.06) 0%,
    rgba(16,185,129,0.02) 100%);
  border-color: rgba(16,185,129,0.20);
  border-left-color: var(--pos);
  padding: var(--space-md) var(--space-xl);
}
.k-radar-strip .k-radar-title {
  font-family: var(--font-sans); font-size: 11px; font-weight: 600;
  letter-spacing: 0.10em; text-transform: uppercase;
  color: var(--rust); margin-bottom: var(--space-sm);
}
.k-radar-strip.warn .k-radar-title { color: var(--warn); }
.k-radar-strip.ok .k-radar-title { color: var(--pos); }
.k-radar-alert-row {
  display: flex; align-items: baseline; gap: var(--space-md);
  padding: 6px 0; border-top: 1px solid var(--rule);
  font-family: var(--font-sans); font-size: 13px;
}
.k-radar-alert-row:first-child { border-top: none; }
.k-radar-alert-row .cat { color: var(--ink); font-weight: 500; flex: 1; }
.k-radar-alert-row .ratio { font-family: var(--font-mono); color: var(--rust); font-size: 12px; }
.k-radar-alert-row .amounts { font-size: 11px; color: var(--ink-3); }

/* ── Mobile (≤640px) ─────────────────────────────────────────────────────── */
@media (max-width: 640px) {

  /* Reduz padding lateral do viewport Streamlit */
  section[data-testid="stAppViewBlockContainer"],
  div[data-testid="stAppViewBlockContainer"] {
    padding-left: 12px !important;
    padding-right: 12px !important;
  }

  /* k-grid — stacked */
  .k-cols-4 { grid-template-columns: repeat(2, 1fr); }
  .k-cols-3 { grid-template-columns: repeat(2, 1fr); }
  .k-cols-2 { grid-template-columns: 1fr; }

  /* Streamlit columns nativas — empilhar verticalmente */
  div[data-testid="stHorizontalBlock"] {
    flex-wrap: wrap !important;
  }
  div[data-testid="column"] {
    min-width: 0 !important;
    width: 100% !important;
    flex: 1 1 100% !important;
  }

  /* k-grid — 4 e 3 colunas viram 1 no mobile estreito */
  .k-cols-4 { grid-template-columns: repeat(2, 1fr); }
  .k-cols-3 { grid-template-columns: 1fr !important; }

  /* Hero — fonte e padding reduzidos */
  .k-hero {
    padding: 20px 16px !important;
    border-radius: 12px !important;
  }
  .k-hero-balance {
    font-size: clamp(20px, 6vw, 28px) !important;
  }
  .k-hero-stats-row {
    flex-wrap: wrap !important;
    gap: 10px !important;
  }
  .k-hero-stat { font-size: 12px !important; }
  .k-hero-divider { display: none !important; }
  .k-hero-stat-val { font-size: 13px !important; }

  /* Section header menor */
  .k-section-header h2 {
    font-size: 16px !important;
  }

  /* Charts — nunca transbordam */
  div[data-testid="stPlotlyChart"],
  div[data-testid="stPlotlyChart"] > div {
    max-width: 100% !important;
    overflow-x: hidden !important;
  }

  /* Dataframe — scroll horizontal */
  div[data-testid="stDataFrame"] {
    overflow-x: auto !important;
    max-width: 100vw !important;
  }

  /* Sidebar toggle sempre visível */
  button[data-testid="collapsedControl"],
  section[data-testid="stSidebarCollapsedControl"] {
    display: flex !important;
  }

  /* Expanders — largura total */
  div[data-testid="stExpander"] {
    width: 100% !important;
  }

  /* Tabs — scroll horizontal para não quebrar */
  div[data-testid="stTabs"] > div:first-child {
    overflow-x: auto !important;
    white-space: nowrap !important;
    scrollbar-width: none !important;
  }

  /* Operating hero — colapsa para coluna única em mobile */
  .k-operating-grid {
    grid-template-columns: 1fr !important;
  }
  .k-operating-signals {
    grid-template-columns: repeat(3, 1fr) !important;
    min-width: unset !important;
  }
  .k-operating-hero {
    padding: 18px 16px !important;
  }
  .k-operating-title {
    font-size: clamp(22px, 5vw, 36px) !important;
  }

  /* Sprint 03: bottom nav + FAB visible */
  .k-bottom-nav { display: grid; }
  .k-fab { display: flex; }
  [data-testid="stApp"] > div:first-child {
    padding-bottom: 80px !important;
  }
  [data-testid="stMainBlockContainer"] {
    padding-bottom: 88px !important;
  }

  /* Sprint 03: touch targets 44px minimum */
  button, [role="button"], a { min-height: 44px !important; }

  /* Sprint 03: tighter headings */
  h1 { font-size: 22px !important; }
  h2 { font-size: 18px !important; }
}

/* ── Mobile: KPI grid 4-col → 2×2 ─────────────────────────────────────────── */
@media (max-width: 640px) {

  /* KPI strip: 4 colunas viram 2×2 */
  div[data-testid="stHorizontalBlock"] {
    flex-wrap: wrap !important;
    gap: 8px !important;
  }
  div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] {
    flex: 1 1 calc(50% - 4px) !important;
    min-width: calc(50% - 4px) !important;
    max-width: calc(50% - 4px) !important;
  }

  /* Hero: fonte menor no mobile */
  .k-hero-balance {
    font-size: 28px !important;
  }

  /* Charts: full width, altura reduzida */
  .js-plotly-plot {
    height: 220px !important;
  }

  /* Tabelas de posições: scroll horizontal */
  .inv-table-row,
  .inv-table-header {
    grid-template-columns: 70px 1fr 70px 60px !important;
    font-size: 11px !important;
  }
  /* Ocultar colunas menos críticas no mobile */
  .inv-table-row > span:nth-child(4),
  .inv-table-row > span:nth-child(6),
  .inv-table-header > span:nth-child(4),
  .inv-table-header > span:nth-child(6) {
    display: none !important;
  }

  /* Quick actions: wrap */
  .k-quick-actions {
    flex-wrap: wrap !important;
  }
  .k-quick-actions a > div {
    font-size: 12px !important;
    padding: 8px 12px !important;
  }

  /* Modais: full width no mobile */
  div[data-testid="stDialog"] > div {
    width: 95vw !important;
    max-width: 95vw !important;
    margin: 8px !important;
  }

  /* Tabs: fonte menor */
  button[data-testid="stTab"] {
    font-size: 12px !important;
    padding: 6px 10px !important;
  }
}

/* ── Mobile: 3 colunas → 1 coluna (M3 controls) ──────────────────────────── */
@media (max-width: 480px) {
  div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] {
    flex: 1 1 100% !important;
    min-width: 100% !important;
    max-width: 100% !important;
  }
}

</style>
"""

# ──────────────────────────────────────────────────────────────────────────────
# Python helpers
# ──────────────────────────────────────────────────────────────────────────────

# Simplifi-style category color palette: (text_color, background_color)
CAT_COLORS: dict[str, tuple[str, str]] = {
    "Alimentação": ("#F59E0B", "rgba(245,158,11,0.14)"),
    "Transporte":  ("#3B82F6", "rgba(59,130,246,0.14)"),
    "Saúde":       ("#EF4444", "rgba(239,68,68,0.14)"),
    "Lazer":       ("#8B5CF6", "rgba(139,92,246,0.14)"),
    "Moradia":     ("#10B981", "rgba(16,185,129,0.14)"),
    "Educação":    ("#0EA5E9", "rgba(14,165,233,0.14)"),
    "Investimento":("#D9B26F", "rgba(217,178,111,0.18)"),
    "Renda":       ("#22C55E", "rgba(34,197,94,0.14)"),
    "Freelance":   ("#F97316", "rgba(249,115,22,0.14)"),
    "Outros":      ("#8F8770", "rgba(143,135,112,0.12)"),
}


@dataclass(frozen=True)
class SidebarNavItem:
    path: str
    icon: str
    label: str


@dataclass(frozen=True)
class SidebarNavSection:
    """Visual section separator with optional label rendered in the sidebar nav."""
    label: str


# Ordered by usage frequency and logical grouping — standard personal finance app IA:
#   Visão Geral → Finanças (daily) → Investimentos → Ferramentas → Info (last)
SIDEBAR_NAV_ITEMS: tuple[SidebarNavItem | SidebarNavSection, ...] = (
    SidebarNavItem("app.py", "⌂", "Klipper"),
    SidebarNavItem("pages/1_Dashboard.py", "◉", "Dashboard"),
    SidebarNavSection("Finanças"),
    SidebarNavItem("pages/2_Transacoes.py", "↕", "Transações"),
    SidebarNavItem("pages/6_Contas.py", "⊞", "Contas"),
    SidebarNavItem("pages/7_Orcamento.py", "◎", "Orçamento"),
    SidebarNavSection("Investimentos"),
    SidebarNavItem("pages/3_Investimentos.py", "▲", "Investimentos"),
    SidebarNavItem("pages/8_Posicoes.py", "◐", "Posições"),
    SidebarNavItem("pages/9_Portfolio.py", "⌗", "Portfólio"),
    SidebarNavItem("pages/4_Decisoes.py", "◌", "Decisões"),
    SidebarNavSection("Ferramentas"),
    SidebarNavItem("pages/5_AI_Consilium.py", "∞", "AI Consilium"),
    SidebarNavItem("pages/10_Saude.py", "✚", "Saúde"),
    SidebarNavItem("pages/11_Extratos.py", "⬆", "Importar"),
    SidebarNavSection(""),
    SidebarNavItem("pages/12_Sobre.py", "ℹ", "Sobre"),
)

BRAND_SVG = """<svg width="22" height="22" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="klp-blade" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#2961C7"/>
      <stop offset="100%" stop-color="#5AAFF0"/>
    </linearGradient>
  </defs>
  <rect x="4" y="4" width="4.5" height="24" fill="currentColor"/>
  <polygon points="8.5,16 15.5,9 13.38,6.88 8.5,11.76" fill="currentColor"/>
  <polygon points="8.5,16 21,28.5 18.88,30.62 8.5,20.24" fill="url(#klp-blade)"/>
</svg>"""


_BRAND_DIR = None


def _brand_path(filename: str):
    from pathlib import Path
    return Path(__file__).parent.parent / "design_handoff_klipper" / "brand" / filename


@functools.lru_cache(maxsize=None)
def _brand_b64(filename: str) -> str:
    """Base64 data-URI for a brand PNG, loaded once and cached for the process lifetime."""
    import base64
    try:
        data = _brand_path(filename).read_bytes()
        return "data:image/png;base64," + base64.b64encode(data).decode()
    except Exception:
        return ""


def brand_icon_img(size: int = 28) -> str:
    """<img> tag for klipper-icon-dark.png at the given pixel size. Falls back to BRAND_SVG."""
    uri = _brand_b64("klipper-icon-dark.png")
    if uri:
        return (
            f'<img src="{uri}" width="{size}" height="{size}" '
            f'style="display:block;border-radius:{size // 5}px" alt="Klipper">'
        )
    return BRAND_SVG


def load_page_icon():
    """Load klipper-icon-dark.png as PIL Image for st.set_page_config(page_icon=...)."""
    try:
        from PIL import Image
        return Image.open(_brand_path("klipper-icon-dark.png"))
    except Exception:
        return "⚓"


# ── Forced-theme overrides injected after KLIPPER_CSS ─────────────────────────
# Late :root declarations beat earlier ones — same specificity, last writer wins.

_FORCE_LIGHT_CSS = """<style>:root {
  --bg:#F4F7FA !important;--bg-deep:#EBF0F5 !important;--bg-2:#FFFFFF !important;
  --surface:#F9FAFB !important;--card:#FFFFFF !important;
  --layer-active:#EFF6FF !important;--layer-crit:#DBEAFE !important;
  --surface-1:rgba(0,0,0,0.02) !important;--surface-2:rgba(0,0,0,0.04) !important;
  --surface-3:rgba(0,0,0,0.07) !important;--surface-tint:rgba(29,78,216,0.03) !important;
  --ink:#111827 !important;--ink-2:#374151 !important;
  --ink-3:#6B7280 !important;--ink-4:#9CA3AF !important;
  --rule:#E5E7EB !important;--rule-2:#D1D5DB !important;
  --rule-brass:rgba(29,78,216,0.12) !important;
  --electric:#1D4ED8 !important;--accent:#1D4ED8 !important;
  --pos:#10B981 !important;--neg:#EF4444 !important;--neg-expense:#EF4444 !important;
  --warn:#F59E0B !important;--danger:#EF4444 !important;--success:#10B981 !important;
  --hero-bg:linear-gradient(145deg,#EFF6FF 0%,#F4F7FA 60%,#FFFFFF 100%) !important;
  --shadow-1:0 1px 3px rgba(0,0,0,0.06),0 1px 2px rgba(0,0,0,0.04) !important;
  --shadow-2:0 4px 12px rgba(0,0,0,0.08),0 2px 4px rgba(0,0,0,0.04) !important;
  --glow-accent:0 0 0 1px rgba(29,78,216,0.14) !important;
  --glow-brass:0 0 0 1px rgba(29,78,216,0.10) !important;
  --brass:#B45309 !important;--moss:#059669 !important;--emerald:#059669 !important;
  --rust:#EF4444 !important;--lantern:#D97706 !important;
}</style>"""

_FORCE_DARK_CSS = """<style>:root {
  --bg:#020617 !important;--bg-deep:#020617 !important;--bg-2:#07111D !important;
  --surface:#07111D !important;--card:#0D1726 !important;
  --layer-active:#132238 !important;--layer-crit:#1B2B45 !important;
  --surface-1:rgba(255,255,255,0.03) !important;--surface-2:rgba(255,255,255,0.05) !important;
  --surface-3:rgba(255,255,255,0.08) !important;--surface-tint:rgba(59,130,246,0.04) !important;
  --ink:#F1F5F9 !important;--ink-2:#CBD5E1 !important;
  --ink-3:#94A3B8 !important;--ink-4:#475569 !important;
  --rule:rgba(255,255,255,0.07) !important;--rule-2:rgba(255,255,255,0.12) !important;
  --rule-brass:rgba(217,178,111,0.18) !important;
  --electric:#3B82F6 !important;--accent:#3B82F6 !important;
  --pos:#10B981 !important;--neg:#F87171 !important;--neg-expense:#F87171 !important;
  --warn:#F59E0B !important;--danger:#EF4444 !important;--success:#10B981 !important;
  --hero-bg:linear-gradient(145deg,#020617 0%,#07111D 60%,#0D1726 100%) !important;
  --shadow-1:0 1px 0 rgba(255,255,255,0.03) inset,0 4px 16px rgba(0,0,0,0.45) !important;
  --shadow-2:0 1px 0 rgba(255,255,255,0.04) inset,0 10px 30px rgba(0,0,0,0.55) !important;
  --glow-accent:0 0 0 1px rgba(59,130,246,0.18),0 0 24px rgba(59,130,246,0.08) !important;
  --glow-brass:0 0 0 1px rgba(217,178,111,0.12),0 0 24px rgba(217,178,111,0.06) !important;
}</style>"""


def inject_css() -> None:
    st.markdown(KLIPPER_CSS, unsafe_allow_html=True)
    theme = st.session_state.get("klipper_theme", "dark")
    if theme == "light":
        st.markdown(_FORCE_LIGHT_CSS, unsafe_allow_html=True)
    else:
        st.markdown(_FORCE_DARK_CSS, unsafe_allow_html=True)


def theme_toggle_btn(key_suffix: str = "") -> None:
    """Renderiza botão de toggle claro/escuro — inclua em render_navigation()."""
    theme = st.session_state.get("klipper_theme", "dark")
    label = "☀  Claro" if theme == "dark" else "☽  Escuro"
    if st.button(label, key=f"klipper_theme_toggle{key_suffix}", use_container_width=True):
        st.session_state["klipper_theme"] = "light" if theme == "dark" else "dark"
        st.rerun()


def render_navigation(key_suffix: str = "") -> None:
    """Sidebar navigation: Klipper brand + grouped page links + theme toggle.

    Renders SidebarNavSection entries as visual group headers and
    SidebarNavItem entries as st.page_link buttons. Order follows standard
    personal-finance IA: overview → daily finances → investments → tools → info.
    """
    st.markdown(sidebar_brand(), unsafe_allow_html=True)
    for item in SIDEBAR_NAV_ITEMS:
        if isinstance(item, SidebarNavSection):
            label_html = (
                f'<div class="k-sidenav-section">{item.label}</div>'
                if item.label
                else '<div style="height:6px"></div>'
            )
            st.markdown(label_html, unsafe_allow_html=True)
        else:
            try:
                st.page_link(item.path, label=f"{item.icon}  {item.label}")
            except Exception:
                # Streamlit Cloud may not have registered a newly deployed page yet;
                # silently skip rather than crash the entire navigation rail.
                pass
    st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)
    theme_toggle_btn(key_suffix=key_suffix)


def sidebar_nav() -> None:
    """Legacy alias — delegates to render_navigation items with section support.

    Unlike render_navigation(), raises on invalid paths so callers notice bugs.
    """
    for item in SIDEBAR_NAV_ITEMS:
        if isinstance(item, SidebarNavSection):
            if item.label:
                st.markdown(
                    f'<div class="k-sidenav-section">{item.label}</div>',
                    unsafe_allow_html=True,
                )
        else:
            st.page_link(item.path, label=f"{item.icon}  {item.label}")


def tx_row_simplifi(
    category: str,
    title: str,
    meta: str,
    amount_str: str,
    val_cls: str = "",
) -> str:
    """Simplifi-style transaction row: colored category badge + title + amount."""
    color, bg = CAT_COLORS.get(category, ("#8F8770", "rgba(143,135,112,0.12)"))
    initial = category[0].upper() if category else "?"
    return (
        f'<div class="k-feed-row">'
        f'<div class="k-cat-badge" style="background:{bg};color:{color}">{initial}</div>'
        f'<div class="k-feed-body">'
        f'<div class="k-feed-title">{title}</div>'
        f'<div class="k-feed-meta">{meta}</div>'
        f'</div>'
        f'<div class="k-feed-val {val_cls}">{amount_str}</div>'
        f'</div>'
    )


def fmt_brl(v: float, compact: bool = False) -> str:
    if compact and abs(v) >= 1_000_000:
        return f"R$ {v/1_000_000:.1f}M"
    if compact and abs(v) >= 1_000:
        return f"R$ {v/1_000:.1f}k"
    formatted = f"R$ {abs(v):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"-{formatted}" if v < 0 else formatted


def fmt_pct(v: float, sign: bool = False) -> str:
    s = "+" if sign and v >= 0 else ""
    return f"{s}{v:.1f}%"


def fmt_change(pct: float) -> str:
    sign = "+" if pct >= 0 else ""
    return f"{sign}{pct:.2f}%"


def kicker(text: str) -> str:
    return f'<div class="k-kicker">{text}</div>'


def k_card(content: str, gilt: bool = False, extra_style: str = "") -> str:
    cls = "k-card" + (" gilt" if gilt else "")
    style = f' style="{extra_style}"' if extra_style else ""
    return f'<div class="{cls}"{style}><div class="k-card-b">{content}</div></div>'


def k_card_with_header(title: str, content: str, hint: str = "", gilt: bool = False) -> str:
    cls = "k-card" + (" gilt" if gilt else "")
    safe_title = html_escape(title)
    hint_html = (
        f'<div style="font-family:var(--font-sans);font-size:11.5px;color:var(--ink-3);margin-top:2px">'
        f'{html_escape(hint)}</div>'
    ) if hint else ""
    return f"""<div class="{cls}">
  <div class="k-card-h">
    <div>
      <div class="k-card-t">{safe_title}</div>
      {hint_html}
    </div>
  </div>
  <div class="k-card-b">{content}</div>
</div>"""


def stat_card(kicker_text: str, value: str, sub: str = "", tone: str = "") -> str:
    color = {
        "pos":   "var(--moss)",
        "neg":   "var(--rust)",
        "warn":  "var(--lantern)",
        "brass": "var(--brass)",
    }.get(tone, "var(--ink)")
    return f"""<div class="k-stat-card">
  <div class="k-kicker">{kicker_text}</div>
  <div class="mono" style="font-size:26px;line-height:1.1;color:{color};font-variant-numeric:tabular-nums">{value}</div>
  <div class="mono muted" style="font-size:11px;margin-top:2px">{sub}</div>
</div>"""


def kpi_card(label: str, value: str, delta: str = "", tone: str = "") -> str:
    """TYPE B KPI card — hero metric with optional delta chip."""
    delta_cls = {"pos": "pos", "neg": "neg", "warn": "warn"}.get(tone, "")
    delta_html = f'<div class="delta {delta_cls}">{delta}</div>' if delta else ""
    return f"""<div class="k-card-kpi">
  <div class="label">{label}</div>
  <div class="value">{value}</div>
  {delta_html}
</div>"""


def action_card(label: str, value: str, sub: str = "") -> str:
    """TYPE A action card — vibrant blue gradient CTA."""
    return f"""<div class="k-card-action">
  <div class="label">{label}</div>
  <div class="value">{value}</div>
  <div class="sub">{sub}</div>
</div>"""


def context_card(title: str, body: str, hint: str = "") -> str:
    """TYPE D context card — brass tint for alerts/WikiAgent."""
    hint_html = f'<div style="font-size:10.5px;color:var(--ink-4);margin-top:4px">{hint}</div>' if hint else ""
    return f"""<div class="k-card-context">
  <div class="k-card-h"><div class="k-card-t">{title}</div>{hint_html}</div>
  <div class="k-card-b">{body}</div>
</div>"""


def k_radar_notification_card(alerts: list[dict]) -> str:
    """Render the financial radar strip.

    Args:
        alerts: List of dicts with keys: category, current, baseline, ratio.
                Empty list means all categories are within bounds.

    Returns:
        HTML string for st.markdown(unsafe_allow_html=True).
    """
    if not alerts:
        return """<div class="k-radar-strip ok">
  <div class="k-radar-title">✓ Conformidade financeira</div>
  <div style="font-family:var(--font-sans);font-size:12.5px;color:var(--ink-3)">
    Nenhuma categoria acima do padrão histórico.
  </div>
</div>"""

    rows_html = "".join(
        f"""<div class="k-radar-alert-row">
  <span class="cat">⚠ {html_escape(a["category"])}</span>
  <span class="ratio">{a["ratio"]:.2f}×</span>
  <span class="amounts">
    R${a["current"]:,.2f} vs R${a["baseline"]:,.2f} histórico
  </span>
</div>"""
        for a in alerts
    )
    tone = "warn" if max(a["ratio"] for a in alerts) < 1.6 else ""
    return f"""<div class="k-radar-strip {tone}">
  <div class="k-radar-title">🔥 Radar financeiro — {len(alerts)} alerta{'s' if len(alerts) > 1 else ''}</div>
  {rows_html}
</div>"""


def plotly_dark_theme(max_height: int = 220) -> dict:
    """Return a Plotly layout dict matching the Klipper dark design system.

    Usage:
        fig.update_layout(**plotly_dark_theme())
        fig.update_layout(**plotly_dark_theme(max_height=180))
    """
    return {
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor":  "rgba(0,0,0,0)",
        "height": max_height,
        "margin": {"l": 0, "r": 0, "t": 8, "b": 0},
        "font": {
            "family": "JetBrains Mono, Geist, Inter, monospace",
            "color":  "#94A3B8",
            "size":   12,
        },
        "showlegend": False,
        "xaxis": {
            "showgrid": False,
            "zeroline": False,
            "tickfont": {"size": 11, "color": "#94A3B8"},
            "linecolor": "rgba(255,255,255,0.07)",
        },
        "yaxis": {
            "showgrid": True,
            "gridcolor": "rgba(255,255,255,0.05)",
            "zeroline": False,
            "tickfont": {"size": 11, "color": "#94A3B8"},
        },
        "hoverlabel": {
            "bgcolor": "#0D1726",
            "bordercolor": "#1E293B",
            "font": {"color": "#F1F5F9", "size": 12},
        },
    }


def k_premium_empty_state(icon: str, title: str, subtitle: str = "") -> str:
    """Premium empty-state card — replaces raw Python errors and blank pages.

    All user-supplied strings are XSS-escaped.
    """
    safe_icon     = html_escape(icon)
    safe_title    = html_escape(title)
    sub_html = (
        f'<div class="sub">{html_escape(subtitle)}</div>'
        if subtitle else ""
    )
    return f"""<div class="k-empty-state">
  <div class="icon">{safe_icon}</div>
  <div class="title">{safe_title}</div>
  {sub_html}
</div>"""


def seg_ctrl(options: list[str], active: int = 0, key: str = "seg") -> int:
    """Render a segmented control; returns the index of the selected segment."""
    import streamlit as _st
    html = '<div class="k-seg-ctrl">'
    for i, opt in enumerate(options):
        cls = "seg active" if i == active else "seg"
        html += f'<div class="{cls}" id="seg-{key}-{i}">{opt}</div>'
    html += "</div>"
    _st.markdown(html, unsafe_allow_html=True)
    selected = _st.radio(
        "", options, index=active, horizontal=True,
        label_visibility="collapsed", key=f"_seg_{key}"
    )
    return options.index(selected)


def feed_row(icon: str, icon_cls: str, title: str, meta: str,
             value: str, val_cls: str = "", note: str = "") -> str:
    note_html = f'<div class="k-feed-note">"{note}"</div>' if note else ""
    return f"""<div class="k-feed-row">
  <div class="k-feed-icon {icon_cls}">{icon}</div>
  <div class="k-feed-body">
    <div class="k-feed-title">{title}</div>
    <div class="k-feed-meta">{meta}</div>
    {note_html}
  </div>
  <div class="k-feed-val {val_cls}">{value}</div>
</div>"""


def mood_chip(mood: str) -> str:
    label_map = {
        "planejado": "planejado", "necessario": "necessário", "prazer": "prazer",
        "impulso": "impulso", "renda": "renda", "obrigatorio": "obrigatório",
        "social": "social", "saude": "saúde", "recorrente": "recorrente",
        "investimento": "investimento",
    }
    label = label_map.get(mood, mood)
    return f'<span class="k-mood {mood}">{label}</span>'


def chip(text: str, tone: str = "") -> str:
    return f'<span class="k-chip {tone}">{text}</span>'


def bar_track(value: float, max_val: float, tone: str = "") -> str:
    pct = min(value / max_val * 100, 100) if max_val > 0 else 0
    cls = f"k-bar-fill {tone}".strip()
    return f"""<div class="k-bar-track">
  <div class="{cls}" style="width:{pct:.1f}%"></div>
</div>"""


def section_header(title: str, sub: str = "") -> str:
    sub_html = f'<span class="s">{sub}</span>' if sub else ""
    return f'<div class="k-sec-h"><span class="t">{title}</span>{sub_html}</div>'


def engine_row(eid: str, name: str, tone: str = "ok") -> str:
    return f"""<div class="k-engine-row {tone}">
  <span class="eid">{eid}</span>
  <span>{name}</span>
  <span class="pulse"></span>
</div>"""


def parcela_row(title: str, store: str, start: str, end_: str, tag: str,
                monthly: float, n_total: int, n_paid: int, card_name: str = "") -> str:
    pct = (n_paid / n_total * 100) if n_total > 0 else 0
    remaining = n_total - n_paid
    total = monthly * n_total
    already_paid = monthly * n_paid
    card_html = f" · {card_name}" if card_name else ""
    return f"""<div class="k-parcela">
  <div style="display:flex;align-items:baseline;justify-content:space-between;gap:12px">
    <div>
      <div style="font-family:var(--font-sans);font-size:14px;color:var(--ink);font-weight:500">{title}</div>
      <div style="font-family:var(--font-sans);font-size:11px;color:var(--ink-3);margin-top:3px">
        {store} · <span class="mono">{start} → {end_}</span> · #{tag}{card_html}
      </div>
    </div>
    <div style="text-align:right;flex-shrink:0">
      <div class="mono" style="font-size:18px;color:var(--brass);font-variant-numeric:tabular-nums">
        {fmt_brl(monthly)}<span class="mono muted" style="font-size:11px"> /mês</span>
      </div>
      <div class="mono muted" style="font-size:11px">{n_paid}/{n_total} pagas · faltam {fmt_brl(monthly * remaining, compact=True)}</div>
    </div>
  </div>
  <div style="height:8px;background:var(--surface-2);border:1px solid var(--rule);border-radius:var(--radius-pill);overflow:hidden;margin-top:14px">
    <div class="k-parcela-fill" style="width:{pct:.1f}%;height:100%"></div>
  </div>
  <div style="display:flex;justify-content:space-between;margin-top:8px;font-family:var(--font-mono);font-size:10px;color:var(--ink-4)">
    <span>{fmt_brl(total, compact=True)} contratado</span>
    <span class="pos">{fmt_brl(already_paid, compact=True)} pago</span>
    <span>{fmt_brl(monthly * remaining, compact=True)} restante</span>
  </div>
</div>"""


def sidebar_brand() -> str:
    return f"""<div style="padding:18px 16px 10px">
  <div style="display:flex;align-items:center;gap:10px">
    <div style="width:38px;height:38px;flex-shrink:0;overflow:hidden;border-radius:10px;
      box-shadow:0 0 0 1px var(--rule-brass)">
      {brand_icon_img(38)}
    </div>
    <div>
      <div style="font-family:'General Sans','Inter',sans-serif;font-size:20px;font-weight:600;
        letter-spacing:-0.025em;color:var(--ink);line-height:1">Klipper</div>
      <div style="font-size:9px;letter-spacing:0.18em;text-transform:uppercase;
        color:var(--ink-4);font-weight:500;margin-top:3px">Wealth · operating system</div>
    </div>
  </div>
</div>"""


def sidebar_engines(violations: int = 0) -> str:
    rows = [
        engine_row("M1", "Quant", "ok"),
        engine_row("M2", "Governance", "neg" if violations > 0 else "ok"),
        engine_row("M3", "Context", "ok"),
        engine_row("AB", "Anti-BS", "ok"),
        engine_row("FR", "Fragility", "ok"),
    ]
    return f"""<div style="margin:8px 12px;padding:12px;background:var(--surface-1);
      border:1px solid var(--rule);border-radius:var(--radius-sm)">
  <div style="font-size:9.5px;letter-spacing:0.16em;text-transform:uppercase;
    color:var(--ink-4);font-weight:600;margin-bottom:8px">WikiAgent · M·</div>
  {"".join(rows)}
</div>"""


def budget_bar(category: str, gasto: float, limite: float) -> None:
    """Renders a nautical budget progress bar via st.markdown."""
    pct   = (gasto / limite * 100) if limite > 0 else 0
    tone  = "neg" if pct >= 100 else "warn" if pct >= 80 else "pos"
    sc    = "var(--rust)" if pct >= 100 else "var(--lantern)" if pct >= 80 else "var(--moss)"
    lbl   = "ESTOURO" if pct >= 100 else "ALERTA" if pct >= 80 else "OK"
    st.markdown(f"""<div style="margin-bottom:14px">
  <div style="display:flex;justify-content:space-between;font-family:var(--font-sans);font-size:12px;margin-bottom:6px">
    <span style="color:var(--ink)">{category}</span>
    <span class="mono" style="color:{sc}">{fmt_brl(gasto, compact=True)} / {fmt_brl(limite, compact=True)}</span>
  </div>
  {bar_track(gasto, limite, tone)}
  <div style="text-align:right;margin-top:4px;font-family:var(--font-mono);font-size:10px;color:{sc}">{pct:.1f}% · {lbl}</div>
</div>""", unsafe_allow_html=True)


def score_circle(score: int) -> None:
    """Renders a Plotly gauge circle for the score (0–100)."""
    import plotly.graph_objects as go
    color = "#7BC68A" if score >= 80 else "#D9B26F" if score >= 60 else "#F4D58D" if score >= 40 else "#D87C6A"
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        domain={"x": [0, 1], "y": [0, 1]},
        gauge={
            "axis": {"range": [0, 100], "visible": False},
            "bar": {"color": color},
            "bgcolor": "rgba(255,255,255,0.05)",
            "borderwidth": 0,
            "steps": [
                {"range": [0, 40], "color": "rgba(216,124,106,0.08)"},
                {"range": [40, 60], "color": "rgba(244,213,141,0.08)"},
                {"range": [60, 80], "color": "rgba(217,178,111,0.08)"},
                {"range": [80, 100], "color": "rgba(123,198,138,0.08)"},
            ],
        },
        number={"font": {"family": "Geist Mono, IBM Plex Mono, monospace", "size": 42, "color": color}},
    ))
    fig.update_layout(
        height=200, margin=dict(l=20, r=20, t=20, b=20),
        paper_bgcolor="rgba(0,0,0,0)", font={"color": "#F2EAD3"},
    )
    st.plotly_chart(fig, use_container_width=True)


def metric_card(titulo: str, valor: str, subtitulo: str = "", cor: str = "default") -> None:
    """Backward-compatible: renders a stat card via st.markdown."""
    tone_map = {"success": "pos", "danger": "neg", "warning": "warn", "primary": "brass"}
    st.markdown(stat_card(titulo, valor, subtitulo, tone_map.get(cor, "")), unsafe_allow_html=True)


def payment_badge(method: str) -> str:
    icons = {
        "PIX": "◎", "CARTAO_CREDITO": "▣", "CARTAO_DEBITO": "◰",
        "DINHEIRO": "◈", "TED": "↹", "BOLETO": "▤", "TRANSFERENCIA": "⇌",
    }
    labels = {
        "PIX": "PIX", "CARTAO_CREDITO": "Crédito", "CARTAO_DEBITO": "Débito",
        "DINHEIRO": "Dinheiro", "TED": "TED", "BOLETO": "Boleto", "TRANSFERENCIA": "Transfer.",
    }
    return f'<span class="k-chip">{icons.get(method, "○")} {labels.get(method, method)}</span>'


def sidebar_user(scenario: str | None = None) -> None:
    """Renders user card + Settings / Logout buttons in the sidebar."""
    _scenario = scenario or st.session_state.get("klipper_scenario", "realista")
    st.markdown(f"""<div style="padding:12px 16px 4px;border-top:1px solid var(--rule);
      background:var(--surface-1);margin-top:8px;border-radius:0 0 var(--radius-sm) var(--radius-sm)">
  <div style="display:flex;align-items:center;gap:10px">
    <div style="width:30px;height:30px;border-radius:50%;
      background:linear-gradient(135deg,var(--brass),#8C6A35);
      color:#1A1106;display:flex;align-items:center;justify-content:center;
      font-family:var(--font-sans);font-size:12px;font-weight:700;
      box-shadow:0 0 0 1px var(--rule-brass);flex-shrink:0">RM</div>
    <div style="min-width:0;flex:1">
      <div style="font-family:var(--font-sans);font-size:12.5px;color:var(--ink);font-weight:500">Roberto Milet</div>
      <div style="font-family:var(--font-mono);font-size:9.5px;color:var(--ink-4);letter-spacing:0.04em">cenário · {_scenario}</div>
    </div>
  </div>
</div>""", unsafe_allow_html=True)

    col_cfg, col_out = st.columns(2)
    with col_cfg:
        if st.button("⚙ Config", width="stretch", key="btn_settings"):
            _open_settings_dialog()
    with col_out:
        if st.button("↩ Sair", width="stretch", key="btn_logout"):
            try:
                from core.auth import logout
                logout()
            except Exception as e:
                import logging as _log
                _log.getLogger(__name__).warning("Erro inesperado no logout: %s", e)
            st.rerun()


@st.dialog("Configurações · Klipper")
def _open_settings_dialog() -> None:
    """Modal de configurações do usuário."""
    import logging as _log
    _logger = _log.getLogger(__name__)

    st.markdown("**Cenário financeiro**")
    scenarios = ["realista", "otimista", "pessimista"]
    current = st.session_state.get("klipper_scenario", "realista")
    new_scenario = st.selectbox(
        "Cenário", scenarios, index=scenarios.index(current), label_visibility="collapsed"
    )
    if new_scenario != current:
        st.session_state["klipper_scenario"] = new_scenario

    st.divider()
    st.markdown("**Autenticação em dois fatores (TOTP)**")

    try:
        from core.auth import (
            has_totp, start_totp_enrollment,
            confirm_totp_enrollment, cancel_totp_enrollment, unenroll_totp,
        )
        totp_active = has_totp()
    except Exception as e:
        _logger.warning("Erro ao verificar TOTP: %s", e)
        totp_active = False

    enrolling = bool(st.session_state.get("settings_enroll_factor_id"))

    if enrolling:
        _render_inline_enroll()
    elif totp_active:
        st.success("2FA ativo — Google Authenticator / Authy")
        if st.button("Desativar 2FA", type="secondary"):
            try:
                unenroll_totp()
                st.success("2FA removido.")
                st.rerun()
            except Exception as e:
                st.error(str(e))
    else:
        st.info("2FA não cadastrado. Ative para maior segurança.")
        if st.button("Ativar 2FA (TOTP)", type="primary"):
            start_totp_enrollment()

    if not enrolling:
        st.divider()
        if st.button("Salvar e fechar", width="stretch"):
            st.rerun()


def _render_inline_enroll() -> None:
    """Renderiza o fluxo de enrollment TOTP inline no settings dialog."""
    import html as _html
    from core.auth import confirm_totp_enrollment, cancel_totp_enrollment

    qr_b64 = st.session_state.get("settings_enroll_qr", "")
    secret  = st.session_state.get("settings_enroll_secret", "")

    st.markdown("Escaneie o QR code com Google Authenticator, Authy ou similar.")

    if qr_b64:
        st.markdown(
            f'<div style="text-align:center;margin:12px 0">'
            f'<img src="data:image/png;base64,{qr_b64}" width="180" '
            f'style="border-radius:8px;border:4px solid white" alt="QR Code TOTP"></div>',
            unsafe_allow_html=True,
        )
    if secret:
        st.markdown(
            f'<div style="font-family:var(--font-mono);font-size:11px;color:var(--ink-3);'
            f'text-align:center;margin-bottom:12px">Chave: <strong>{_html.escape(secret)}</strong></div>',
            unsafe_allow_html=True,
        )

    code = st.text_input("Código TOTP (6 dígitos)", max_chars=6, placeholder="000000")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Confirmar 2FA", type="primary", width="stretch"):
            if not code or len(code) < 6:
                st.error("Código deve ter 6 dígitos.")
            else:
                ok, err = confirm_totp_enrollment(code.strip())
                if ok:
                    st.success("2FA ativado com sucesso!")
                    st.rerun()
                else:
                    st.error(err)
    with col2:
        if st.button("Cancelar", width="stretch"):
            cancel_totp_enrollment()
            st.rerun()


def sidebar_ai_qa(ctx=None) -> None:
    """Kira — persistent AI Q&A sidebar widget. ctx is an optional FinancialContext."""
    import logging as _log
    _logger = _log.getLogger(__name__)

    with st.expander("◈ Kira · IA Financeira", expanded=False):
        hist_key = "kira_history"
        if hist_key not in st.session_state:
            st.session_state[hist_key] = []

        history: list[dict] = st.session_state[hist_key]

        if history:
            msgs_html = ""
            for m in history[-6:]:
                cls = "user" if m["role"] == "user" else ""
                import html as _html_mod
                msgs_html += (
                    f'<div class="k-kira-bubble {cls}" style="margin-bottom:6px">'
                    f'{_html_mod.escape(m["content"])}'
                    f'</div>'
                )
            st.markdown(msgs_html, unsafe_allow_html=True)

        q = st.text_input(
            "Pergunta", placeholder="ex: estou dentro do orçamento?",
            label_visibility="collapsed", key="kira_input",
        )
        col_ask, col_clear = st.columns([3, 1])
        with col_ask:
            ask_clicked = st.button("Perguntar", type="primary", width="stretch", key="kira_ask")
        with col_clear:
            if st.button("↺", width="stretch", key="kira_clear"):
                st.session_state[hist_key] = []
                st.rerun()

        if ask_clicked and q.strip():
            try:
                from core.financial_ai import ask as _ask
                history.append({"role": "user", "content": q.strip()})
                with st.spinner("Kira está pensando…"):
                    resp = _ask(
                        q.strip(),
                        ctx=ctx,
                        history=[m for m in history[:-1]],
                    )
                history.append({"role": "assistant", "content": resp})
                st.session_state[hist_key] = history
                st.rerun()
            except RuntimeError as e:
                st.warning(f"Kira indisponível: {e}")
            except Exception as e:
                _logger.error("Kira error: %s", e)
                st.error("Erro ao contatar a IA. Tente novamente.")


# ── Novos componentes de layout ────────────────────────────────────────────────

def hero_section(
    title: str,
    saldo: str,
    ganhos: str,
    gastos: str,
    subtitle: str = "",
) -> str:
    """Renderiza o hero colorido no topo da página.

    Args:
        title:    Label acima do saldo (ex: 'maio · 2026').
        saldo:    Saldo líquido formatado (ex: 'R$ 3.500,00').
        ganhos:   Total de entradas do mês (ex: 'R$ 8.000,00').
        gastos:   Total de saídas do mês (ex: 'R$ 4.500,00').
        subtitle: Linha opcional abaixo do título.
    """
    sub_html = (
        f'<div style="font-family:var(--font-sans);font-size:11px;'
        f'color:var(--ink-4);margin-top:2px">{subtitle}</div>'
        if subtitle else ""
    )
    return f"""<div class="k-hero">
  <div class="k-hero-kicker">{title}</div>
  {sub_html}
  <div class="k-hero-balance">{saldo}</div>
  <div class="k-hero-stats-row">
    <div class="k-hero-stat">
      <span class="k-hero-stat-label">Entradas</span>
      <span class="k-hero-stat-val" style="color:var(--emerald)">{ganhos}</span>
    </div>
    <div class="k-hero-divider"></div>
    <div class="k-hero-stat">
      <span class="k-hero-stat-label">Saídas</span>
      <span class="k-hero-stat-val" style="color:var(--electric)">{gastos}</span>
    </div>
  </div>
</div>"""


def tx_row(
    category: str,
    name: str,
    date_str: str,
    subcategory: str,
    amount: str,
    tone: str = "neg",
    notes: str = "",
) -> str:
    """Renderiza uma linha de transação no estilo do referencial.

    Args:
        category:    Nome da categoria (ex: 'Alimentação').
        name:        Descrição da transação.
        date_str:    Data formatada (ex: '23/Mai').
        subcategory: Sub-label ou tag de categoria.
        amount:      Valor formatado (ex: '-R$ 45,00').
        tone:        'pos', 'neg' ou 'warn' — cor do valor.
        notes:       Nota opcional exibida abaixo da data.
    """
    color, bg = CAT_COLORS.get(category, ("#8F8770", "rgba(143,135,112,0.12)"))
    initial = category[0].upper() if category else "?"
    notes_html = (
        f'<div class="k-tx-notes">{notes}</div>' if notes else ""
    )
    return (
        f'<div class="k-tx-row">'
        f'<div class="k-tx-icon" style="background:{bg};color:{color}">{initial}</div>'
        f'<div class="k-tx-body">'
        f'<div class="k-tx-name">{name}</div>'
        f'<div class="k-tx-meta">{date_str} · {subcategory}</div>'
        f'{notes_html}'
        f'</div>'
        f'<div class="k-tx-amount {tone}">{amount}</div>'
        f'</div>'
    )


def setup_sidebar(
    ctx=None,
    violations: int = 0,
    include_ai_qa: bool = True,
) -> None:
    """Configura a sidebar nativa do Streamlit com nav, engines, user e Kira Q&A.

    Substitui o padrão legado st.columns([1,4]) em todas as páginas.

    Args:
        ctx:           Contexto financeiro para o Q&A da Kira (opcional).
        violations:    Número de violações M2 (colore o badge Governance).
        include_ai_qa: Se False, omite o widget de Q&A da Kira.
    """
    with st.sidebar:
        render_navigation()
        st.markdown(sidebar_engines(violations), unsafe_allow_html=True)
        sidebar_user()
        if include_ai_qa:
            sidebar_ai_qa(ctx)
