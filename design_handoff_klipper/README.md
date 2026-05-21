# Handoff: Klipper — Wealth Operating System

> Personal finance app for Roberto Milet. The Klipper name references clipper ships (organization + speed) and paperclips (order). The design positions Klipper as a **wealth OS** — not a bank, not a fintech — sitting on top of the WikiAgent v2.0 engine architecture (M1 Quant / M2 Governance / M3 Context / M4 AI Consilium / Anti-BS / Fragility).

---

## About the Design Files

The HTML files bundled here are **design references**, not production code. They were authored as a React-in-Babel prototype in a single self-contained directory for quick iteration. Everything renders in the browser from `Klipper.html` by loading raw `.jsx` files through `@babel/standalone`.

The job is to **recreate this design in Klipper's real codebase**, which today is:

- Python · Streamlit (`streamlit run app.py`)
- Supabase PostgreSQL (`migrations/001_initial_schema.sql`)
- LiteLLM multi-provider for M4 Consilium
- pages/1_Dashboard … pages/5_AI_Consilium

**Two viable paths:**

1. **Stay on Streamlit** — port these screens to Streamlit pages using `st.markdown` + custom HTML/CSS injected via `unsafe_allow_html=True`. The wallet cards, parcelas timeline, and feed will require a lot of custom HTML. The AI Consilium 2×2 grid is feasible with `st.columns`. **This is the path of least disruption** but will not match the prototype's depth/animations 1:1.

2. **Replace Streamlit with Next.js + FastAPI** (recommended for the long term) — Next.js 15 App Router + Tailwind for the UI, FastAPI as a thin Python layer that keeps the WikiAgent engines + Supabase + LiteLLM. The prototype components map almost directly to Next.js + Tailwind. This is the right choice if Klipper is to become the wealth OS described in the prototype.

Either path: **the WikiAgent engines (M1/M2/M3/AB/FR) and Supabase schema are unchanged.** Only the presentation layer is being rebuilt.

---

## Fidelity

**High-fidelity (hi-fi).** The mocks specify exact colors, typography, spacing, radii, shadows, and ambient-light treatments. Recreate them pixel-precisely with the codebase's chosen framework.

---

## Screens / Views

The prototype has **10 pages** grouped into three sidebar sections: **Fluxo** (daily money flow — the center), **Capital** (wealth + thesis management — secondary), **Mente** (AI + capture + brand).

### Sidebar (persistent)

- **Width**: 248px, sticky, full viewport height
- **Background**: linear-gradient(180deg, `color-mix(in oklab, var(--bg) 96%, white 4%)`, `var(--bg-2)`)
- **Border-right**: 1px solid `var(--rule)`
- **Sections**:
  - **Brand block** (top): 22px K mark in a 38×38 brass-tinted rounded-square badge + wordmark "Klipper" in General Sans 22px/600/-0.025em + tagline "Wealth · operating system" in 10px/600/0.18em-tracked uppercase
  - **Live snapshot card**: clickable button → Patrimônio. Shows compact patrimônio value, 30d delta, cash%, position count
  - **Nav** (grouped Fluxo/Capital/Mente, 9 items): icon glyph + label + optional count badge
  - **Engines panel** (WikiAgent · M·): 5 rows (M1 Quant / M2 Governance / M3 Context / AB Anti-BS / FR Fragility) each with a 2-char id badge + name + pulsing dot indicator (green = ok, red = breach)
  - **Agenda preview**: next event from the AGENDA array
  - **Footer**: 30px circular avatar (RM monogram) + name + scenario meta + settings cog

### 1. Home (`/`)

The **center of the system**. Daily money flow, behavior, narrative — patrimônio is intentionally a glance, not the lead.

**Layout**: 3-column hero strip (1.4fr / 1fr / 1fr), then 2-column main (1.7fr / 1fr).

