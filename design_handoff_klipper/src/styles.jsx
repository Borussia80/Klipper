// styles.jsx — Klipper nautical · v2 (depth, glass, blur, layered type)

const KLIPPER_CSS = `
/* ─────────────────────────────────────────────────────────────
   RESET + BASE
   ───────────────────────────────────────────────────────────── */
*, *::before, *::after { box-sizing: border-box; }
html, body { margin: 0; padding: 0; }
html { color-scheme: dark; }
body {
  background: var(--bg);
  color: var(--ink);
  font-family: var(--font-sans);
  font-size: 13.5px;
  line-height: 1.5;
  -webkit-font-smoothing: antialiased;
  text-rendering: optimizeLegibility;
  font-feature-settings: "ss01", "cv01", "cv11";
  min-height: 100vh;
  overflow-x: hidden;
}
button { font: inherit; color: inherit; cursor: pointer; background: none; border: 0; padding: 0; }
input, textarea, select { font: inherit; color: inherit; }
a { color: inherit; text-decoration: none; }

/* AMBIENT LIGHT — radial gradient that bleeds the brass/sea into the canvas */
body::before {
  content: '';
  position: fixed; inset: 0; z-index: 0; pointer-events: none;
  background: var(--ambient, none);
  opacity: 0.9;
}

/* ─────────────────────────────────────────────────────────────
   APP SHELL
   ───────────────────────────────────────────────────────────── */
.k-app {
  position: relative; z-index: 1;
  display: grid;
  grid-template-columns: 248px 1fr;
  min-height: 100vh;
  background: transparent;
}

/* SIDEBAR — fixed, glass */
.k-side {
  position: sticky; top: 0; height: 100vh;
  border-right: 1px solid var(--rule);
  background: linear-gradient(180deg,
    color-mix(in oklab, var(--bg) 96%, white 4%) 0%,
    var(--bg-2) 100%);
  display: flex; flex-direction: column; overflow: hidden;
  z-index: 2;
}
.k-side-h {
  padding: 22px 20px 16px;
}
.k-brand {
  display: flex; align-items: center; gap: 12px;
  font-family: "General Sans", "Inter", sans-serif;
  font-size: 22px; font-weight: 600; letter-spacing: -0.025em;
  color: var(--ink);
  line-height: 1;
}
.k-brand-mark {
  /* legacy badge — kept for any callers, but BrandMark now renders an image directly */
  display: grid; place-items: center;
  flex-shrink: 0;
}
.k-tagline {
  margin-top: 6px;
  font-family: var(--font-ui);
  font-size: 10px; letter-spacing: 0.18em; text-transform: uppercase;
  color: var(--ink-3); font-weight: 500;
}

/* sidebar live snapshot — tiny patrimônio + delta + cash bar */
.k-side-snap {
  margin: 4px 14px 6px;
  padding: 12px 14px;
  background: var(--surface-2);
  border: 1px solid var(--rule);
  border-radius: var(--radius-sm);
  display: flex; flex-direction: column; gap: 6px;
  position: relative; overflow: hidden;
}
.k-side-snap::before {
  content: ''; position: absolute; inset: -1px;
  background: radial-gradient(circle at top left, var(--brass-soft), transparent 70%);
  pointer-events: none;
}
.k-side-snap > * { position: relative; z-index: 1; }
.k-side-snap .lbl { font-size: 9.5px; letter-spacing: 0.15em; text-transform: uppercase; color: var(--ink-3); }
.k-side-snap .v { font-family: var(--font-serif); font-size: 19px; line-height: 1; color: var(--ink);
  font-variant-numeric: tabular-nums; letter-spacing: -0.01em; }
.k-side-snap .d { font-family: var(--font-mono); font-size: 11px; }

.k-nav { padding: 10px 8px; display: flex; flex-direction: column; gap: 1px; flex: 1; min-height: 0;
  overflow-y: auto; }
.k-nav::-webkit-scrollbar { width: 0; }
.k-nav-section {
  font-family: var(--font-ui);
  font-size: 9.5px; letter-spacing: 0.16em; text-transform: uppercase;
  color: var(--ink-4); padding: 16px 14px 8px; font-weight: 600;
}
.k-nav-i {
  display: flex; align-items: center; gap: 10px;
  padding: 9px 12px; border-radius: var(--radius-xs);
  font-family: var(--font-ui);
  font-size: 13px; color: var(--ink-2); font-weight: 450;
  cursor: pointer; text-align: left; width: 100%; white-space: nowrap;
  transition: background 160ms var(--ease), color 160ms var(--ease);
  position: relative;
}
.k-nav-i:hover { background: var(--surface-1); color: var(--ink); }
.k-nav-i.is-active {
  background: var(--surface-2); color: var(--ink);
}
.k-nav-i.is-active::before {
  content: ''; position: absolute; left: -8px; top: 8px; bottom: 8px; width: 2px;
  background: var(--brass); border-radius: 2px; box-shadow: 0 0 8px var(--brass-glow);
}
.k-nav-mark {
  width: 16px; height: 16px;
  display: grid; place-items: center;
  font-family: var(--font-mono); font-size: 13px; color: var(--ink-3); opacity: 0.85;
}
.k-nav-i.is-active .k-nav-mark { color: var(--brass); opacity: 1; }
.k-nav-i .k-nav-tag {
  margin-left: auto; font-family: var(--font-mono); font-size: 10px;
  color: var(--ink); padding: 1px 6px; border-radius: var(--radius-pill);
  background: var(--surface-2); border: 1px solid var(--rule);
}
.k-nav-i .k-nav-tag.warn { color: var(--lantern); border-color: rgba(244,213,141,0.3); }
.k-nav-i .k-nav-tag.neg  { color: var(--rust); border-color: rgba(216,124,106,0.3); }
.k-nav-i .k-nav-tag.pos  { color: var(--moss); border-color: rgba(123,198,138,0.3); }

/* engines mini-status */
.k-engines {
  margin: 10px 12px 8px;
  padding: 12px 12px;
  background: var(--surface-1);
  border: 1px solid var(--rule);
  border-radius: var(--radius-sm);
  display: flex; flex-direction: column; gap: 6px;
}
.k-engine-row {
  display: grid; grid-template-columns: 22px 1fr auto; align-items: center; gap: 8px;
  font-family: var(--font-ui); font-size: 11.5px; color: var(--ink-2);
  white-space: nowrap;
}
.k-engine-row .id {
  font-family: var(--font-mono); font-size: 9px; letter-spacing: 0.06em;
  padding: 2px 4px; border-radius: 3px;
  background: rgba(0,0,0,0.25); border: 1px solid var(--rule);
  text-align: center; min-width: 22px;
}
.k-engine-row .pulse {
  width: 6px; height: 6px; border-radius: 50%;
  position: relative;
}
.k-engine-row .pulse::after {
  content: ''; position: absolute; inset: -3px; border-radius: 50%;
  border: 1px solid currentColor; opacity: 0.3;
  animation: k-pulse 2s ease-out infinite;
}
.k-engine-row.ok    .pulse, .k-engine-row.ok    .id { color: var(--moss); }
.k-engine-row.ok    .pulse { background: var(--moss); }
.k-engine-row.warn  .pulse, .k-engine-row.warn  .id { color: var(--lantern); }
.k-engine-row.warn  .pulse { background: var(--lantern); }
.k-engine-row.neg   .pulse, .k-engine-row.neg   .id { color: var(--rust); }
.k-engine-row.neg   .pulse { background: var(--rust); }
@keyframes k-pulse {
  0% { transform: scale(0.6); opacity: 0.6; }
  100% { transform: scale(2.2); opacity: 0; }
}

.k-side-f {
  padding: 14px 16px; border-top: 1px solid var(--rule);
  display: flex; flex-direction: column; gap: 10px; flex-shrink: 0;
  background: var(--surface-1);
}
.k-user { display: flex; align-items: center; gap: 10px; min-width: 0; }
.k-user .av {
  width: 30px; height: 30px; border-radius: 50%;
  background: linear-gradient(135deg, var(--brass), color-mix(in oklab, var(--brass), black 40%));
  color: var(--bg); display: grid; place-items: center;
  font-family: var(--font-serif); font-size: 12px; font-weight: 700;
  box-shadow: 0 0 0 1px var(--rule-brass);
  flex-shrink: 0;
}
.k-user .name { font-family: var(--font-ui); font-size: 12.5px; color: var(--ink);
  font-weight: 500; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; line-height: 1.1; }
.k-user .meta { font-family: var(--font-mono); font-size: 9.5px; color: var(--ink-4);
  letter-spacing: 0.04em; line-height: 1.2; margin-top: 2px; }

/* ─────────────────────────────────────────────────────────────
   TOPBAR
   ───────────────────────────────────────────────────────────── */
.k-top {
  display: flex; align-items: center; justify-content: space-between;
  padding: 18px 32px 14px;
  background: linear-gradient(180deg, color-mix(in oklab, var(--bg), black 5%), transparent);
  position: sticky; top: 0; z-index: 5; gap: 16px;
  -webkit-backdrop-filter: blur(16px);
  backdrop-filter: blur(16px);
  border-bottom: 1px solid var(--rule);
}
.k-top-l { display: flex; flex-direction: column; gap: 2px; min-width: 0; }
.k-top-title {
  font-family: var(--font-serif); font-size: 22px; font-weight: 500;
  color: var(--ink); letter-spacing: -0.01em; white-space: nowrap;
  margin: 0; line-height: 1.1;
}
.k-top-sub {
  font-family: var(--font-ui); font-size: 11px; letter-spacing: 0.10em;
  text-transform: uppercase; color: var(--ink-3); font-weight: 500;
  white-space: nowrap;
}
.k-top-r { display: flex; align-items: center; gap: 12px; font-family: var(--font-mono);
  font-size: 11px; color: var(--ink-3); white-space: nowrap; flex-shrink: 0; }

.k-coord {
  display: inline-flex; align-items: center; gap: 8px;
  padding: 5px 10px; border: 1px solid var(--rule); border-radius: var(--radius-pill);
  background: var(--surface-1); color: var(--ink-3);
}
.k-coord-dot { width: 5px; height: 5px; border-radius: 50%; background: var(--brass); box-shadow: 0 0 8px var(--brass-glow); }

/* MAIN */
.k-main { overflow-x: hidden; position: relative; min-width: 0; }
.k-page { padding: 24px 32px 80px; max-width: 1440px; }

/* ─────────────────────────────────────────────────────────────
   CARDS (glass surfaces with depth)
   ───────────────────────────────────────────────────────────── */
.k-card {
  background: var(--surface-2);
  border: 1px solid var(--rule);
  border-radius: var(--radius);
  box-shadow: var(--shadow-1);
  -webkit-backdrop-filter: blur(8px) saturate(140%);
  backdrop-filter: blur(8px) saturate(140%);
  display: flex; flex-direction: column;
  transition: transform 180ms var(--ease), box-shadow 180ms var(--ease), border-color 180ms var(--ease);
  position: relative; overflow: hidden;
}
.k-card.hover:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-2);
  border-color: var(--rule-2);
}
.k-card.elev-2 { background: var(--surface-3); box-shadow: var(--shadow-2); }
.k-card.glow {
  border-color: var(--rule-brass);
  box-shadow: var(--shadow-1), var(--glow-brass);
}
/* Brass top hairline accent for premium cards */
.k-card.gilt::before {
  content: ''; position: absolute; top: 0; left: 16px; right: 16px; height: 1px;
  background: linear-gradient(90deg, transparent, var(--brass), transparent);
  opacity: 0.5;
}
.k-card-h {
  padding: 16px 20px 12px;
  display: flex; align-items: flex-start; justify-content: space-between; gap: 16px;
}
.k-card-h > *:last-child { flex-shrink: 0; }
.k-card-t {
  font-family: var(--font-serif); font-size: 16px; color: var(--ink);
  font-weight: 500; line-height: 1.2; letter-spacing: -0.005em;
}
.k-card-hint { font-family: var(--font-ui); font-size: 11.5px; color: var(--ink-3); margin-top: 4px; font-weight: 400; }
.k-card-b { padding: 4px 20px 18px; }
.k-card-b.full { padding: 0; }
.k-kicker {
  font-family: var(--font-ui);
  font-size: 9.5px; letter-spacing: 0.16em; text-transform: uppercase;
  color: var(--brass); margin-bottom: 6px; font-weight: 600;
}

/* GRID UTILITIES */
.k-grid { display: grid; gap: 16px; }
.k-cols-2 { grid-template-columns: repeat(2, 1fr); }
.k-cols-3 { grid-template-columns: repeat(3, 1fr); }
.k-cols-4 { grid-template-columns: repeat(4, 1fr); }
.k-cols-12 { grid-template-columns: repeat(12, 1fr); }

/* METRICS */
.k-metric { display: flex; flex-direction: column; gap: 4px; min-width: 0; }
.k-metric-l {
  font-family: var(--font-ui); font-size: 10.5px; letter-spacing: 0.12em;
  text-transform: uppercase; color: var(--ink-3); font-weight: 600;
}
.k-metric-v {
  font-family: var(--font-serif); font-size: 30px; line-height: 1.05; color: var(--ink);
  font-variant-numeric: tabular-nums; letter-spacing: -0.015em;
}
.k-metric-d {
  display: flex; align-items: baseline; gap: 8px;
  font-family: var(--font-mono); font-size: 11.5px; font-variant-numeric: tabular-nums;
  color: var(--ink-3);
}
.k-metric-d.pos { color: var(--pos); }
.k-metric-d.neg { color: var(--neg); }

/* TABLE */
.k-tbl { width: 100%; border-collapse: collapse; font-family: var(--font-ui); font-size: 12.5px; }
.k-tbl th {
  text-align: left; font-weight: 600; color: var(--ink-3);
  font-family: var(--font-ui);
  font-size: 9.5px; letter-spacing: 0.14em; text-transform: uppercase;
  padding: 10px 16px; border-bottom: 1px solid var(--rule);
}
.k-tbl td { padding: 11px 16px; border-bottom: 1px solid var(--rule); color: var(--ink-2);
  vertical-align: middle; }
.k-tbl tr:last-child td { border-bottom: 0; }
.k-tbl tbody tr { transition: background 120ms var(--ease); }
.k-tbl tbody tr:hover td { background: var(--surface-1); color: var(--ink); }
.k-tbl .num { font-family: var(--font-mono); font-variant-numeric: tabular-nums;
  text-align: right; color: var(--ink); }
.k-tbl .pos { color: var(--pos); }
.k-tbl .neg { color: var(--neg); }
.k-tbl .ticker { font-family: var(--font-mono); font-weight: 600; color: var(--ink); letter-spacing: 0.02em; }

/* CHIP */
.k-chip {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 3px 9px; border-radius: var(--radius-pill);
  background: var(--surface-1); border: 1px solid var(--rule);
  font-family: var(--font-ui);
  font-size: 10.5px; color: var(--ink-2); letter-spacing: 0.01em;
  font-weight: 500; line-height: 1.4;
}
.k-chip.pos { color: var(--moss); border-color: rgba(123,198,138,0.3); background: rgba(123,198,138,0.06); }
.k-chip.neg { color: var(--rust); border-color: rgba(216,124,106,0.3); background: rgba(216,124,106,0.06); }
.k-chip.warn { color: var(--lantern); border-color: rgba(244,213,141,0.3); background: rgba(244,213,141,0.06); }
.k-chip.brass { color: var(--brass); border-color: var(--rule-brass); background: var(--brass-soft); }

/* BUTTON */
.k-btn {
  display: inline-flex; align-items: center; gap: 7px;
  padding: 7px 13px; border-radius: var(--radius-pill);
  background: var(--surface-2); border: 1px solid var(--rule);
  color: var(--ink); font-family: var(--font-ui); font-size: 12px;
  font-weight: 500; line-height: 1; white-space: nowrap;
  transition: background 140ms var(--ease), border-color 140ms var(--ease), transform 140ms var(--ease);
}
.k-btn:hover { background: var(--surface-3); border-color: var(--rule-2); }
.k-btn:active { transform: scale(0.97); }
.k-btn.primary {
  background: linear-gradient(180deg, var(--brass), color-mix(in oklab, var(--brass), black 18%));
  color: #1A1106; border-color: color-mix(in oklab, var(--brass), white 8%);
  font-weight: 600;
  box-shadow: 0 1px 0 rgba(255,255,255,0.2) inset, var(--glow-brass);
}
.k-btn.primary:hover { filter: brightness(1.1); }
.k-btn.ghost { background: transparent; border-color: transparent; color: var(--ink-3); }
.k-btn.ghost:hover { color: var(--ink); background: var(--surface-1); }

/* TABS */
.k-tabs { display: flex; gap: 4px; padding: 4px; background: var(--surface-1);
  border: 1px solid var(--rule); border-radius: var(--radius-pill); }
.k-tab {
  padding: 7px 14px; border-radius: var(--radius-pill);
  font-family: var(--font-ui); font-size: 12px; color: var(--ink-3);
  cursor: pointer; transition: all 140ms var(--ease); white-space: nowrap;
  font-weight: 500;
}
.k-tab:hover { color: var(--ink); }
.k-tab.is-active {
  background: var(--surface-3); color: var(--ink);
  box-shadow: 0 1px 0 rgba(255,255,255,0.05) inset;
}

/* PROVIDER pills */
.k-prov {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 3px 9px; border-radius: var(--radius-pill);
  font-family: var(--font-ui);
  font-size: 11px; color: var(--ink);
  border: 1px solid currentColor;
}

/* SECTION HEADER */
.k-sec-h {
  display: flex; align-items: baseline; justify-content: space-between;
  margin: 28px 0 14px;
}
.k-sec-h .t {
  font-family: var(--font-serif); font-size: 19px; font-weight: 500;
  color: var(--ink); letter-spacing: -0.005em;
}
.k-sec-h .s {
  font-family: var(--font-ui); font-size: 11px; letter-spacing: 0.1em;
  text-transform: uppercase; color: var(--ink-3); font-weight: 500;
}

/* SCROLL */
.k-main::-webkit-scrollbar, .k-page::-webkit-scrollbar { width: 8px; height: 8px; }
.k-main::-webkit-scrollbar-thumb { background: var(--rule-2); border-radius: 4px; }

/* SELECTION */
::selection { background: var(--brass-soft); color: var(--ink); }

/* HELPER classes */
.muted { color: var(--ink-3); }
.dim { color: var(--ink-4); }
.serif { font-family: var(--font-serif); }
.mono { font-family: var(--font-mono); font-variant-numeric: tabular-nums; }
.ui { font-family: var(--font-ui); }
.pos { color: var(--pos); } .neg { color: var(--neg); } .warn { color: var(--warn); }
.brass-c { color: var(--brass); }

/* ─────────────────────────────────────────────────────────────
   FEED · timeline
   ───────────────────────────────────────────────────────────── */
.k-feed { display: flex; flex-direction: column; gap: 0; }
.k-feed-day {
  display: grid; grid-template-columns: 88px 1fr; gap: 16px;
  padding: 14px 0;
  border-top: 1px solid var(--rule);
}
.k-feed-day:first-child { border-top: 0; padding-top: 8px; }
.k-feed-day-h {
  font-family: var(--font-ui); font-size: 11px; letter-spacing: 0.14em;
  text-transform: uppercase; color: var(--ink-3); padding-top: 6px;
  font-weight: 600;
}
.k-feed-day-h .sub {
  display: block; font-family: var(--font-mono); font-size: 10px;
  color: var(--ink-4); margin-top: 4px; letter-spacing: 0.05em; text-transform: none;
}
.k-feed-list { display: flex; flex-direction: column; gap: 6px; min-width: 0; }
.k-feed-row {
  display: grid; grid-template-columns: 36px 1fr auto; gap: 12px;
  padding: 12px 14px;
  background: var(--surface-1);
  border: 1px solid transparent;
  border-radius: var(--radius-sm);
  align-items: center;
  transition: all 140ms var(--ease);
  cursor: default;
  min-width: 0;
}
.k-feed-row:hover {
  background: var(--surface-2); border-color: var(--rule-2);
  transform: translateX(2px);
}
.k-feed-row .icon {
  width: 36px; height: 36px; border-radius: 50%;
  display: grid; place-items: center;
  font-family: var(--font-mono); font-size: 14px; font-weight: 600;
  background: var(--surface-2); border: 1px solid var(--rule);
}
.k-feed-row .icon.in    { color: var(--moss);   border-color: rgba(123,198,138,0.4); background: rgba(123,198,138,0.08); }
.k-feed-row .icon.out   { color: var(--ink-2);  }
.k-feed-row .icon.invest{ color: var(--brass);  border-color: var(--rule-brass); background: var(--brass-soft); }
.k-feed-row .body { display: flex; flex-direction: column; gap: 3px; min-width: 0; }
.k-feed-row .top { display: flex; align-items: baseline; gap: 10px; min-width: 0; }
.k-feed-row .t {
  font-family: var(--font-ui); font-size: 13px; color: var(--ink);
  font-weight: 500; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
  flex: 0 1 auto; min-width: 0;
}
.k-feed-row .meta {
  font-family: var(--font-ui); font-size: 11px; color: var(--ink-3);
  display: flex; align-items: center; gap: 8px; flex-wrap: wrap;
}
.k-feed-row .meta .dot { width: 3px; height: 3px; background: var(--ink-4); border-radius: 50%; }
.k-feed-row .note {
  font-family: var(--font-serif); font-size: 12px; font-style: italic; color: var(--ink-3);
  margin-top: 4px; line-height: 1.4;
}
.k-feed-row .v {
  font-family: var(--font-mono); font-variant-numeric: tabular-nums;
  font-size: 14px; text-align: right; color: var(--ink); white-space: nowrap;
  font-weight: 500;
}
.k-feed-row .v.pos { color: var(--moss); }
.k-feed-row .v.neg { color: var(--ink); }
.k-feed-row .v.invest { color: var(--brass); }
.k-feed-row .vs {
  font-family: var(--font-mono); font-size: 10px; color: var(--ink-4);
  text-align: right; margin-top: 2px;
}

/* MOOD chip variants */
.k-mood {
  display: inline-flex; align-items: center; padding: 2px 7px;
  font-family: var(--font-ui); font-size: 9.5px; font-weight: 500;
  letter-spacing: 0.06em; border-radius: var(--radius-pill);
  background: var(--surface-2); color: var(--ink-3); border: 1px solid var(--rule);
}
.k-mood.planejado    { color: var(--moss);   border-color: rgba(123,198,138,0.3); }
.k-mood.necessario   { color: var(--sea);    border-color: rgba(127,179,200,0.3); }
.k-mood.prazer       { color: var(--brass);  border-color: var(--rule-brass); }
.k-mood.investimento { color: var(--brass);  border-color: var(--rule-brass); background: var(--brass-soft); }
.k-mood.obrigatorio  { color: var(--ink-3); }
.k-mood.impulso      { color: var(--copper); border-color: rgba(224,136,85,0.4); background: rgba(224,136,85,0.08); }
.k-mood.renda        { color: var(--moss);   border-color: rgba(123,198,138,0.4); background: rgba(123,198,138,0.08); }
.k-mood.social       { color: var(--sea);    border-color: rgba(127,179,200,0.3); }
.k-mood.saude        { color: var(--lantern);border-color: rgba(244,213,141,0.3); }
.k-mood.recorrente   { color: var(--ink-3); }

/* ─────────────────────────────────────────────────────────────
   CARDS (Cartões — wallet)
   ───────────────────────────────────────────────────────────── */
.k-wallet {
  display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 18px;
}
.k-cardobj {
  position: relative; aspect-ratio: 1.586 / 1;
  border-radius: 18px;
  padding: 18px 20px;
  color: var(--ink);
  display: flex; flex-direction: column; justify-content: space-between;
  overflow: hidden;
  box-shadow: 0 12px 32px rgba(0,0,0,0.45), 0 1px 0 rgba(255,255,255,0.08) inset;
  transition: transform 200ms var(--ease), box-shadow 200ms var(--ease);
  cursor: default;
}
.k-cardobj::before {
  content: ''; position: absolute; inset: 0;
  background: radial-gradient(circle at 80% 0%, rgba(255,255,255,0.18), transparent 60%);
  pointer-events: none;
}
.k-cardobj:hover { transform: translateY(-3px); box-shadow: 0 22px 56px rgba(0,0,0,0.55); }
.k-cardobj .bank { font-family: var(--font-ui); font-size: 11px;
  letter-spacing: 0.18em; text-transform: uppercase; font-weight: 600; opacity: 0.85; }
.k-cardobj .brand { font-family: var(--font-ui); font-size: 13px; font-weight: 500; opacity: 0.8; margin-top: 4px; }
.k-cardobj .num { font-family: var(--font-mono); font-size: 17px; letter-spacing: 0.18em;
  margin-top: auto; opacity: 0.95; }
.k-cardobj .row {
  display: flex; justify-content: space-between; align-items: flex-end;
  font-family: var(--font-ui); font-size: 10.5px; font-weight: 500;
  letter-spacing: 0.08em; text-transform: uppercase; opacity: 0.7; margin-top: 10px;
}
.k-cardobj .holder { font-family: var(--font-ui); font-size: 12px; font-weight: 500;
  letter-spacing: 0.06em; }

/* small card chip */
.k-card-chip {
  width: 32px; height: 24px; border-radius: 4px;
  background: linear-gradient(135deg, #C9A05E, #8C6A35);
  position: absolute; top: 20px; right: 70px;
  box-shadow: 0 1px 0 rgba(255,255,255,0.2) inset;
}
.k-card-chip::after {
  content: ''; position: absolute; inset: 4px;
  background:
    linear-gradient(180deg, rgba(0,0,0,0.2) 50%, transparent 50%) 0 0 / 100% 4px,
    linear-gradient(90deg, rgba(0,0,0,0.2) 50%, transparent 50%) 0 0 / 4px 100%;
}

/* ─────────────────────────────────────────────────────────────
   PARCELAS · timeline visual
   ───────────────────────────────────────────────────────────── */
.k-parcela {
  padding: 16px 18px;
  background: var(--surface-1);
  border: 1px solid var(--rule);
  border-radius: var(--radius-sm);
  margin-bottom: 10px;
  transition: all 160ms var(--ease);
}
.k-parcela:hover { background: var(--surface-2); border-color: var(--rule-2); }
.k-parcela-h { display: flex; align-items: baseline; justify-content: space-between; gap: 12px; }
.k-parcela-t { font-family: var(--font-ui); font-size: 14px; color: var(--ink); font-weight: 500; }
.k-parcela-s { font-family: var(--font-ui); font-size: 11px; color: var(--ink-3); }
.k-parcela-bar {
  height: 10px; background: var(--surface-2); border-radius: var(--radius-pill);
  margin-top: 14px; position: relative; overflow: hidden;
  border: 1px solid var(--rule);
}
.k-parcela-fill {
  height: 100%;
  background: linear-gradient(90deg,
    color-mix(in oklab, var(--brass), black 30%),
    var(--brass));
  border-radius: var(--radius-pill);
  position: relative;
  box-shadow: 0 0 12px var(--brass-glow);
}
.k-parcela-fill::after {
  content: ''; position: absolute; right: -1px; top: -2px; bottom: -2px; width: 2px;
  background: var(--brass); box-shadow: 0 0 8px var(--brass);
}
.k-parcela-ticks {
  display: flex; justify-content: space-between; margin-top: 6px;
  font-family: var(--font-mono); font-size: 9.5px; color: var(--ink-4);
}

/* CHAT */
.k-msg { padding: 16px 20px; border-bottom: 1px solid var(--rule); }
.k-msg-h { display: flex; align-items: center; gap: 10px;
  font-family: var(--font-ui); font-size: 11.5px; color: var(--ink-3); margin-bottom: 10px; }
.k-msg-b { font-family: var(--font-sans); font-size: 13px; color: var(--ink-2);
  line-height: 1.6; white-space: pre-wrap; }
.k-msg.user .k-msg-b { color: var(--ink); font-family: var(--font-serif);
  font-size: 17px; line-height: 1.45; font-style: italic; }

/* COMPOSER */
.k-comp {
  padding: 14px 18px; border-top: 1px solid var(--rule);
  background: var(--surface-1);
  display: flex; align-items: center; gap: 10px;
}
.k-comp input {
  flex: 1; border: 0; background: var(--surface-2); color: var(--ink);
  padding: 10px 14px; border-radius: var(--radius-pill);
  font-family: var(--font-ui); font-size: 13px;
  outline: 1px solid var(--rule);
}
.k-comp input::placeholder { color: var(--ink-4); }
.k-comp input:focus { outline: 1px solid var(--brass); background: var(--surface-3); }

/* focus visibility */
button:focus-visible, input:focus-visible {
  outline: 2px solid var(--brass); outline-offset: 2px;
}

/* MOOD-specific tweaks */
body[data-mood="terminal"] .k-card-t { font-family: var(--font-mono); font-weight: 500; }
body[data-mood="terminal"] .k-metric-v { font-family: var(--font-mono); }
body[data-mood="terminal"] .k-top-title::before { content: '› '; color: var(--brass); }
body[data-mood="terminal"] .k-feed-day-h::before { content: '— '; color: var(--brass); }

body[data-mood="editorial"] .k-card-t { font-family: var(--font-serif); font-weight: 600; }
body[data-mood="editorial"] .k-card-hint { font-style: italic; }
body[data-mood="editorial"] .k-feed-row .t { font-family: var(--font-serif); font-size: 14.5px; }

/* hide-on-narrow utility */
@media (max-width: 1280px) {
  .narrow-hide { display: none !important; }
}
`;

(function injectCss() {
  const id = 'klipper-css';
  const existing = document.getElementById(id);
  if (existing) existing.remove();
  const s = document.createElement('style');
  s.id = id; s.textContent = KLIPPER_CSS;
  document.head.appendChild(s);
})();

window.KLIPPER_CSS = KLIPPER_CSS;
