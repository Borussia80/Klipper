"""core/styles.py — Klipper nautical theme for Streamlit."""

from __future__ import annotations
import streamlit as st

# ──────────────────────────────────────────────────────────────────────────────
# CSS
# ──────────────────────────────────────────────────────────────────────────────

KLIPPER_CSS = """
<style>
/* ── Fonts ─────────────────────────────────────────────────────────────────── */
@import url('https://api.fontshare.com/v2/css?f[]=general-sans@200,300,400,500,600,700&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Geist+Mono:wght@400;500;600&display=swap');

/* ── Tokens ─────────────────────────────────────────────────────────────────── */
:root {
  --bg:           #08161F;
  --bg-2:         #0C1E2B;
  --surface-1:    rgba(255,255,255,0.025);
  --surface-2:    rgba(255,255,255,0.045);
  --surface-3:    rgba(255,255,255,0.07);
  --surface-tint: rgba(200,163,100,0.04);
  --ink:          #F2EAD3;
  --ink-2:        #C9BC9E;
  --ink-3:        #8F8770;
  --ink-4:        #5C5746;
  --rule:         rgba(255,255,255,0.06);
  --rule-2:       rgba(255,255,255,0.10);
  --rule-brass:   rgba(200,163,100,0.22);
  --brass:        #D9B26F;
  --brass-soft:   rgba(217,178,111,0.18);
  --brass-glow:   rgba(217,178,111,0.35);
  --sea:          #7FB3C8;
  --copper:       #E08855;
  --moss:         #7BC68A;
  --rust:         #D87C6A;
  --lantern:      #F4D58D;
  --pos:          #7BC68A;
  --neg:          #D87C6A;
  --warn:         #F4D58D;
  --accent:       #D9B26F;
  --shadow-1:     0 1px 0 rgba(255,255,255,0.04) inset, 0 6px 18px rgba(0,0,0,0.35);
  --shadow-2:     0 1px 0 rgba(255,255,255,0.05) inset, 0 12px 32px rgba(0,0,0,0.42);
  --glow-brass:   0 0 0 1px rgba(217,178,111,0.15), 0 0 32px rgba(217,178,111,0.10);
  --font-serif:   'Instrument Serif', Georgia, serif;
  --font-sans:    'General Sans', 'Inter', sans-serif;
  --font-mono:    'Geist Mono', 'IBM Plex Mono', monospace;
  --radius-xs:    6px;
  --radius-sm:    10px;
  --radius:       16px;
  --radius-lg:    20px;
  --radius-pill:  999px;
  --ease:         cubic-bezier(0.2,0.7,0.2,1);
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

/* sidebar */
section[data-testid="stSidebar"] {
  background: linear-gradient(180deg,
    color-mix(in oklab, #08161F 96%, white 4%) 0%,
    #0C1E2B 100%) !important;
  border-right: 1px solid var(--rule) !important;
}
section[data-testid="stSidebar"] > div {
  background: transparent !important;
  padding-top: 12px !important;
}
[data-testid="stSidebarNavSeparator"] { display: none !important; }
[data-testid="stSidebarNavItems"] { padding: 0 !important; }
[data-testid="stSidebarNavLink"] {
  color: var(--ink-2) !important;
  font-family: var(--font-sans) !important;
  font-size: 13px !important;
  border-radius: var(--radius-xs) !important;
  padding: 8px 12px !important;
  margin: 1px 4px !important;
  transition: background 160ms, color 160ms !important;
}
[data-testid="stSidebarNavLink"]:hover {
  background: var(--surface-1) !important;
  color: var(--ink) !important;
}
[data-testid="stSidebarNavLink"][aria-current="page"] {
  background: var(--surface-2) !important;
  color: var(--ink) !important;
  border-left: 2px solid var(--brass) !important;
}
[data-testid="stSidebarNavLink"] span { font-family: var(--font-sans) !important; }

/* main content area */
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

/* inputs */
.stTextInput input, .stNumberInput input, .stTextArea textarea {
  background: var(--surface-2) !important;
  border: 1px solid var(--rule) !important;
  color: var(--ink) !important;
  border-radius: var(--radius-sm) !important;
  font-family: var(--font-sans) !important;
}
.stTextInput input:focus, .stNumberInput input:focus {
  border-color: var(--brass) !important;
  box-shadow: 0 0 0 1px var(--brass) !important;
}
.stSelectbox [data-baseweb="select"] {
  background: var(--surface-2) !important;
  border: 1px solid var(--rule) !important;
  border-radius: var(--radius-sm) !important;
}
.stSelectbox [data-baseweb="select"] > div { background: transparent !important; color: var(--ink) !important; }

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
  background: linear-gradient(90deg, color-mix(in oklab, var(--brass), black 30%), var(--brass));
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
  background: linear-gradient(90deg, color-mix(in oklab, var(--brass), black 20%), var(--brass));
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
</style>
"""

# ──────────────────────────────────────────────────────────────────────────────
# Python helpers
# ──────────────────────────────────────────────────────────────────────────────

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


@__import__("functools").lru_cache(maxsize=None)
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


def inject_css() -> None:
    st.markdown(KLIPPER_CSS, unsafe_allow_html=True)


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


def kicker(text: str) -> str:
    return f'<div class="k-kicker">{text}</div>'


def k_card(content: str, gilt: bool = False, extra_style: str = "") -> str:
    cls = "k-card" + (" gilt" if gilt else "")
    style = f' style="{extra_style}"' if extra_style else ""
    return f'<div class="{cls}"{style}><div class="k-card-b">{content}</div></div>'


def k_card_with_header(title: str, content: str, hint: str = "", gilt: bool = False) -> str:
    cls = "k-card" + (" gilt" if gilt else "")
    hint_html = f'<div style="font-family:var(--font-sans);font-size:11.5px;color:var(--ink-3);margin-top:2px">{hint}</div>' if hint else ""
    return f"""<div class="{cls}">
  <div class="k-card-h">
    <div>
      <div class="k-card-t">{title}</div>
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


def sidebar_user(scenario: str = "realista") -> str:
    return f"""<div style="padding:12px 16px;border-top:1px solid var(--rule);
      background:var(--surface-1);margin-top:8px">
  <div style="display:flex;align-items:center;gap:10px">
    <div style="width:30px;height:30px;border-radius:50%;
      background:linear-gradient(135deg,var(--brass),#8C6A35);
      color:#1A1106;display:flex;align-items:center;justify-content:center;
      font-family:var(--font-sans);font-size:12px;font-weight:700;
      box-shadow:0 0 0 1px var(--rule-brass);flex-shrink:0">RM</div>
    <div style="min-width:0;flex:1">
      <div style="font-family:var(--font-sans);font-size:12.5px;color:var(--ink);font-weight:500">Roberto Milet</div>
      <div style="font-family:var(--font-mono);font-size:9.5px;color:var(--ink-4);letter-spacing:0.04em">cenário · {scenario}</div>
    </div>
  </div>
</div>"""