**Hero strip:**
- **"O dia em dinheiro · terça, 21 mai"** card (gilt + ambient glow): kicker + today's net in Instrument Serif 38px + entrou/saiu/investido FlowStat row (icon circle + uppercase label + Geist Mono value) + italic Anti-BS narrative quote in Instrument Serif 14px + "↳ narrativa Anti-BS · gerada às 16:20" timestamp
- **"Maio · até hoje"** card: 2-col metric grid (Entradas / Saídas) + FlowBar (stacked horizontal bar with mood-colored segments)
- **"Comportamento · streak"** card: 56px circular progress ring (brass, 14/30 days saved) + 2-col MiniStat row at bottom

**Main grid:**
- **"Feed financeiro"** Card (left, padded=false): full transaction timeline grouped by day (`hoje`, `ontem`, `19/05`...). Each day row has 88px sticky day label + list of FeedRow items
- **Side rail** (right): "Insights" (gilt), "Agenda" (5 events), "Patrimônio glance" (compact metric + sparkline + 4 allocation chips)

**FeedRow component** (transactions in feed):
- 36×36 circular icon (mood-tinted): in=moss, invest=brass, out=neutral
- Body: ticker/description in General Sans 13/500 + meta line (time · category · `<Mood>` chip · card brand) + optional Instrument Serif italic narrative note ("'visita do Lucas no fim de semana'")
- Right: Geist Mono value 14px (color depends on type), optional auto badge

### 2. Movimento (`/transactions`)

Full ledger with filters and behavioral analytics.

**Layout**: 4-col summary strip → tabs filter + mood-chip filter row → 2-col main (1.7fr / 1fr).

**Filter system**:
- **Tabs** (pill group, `.k-tabs`): Tudo / Entradas / Saídas / Investimento / Recorrentes
- **Mood chips** (clickable, opacity toggle on selection): all 8 moods + counts

**Main grid:**
- **Ledger** card: filtered feed (same FeedRow component as Home)
- **"Por categoria"** card: top 7 categories ranked, label + Geist Mono total + thin brass BarTrack (4px height)
- **"Por mood"** card: month-vs-prev comparison. Each mood row has chip + delta percentage + proportional BarTrack (turns copper if up >20%)

### 3. Cartões (`/cards`)

**Apple Wallet / Amex / Nubank Ultravioleta** vibe. Ultra-fast tactile card switcher.

**Layout**: 4-col summary strip → "Carteira" SecHeader → wallet grid (auto-fit minmax(280px, 1fr)) → "Selected detail" SecHeader → 2-col detail (320px / 1fr).

**Card object** (`.k-cardobj`):
- aspect-ratio 1.586/1 (real credit-card proportion)
- 18px border-radius
- 18×20 padding
- per-card background gradient (Itaú=black, Amex=silver, Nu=ultravioleta gradient, Inter=orange)
- top-right shimmer overlay: radial-gradient at 80% 0%, white 18% → transparent 60%
- selected state: 1px brass border + brass glow + translateY(-3px)
- chip element (`.k-card-chip`): 32×24 brass-gradient rect with embossed grid pattern, abs-positioned top:56 left:22
- bank name (uppercase 11px/600/0.18em), brand name (13px/500), masked card number (`•••• •••• •••• 1234` Geist Mono 17px/0.18em), holder (`ROBERTO MILET`), vence date

**4 cards in CARDS array** (see data section).

**Selected detail**:
- Left column: "Próxima fatura" card (Instrument Serif 30px value + closing/due dates + BarTrack progress) + "Saúde do uso" card (4-row label/value list)
- Right column: "Lançamentos · 30d" card with FeedRow list filtered by `tx.card === activeId`

### 4. Parcelas (`/parcelas`)

Timeline-visual installment tracking.

**Layout**: 4-col summary → "Compromissos parcelados" header → ParcelaRow stack → "Horizonte de pagamentos" → 12-month bar chart.

**ParcelaRow** (per installment plan):
- Header: 36px IconBadge (tag-derived glyph) + title (General Sans 14/500) + store/dates/tag + Instrument Serif 18px monthly value with `/mês` suffix + "X/N pagas · faltam Y" Mono
- **Per-installment dot timeline**: `grid-template-columns: repeat(N, 1fr)` with 8px-tall rounded rects — paid=brass, unpaid=surface-2, current-position=brass + glow
- Footer: 3-col Geist Mono row (total contratado / já pago / restante)

**HorizonChart**: 12 month columns. Bars in brass for current month (with glow), grey for future. Labels above (value) and below (month name).

### 5. Patrimônio (`/patrimonio`) — the old "Dashboard"

The wealth-management surface. Patrimônio hero, allocation, governance, theses.

**Layout**: 4-col hero (1.8fr / 1fr / 1fr / 1fr) → 2-col middle (allocation + governance) → theses table.

**Hero**:
- **Patrimônio** card (gilt): Instrument Serif 40px patrimônio + 30d/12m delta + 180-day AreaChart with brass gradient fill + mark dot at last value + month tick labels
- **Caixa & liquidez** card: percentage in Instrument Serif 28px + R$ value + "limite M2 ≥ 20%" + colored BarTrack
- **Fragility** card: 96px FragilityGauge (270° arc, color shifts moss→lantern→rust on value) + label
- **Anti-BS** card: score 30px (color-keyed) + flags + alert pill if flags > 0

**Allocation card**: 160px DonutChart with `R$ 1,85 M / patrimônio` center label + 6-row legend.

**Governance card**: 3 GovRow entries (Max ativo / Max tese / Caixa mínimo) with check/cross + value/limit + colored progress bar + status copy at bottom.

**Theses table**: tese / status chip / Conviction (5-dot bar) / Alocação / Perf 12m / RiskBar / Âncora (italic Instrument Serif).

### 6. Posições (`/positions`)

Live market-mark table.

4-col summary (Valor de mercado / P&L total / Var dia / Beta vs IBOV) → 9-column positions table (Ativo · Classe · Qtd · Preço · Custo · Valor · P&L · Var dia).

### 7. Teses (`/theses`)

Master/detail: 320px tese list (clickable cards, selected glows brass) + 1fr detail card (4-metric strip → âncora quant + contexto macro).

### 8. AI Consilium (`/consilium`)

Multi-provider chat. **Panel view** (default) shows 2×2 grid of responses side-by-side. **Conversation view** is the linear thread.

**Layout**:
- Header: kicker + Instrument Serif title + cost meta + tabs (Painel / Conversa)
- Provider chooser strip: 5 ProviderPills (Claude / Gemini / GPT-4o / Qwen / Kimi) — toggleable, active=glyph-colored border + tinted bg
- Main: 1fr / 360px grid. Chat region (Card with composer at bottom) + context rail (3 cards: Contexto enviado as chips, Regras do Agente list, Custo & uso table)

**PanelView**:
- User message at top (italic Instrument Serif 17px)
- Below: grid `repeat(min(2, N), 1fr)` of provider responses
- Each response: avatar glyph + provider name + cost/tokens + General Sans 12.5/1.6 body + "★ marcar" / "↳ aprofundar" actions

### 9. Captura (`/mobile`)

Telegram bot mockup. 1fr / 380px grid.

**Left**: centered 340×700 phone frame (radius 42 outer, 34 inner, top notch, brass-tinted shadow). Inside: status bar + Telegram-style header (Klipper Bot avatar + online status) + message bubbles (user=brass-tinted right-aligned, bot=neutral left-aligned) + composer.

Demonstrated flow: user types "gastei 86,40 ifood" → bot logs and replies with M2 context; user types "comprei 200 wege3 a 41,30" → bot does M2 check, shows confirm button; user types "/? vale aumentar fii logística agora?" → bot routes to Consilium and replies with 3-model summary.

**Right**: explanation cards (Comandos suportados list, Stack list with deploy status).

### 10. Marca (`/brand`)

Brand system showcase. Hero with mark + wordmark, construction notes, mark variants grid, scale row 16→96px, wordmark scale, lockup horizontal, palette grid (12 swatches with tokens + hex), 3-font type stack ("Aa" specimens), voice (diz/não diz).

---

## Design Tokens

### Typography

```
--font-sans / --font-ui : 'General Sans', 'Inter', ui-sans-serif, system-ui, sans-serif
--font-serif            : 'Instrument Serif', 'Spectral', Georgia, serif
--font-mono             : 'Geist Mono', 'IBM Plex Mono', ui-monospace, Menlo, monospace
```

**Sources** (all free, web-loadable):
- General Sans → Fontshare: `https://api.fontshare.com/v2/css?f[]=general-sans@200,300,400,500,600,700&display=swap`
- Instrument Serif → Google Fonts (regular + italic)
- Geist Mono → Google Fonts (400, 500, 600)

**Usage rules**:
- General Sans Semibold (-2.5% tracking) for wordmark and UI titles
- General Sans Medium/Regular for body, labels, table cells, buttons
- Instrument Serif for hero numbers (patrimônio), card titles, italic narrative quotes
- Geist Mono for every number, ticker, timestamp, percentage delta, currency value

**Type scale** (used in prototype):

| Use | Family | Size | Weight | Tracking |
|---|---|---|---|---|
| Wordmark XL | General Sans | 56–72px | 600 | -0.025em |
| Patrimônio hero | Instrument Serif | 38–40px | 400 | -0.02em |
| Page title (topbar) | Instrument Serif | 22px | 500 | -0.01em |
| Card title | Instrument Serif | 16px | 500 | -0.005em |
| Metric value | Instrument Serif | 26–30px | 400 | -0.015em |
| Kicker (uppercase) | General Sans | 9.5px | 600 | 0.16em |
| Body | General Sans | 12.5–13.5px | 400/500 | 0 |
| Mono data | Geist Mono | 10–14px | 400/500 | tabular-nums |

### Color tokens (nautical palette)

```
/* canvas */
--bg          : #08161F   /* deep open-sea */
--bg-2        : #0C1E2B   /* ambient ink */

/* surfaces (glass) */
--surface-1   : rgba(255,255,255,0.025)
--surface-2   : rgba(255,255,255,0.045)
--surface-3   : rgba(255,255,255,0.07)
--surface-tint: rgba(200,163,100,0.04)

/* ink */
--ink         : #F2EAD3   /* parchment */
--ink-2       : #C9BC9E
--ink-3       : #8F8770
--ink-4       : #5C5746

/* rules */
--rule        : rgba(255,255,255,0.06)
--rule-2      : rgba(255,255,255,0.10)
--rule-brass  : rgba(200,163,100,0.22)

/* brand */
--brass       : #D9B26F   /* primary accent */
--brass-soft  : rgba(217,178,111,0.18)
--brass-glow  : rgba(217,178,111,0.35)
--sea         : #7FB3C8   /* secondary */
--copper      : #E08855   /* alert */
--moss        : #7BC68A   /* positive */
--rust        : #D87C6A   /* negative */
--lantern     : #F4D58D   /* warn */

/* semantic */
--pos         : var(--moss)
--neg         : var(--rust)
--warn        : var(--lantern)
--accent      : var(--brass)
--cash        : var(--brass)
```

### Depth / shadow tokens

```
--shadow-1    : 0 1px 0 rgba(255,255,255,0.04) inset, 0 6px 18px rgba(0,0,0,0.35)
--shadow-2    : 0 1px 0 rgba(255,255,255,0.05) inset, 0 12px 32px rgba(0,0,0,0.42)
--shadow-3    : 0 1px 0 rgba(255,255,255,0.06) inset, 0 24px 60px rgba(0,0,0,0.5)
--glow-brass  : 0 0 0 1px rgba(217,178,111,0.15), 0 0 32px rgba(217,178,111,0.10)
```

### Radius scale

```
--radius-xs   : 6px
--radius-sm   : 10px
--radius      : 16px     /* default cards */
--radius-lg   : 20px
--radius-xl   : 28px
--radius-pill : 999px
```

### Ambient light (body::before)

```css
body::before {
  position: fixed; inset: 0; z-index: 0; pointer-events: none;
  background:
    radial-gradient(circle at 18% -10%, rgba(217,178,111,0.07), transparent 45%),
    radial-gradient(circle at 90% 110%, rgba(127,179,200,0.06), transparent 55%);
  opacity: 0.9;
}
```

### Glass surface recipe (every card)

```css
background: var(--surface-2);
border: 1px solid var(--rule);
border-radius: var(--radius);
box-shadow: var(--shadow-1);
backdrop-filter: blur(8px) saturate(140%);
-webkit-backdrop-filter: blur(8px) saturate(140%);
```

### Animation tokens

```
--ease  : cubic-bezier(0.2, 0.7, 0.2, 1)
```
- Card hover: `transform: translateY(-2px); box-shadow: var(--shadow-2);` in 180ms
- Button active: `transform: scale(0.97);` in 140ms
- Feed row hover: `transform: translateX(2px); background: var(--surface-2)` in 140ms
- Engine pulse: 2s ease-out infinite expanding ring

---

## Mood System

The user can toggle a **mood lens** via the Tweaks panel: `default` / `terminal` / `editorial`. Each is a thin overlay on top of the nautical base — only typography and a few palette tweaks change.

- **default** (Bordo): General Sans + Instrument Serif + Geist Mono. The shipping look.
- **terminal** (Quant · análise · foco): Geist Mono everywhere (including UI). Brass swaps to a quant-green `#39E0B0`. Background darkens slightly. Radius shrinks (8/10px).
- **editorial** (Review · journaling · reflexão): Body switches to Instrument Serif. UI stays sans. Background warms slightly. Radius grows (20/28px).

If you're shipping a v1, ship `default` only. Mood is an aspirational system, not a requirement.

---

## Scenarios

The prototype ships 3 scenarios that toggle the data: `otimista` / `realista` / `estressado`. In production this becomes real Supabase data — scenarios were a prototype affordance for showing how the UI handles different states (e.g., M2 violations rendering as red ✕ rows, fragility gauge turning rust at 0.82, anti-BS flags appearing).

**Important**: the visual logic for `status === 'over-limit' / 'breach'`, `governance.ok === false`, `antiBs.flags > 0`, and `fragility > 0.65` must be preserved when wiring real data.

---

## Brand Mark (Logo)

The official Klipper mark is a **K monogram** — solid dark stem + short upper arm + an extended diagonal **blue blade** for the lower arm. The blue blade evokes the proa of a clipper (direction, decision) without being literal. It ships as a set of PNG assets (see `brand/`).

### Assets (in `brand/`)

| File | Size | Use |
|---|---|---|
| `klipper-icon-dark.png`     | 195×195 | App icon / sidebar mark on dark surfaces. Dark navy rounded square + white K + blue blade. **Default.** |
| `klipper-icon-light.png`    | 195×195 | App icon on light surfaces. White rounded square + dark K + blue blade. |
| `klipper-icon-gradient.png` | 195×195 | App icon on blue gradient. |
| `klipper-icon-black.png`    | 195×195 | App icon on pure black. |
| `klipper-mark.png`          | 260×280 | Just the mark, no badge (over photography, dark mode lockups). |
| `klipper-lockup-light.png`  | 900×280 | Full lockup on light background. |
| `klipper-lockup-dark.png`   | 625×300 | Full lockup on dark navy background. |
| `klipper-lockup-gradient.png` | 629×300 | Full lockup on blue gradient. |

The rounded-square icons have **transparent corners** (clipped to the rounded-square boundary), so dropping them on any background renders correctly without a white halo.

### Wordmark

`Klipper` in **General Sans Semibold**, letter-spacing `-0.025em`. Spacing mark→wordmark = ½ × mark height. Align mark to the wordmark's cap height. Do not redraw the wordmark — pair it with the type system below.

---

## Data Shape

See `src/data.jsx` for the full mock data. Key shapes you need to replicate from Supabase:

```ts
type Transaction = {
  d: string;        // "hoje" | "ontem" | "19/05" — display label
  time: string;     // "14:32"
  t: string;        // description
  k: 'in' | 'out' | 'invest' | 'parcela' | 'recorrente';
  v: number;        // signed amount in BRL
  cat?: string;     // 'alimentação' | 'transporte' | 'saúde' | ...
  mood?: 'planejado' | 'necessário' | 'prazer' | 'investimento'
       | 'obrigatório' | 'impulso' | 'renda' | 'social' | 'saúde' | 'recorrente';
  card?: string;    // FK → Card.id
  auto?: boolean;
  note?: string;    // narrative — used in the italic quote slot
};

type Card = {
  id: string; bank: string; brand: string; label: string;
  last4: string;
  color: string;    // CSS gradient
  accent: string; ink?: string;
  limit: number; used: number;
  closing: string; due: string;
  next: number;     // next invoice amount
};

type Parcela = {
  id: string; title: string; store: string;
  total: number; n: number; paid: number; monthly: number;
  card: string;     // FK → Card.id
  start: string; end: string; tag: string;
};

type Thesis = {
  id: string; name: string;
  alloc: number;    // 0..1 — % of patrimônio
  conviction: 1 | 2 | 3 | 4 | 5;
  perf12m: number;  // percentage
  status: 'on-track' | 'watch' | 'over-limit' | 'breach';
  anchor: string;   // M1 quant rationale, free text
  risk: number;     // 0..1 — vol normalizada
};

type Provider = 'claude' | 'gemini' | 'openai' | 'qwen' | 'kimi';
type ConsiliumMessage =
  | { role: 'user'; when: string; text: string }
  | { role: 'assistant'; provider: Provider; when: string;
      cost: number; tokens: number; text: string };

type AgendaItem = {
  d: string;        // "amanhã" | "24/05"
  when: string;     // "24/05"
  title: string;
  v: number;
  tag: string;
  tone: 'pos' | 'neg' | 'warn' | 'info';
};
```

The prototype computes monthly aggregates and behavior comparisons (`BEHAVIOR.thisMonth` vs `BEHAVIOR.lastMonth`) at build time from the TX array. In production, these should be computed by Supabase views or RPC calls.

---

## WikiAgent Engines — Mapping to UI

| Engine | Where it surfaces | What it computes |
|---|---|---|
| **M1 Quant** | Fragility gauge · risk bars on theses · "âncora quant" copy | Volatility, drawdown, correlations, Sharpe, beta |
| **M2 Governance** | "Governance" card with 3 GovRows · status chips on theses · M2 badge in Telegram bot replies · sidebar engine pulse | Max-asset 10%, max-thesis 25%, min-cash 20% — beginner mode |
| **M3 Context** | "Contexto macro" panel in Tese detail · "Contexto enviado" chips in Consilium · sentiment score | Selic, IBOV, sentiment, macro layers fed to LLMs |
| **Anti-BS** | Score badge in Patrimônio hero · "narrativa Anti-BS" quote on Home · Anti-BS Check audit history | Narrative-vs-evidence delta. Flags fire when conviction doesn't match evidence trail |
| **Fragility** | The 270° gauge dial · sidebar status pulse | Composite 0..1 — portfolio resilience to shocks |

The prototype renders these as **visual outputs** — the real engines in `core/` already compute the underlying numbers.

---

## Routing

Single-page React app in the prototype. In production:

```
/                 → Home
/movimento        → Transactions
/cartoes          → Cards
/parcelas         → Parcelas
/patrimonio       → Patrimonio (old dashboard)
/posicoes         → Positions
/teses            → Theses
/consilium        → AI Consilium
/captura          → Mobile / Telegram setup
/marca            → Brand (probably internal-only)
```

Sidebar `active` state should match the route. The "live snapshot" card in the sidebar is a button that navigates to `/patrimonio`.

---

## Interactions & Behavior

- **All cards with `hover` modifier**: lift 2px + deeper shadow + brighter border. Use the cubic ease.
- **Buttons**: scale(0.97) on active.
- **Feed rows**: translateX(2px) on hover. Cursor stays default.
- **Tabs**: pill background slides in via `box-shadow` change (no layout shift).
- **Provider pills in Consilium**: toggle active state controls which messages render in PanelView/ConversationView.
- **Wallet cards**: clicking sets `active`; the active card lifts + brass glow border.
- **Mood chips in Movimento**: clicking sets a single-mood filter; clicking again toggles off. "tudo" chip clears.
- **Tweaks panel** (bottom-right, toggled by the host toolbar): mood / scenario / showEngines. Should not ship to production — replace with real preferences.

---

## Files in This Handoff

```
design_handoff_klipper/
├── README.md                    ← this file
├── Klipper.html                 ← entry point — load this to see the design
├── tweaks-panel.jsx             ← in-design control panel (do not ship)
└── src/
    ├── themes.jsx               ← NAUTICAL_BASE + MOODS + applyMood()
    ├── styles.jsx               ← all CSS injected at runtime (~26 KB)
    ├── data.jsx                 ← TX, CARDS, PARCELAS, BEHAVIOR, AGENDA, SCENARIOS, CONSILIUM_THREAD, PROVIDERS
    ├── primitives.jsx           ← Card, Kicker, Mono, Serif, AreaChart, Spark, DonutChart, FlowBar, FragilityGauge, BarTrack, Mood, IconBadge
    ├── shell.jsx                ← Sidebar, TopBar, BrandMark, NAV
    ├── page_home.jsx            ← Home (the center)
    ├── page_transactions.jsx    ← Movimento (full ledger + filters)
    ├── page_cards.jsx           ← Cartões (wallet)
    ├── page_parcelas.jsx        ← Parcelas (timeline)
    ├── page_capital.jsx         ← Patrimônio + Posições + Teses (3 pages in one file)
    ├── page_consilium.jsx       ← AI Consilium
    ├── page_mobile.jsx          ← Captura (Telegram bot mockup)
    ├── page_brand.jsx           ← Marca (brand system showcase)
    └── app.jsx                  ← root + routing + Tweaks
```

**To run the prototype locally**: serve the folder over HTTP (e.g., `python -m http.server 8000`) and open `Klipper.html`. Babel transpiles JSX in-browser. There is no build step.

---

## Suggested Implementation Order (Next.js path)

1. **Tokens + globals**: port `themes.jsx` vars + `styles.jsx` rules into `app/globals.css` + a tailwind config. Set up the 3 font sources via `next/font`.
2. **Primitives**: Card, Kicker, Mono, Serif, AreaChart, DonutChart, FragilityGauge, BarTrack, Mood, IconBadge → `components/ui/`.
3. **Shell**: Sidebar + TopBar + BrandMark → `components/shell/`. App layout in `app/layout.tsx`.
4. **Pages in order of value**: Home → Movimento → Patrimônio → Cartões → Parcelas → Consilium → Posições → Teses → Captura → Marca.
5. **Wire data**: replace `SCENARIOS[scenario]` reads with Supabase queries via tRPC/Server Components. TX feed should paginate.
6. **Wire engines**: M1/M2/M3/AB/FR currently produce literal strings ("Fragility 0.34", "+11.2%") — wire to the real `core/` engines via a thin Python FastAPI passthrough.
7. **Mood toggle**: ship `default` only. Add `terminal` / `editorial` later if users ask.

---

## Notes on Brand Use

- The K mark SVG is canonical — use the source above, do not redraw.
- The wordmark is set in **General Sans Semibold** with `-0.025em` letter-spacing. Do not substitute Inter for it without checking — the visual weight differs.
- Brass `#D9B26F` is the **single primary accent**. Sea / Moss / Rust / Lantern / Copper are semantic only — they should never be used decoratively.
- Do not introduce gradients beyond the brand-mark blade gradient (`#F4D58D → #C8A05E`), the brass primary-button gradient, and the per-card gradients in `CARDS`.

---

## Questions for the Developer

- Are you shipping on Streamlit or replacing it with Next.js?
- Is the Telegram bot (Fase 6) in scope for this implementation pass, or rendered as marketing/setup-only?
- Do you want mood lenses in v1 or v1.1?
- Authentication: Supabase Auth or assume single-user (Roberto) for now?

The HTML files in this folder are the source of truth for visual treatment. Where this README and the HTML disagree, **the HTML wins** — re-read the source.
