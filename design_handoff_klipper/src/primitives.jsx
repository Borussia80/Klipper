// primitives.jsx — shared low-level components (v2)

const { useState, useMemo, useRef, useEffect } = React;

// ─── LAYOUT ───────────────────────────────────────────────────
function Card({ children, title, hint, action, kicker, padded = true, hover = false, gilt = false, glow = false, elev, style, className = '' }) {
  const cls = ['k-card', hover && 'hover', gilt && 'gilt', glow && 'glow', elev && 'elev-' + elev, className]
    .filter(Boolean).join(' ');
  return (
    <section className={cls} style={style}>
      {(title || kicker || action || hint) && (
        <header className="k-card-h">
          <div>
            {kicker && <div className="k-kicker">{kicker}</div>}
            {title && <div className="k-card-t">{title}</div>}
            {hint && <div className="k-card-hint">{hint}</div>}
          </div>
          {action}
        </header>
      )}
      <div className={padded ? 'k-card-b' : 'k-card-b full'}>{children}</div>
    </section>
  );
}

function Kicker({ children, style }) { return <div className="k-kicker" style={style}>{children}</div>; }
function Mono({ children, style, className = '' }) {
  return <span className={'mono ' + className} style={style}>{children}</span>;
}
function Serif({ children, style, className = '' }) {
  return <span className={'serif ' + className} style={style}>{children}</span>;
}
function SecHeader({ title, sub, action }) {
  return (
    <div className="k-sec-h">
      <div><span className="t">{title}</span>{sub && <span className="s" style={{ marginLeft: 12 }}>{sub}</span>}</div>
      {action}
    </div>
  );
}

// ─── CHARTS ───────────────────────────────────────────────────
function AreaChart({ data, w = 720, h = 200, pad = { t: 8, r: 0, b: 22, l: 0 }, color = 'var(--brass)', fillSoft = 'var(--brass-soft)', mark, gradient = true }) {
  const min = Math.min(...data), max = Math.max(...data);
  const range = max - min || 1;
  const innerW = w - pad.l - pad.r, innerH = h - pad.t - pad.b;
  const xs = (i) => pad.l + (i / (data.length - 1)) * innerW;
  const ys = (v) => pad.t + (1 - (v - min) / range) * innerH;
  const pts = data.map((v, i) => `${xs(i).toFixed(1)},${ys(v).toFixed(1)}`).join(' ');
  const area = `M ${xs(0)},${pad.t + innerH} L ${pts.replace(/ /g, ' L ')} L ${xs(data.length - 1)},${pad.t + innerH} Z`;
  const id = useMemo(() => 'gr' + Math.random().toString(36).slice(2, 8), []);
  return (
    <svg viewBox={`0 0 ${w} ${h}`} preserveAspectRatio="none" style={{ width: '100%', height: h, display: 'block' }}>
      <defs>
        <linearGradient id={id} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor={color} stopOpacity="0.35" />
          <stop offset="100%" stopColor={color} stopOpacity="0" />
        </linearGradient>
      </defs>
      <path d={area} fill={gradient ? `url(#${id})` : fillSoft} />
      <polyline points={pts} fill="none" stroke={color} strokeWidth="1.5" strokeLinejoin="round" strokeLinecap="round" />
      {mark != null && (
        <g>
          <line x1={xs(mark)} x2={xs(mark)} y1={pad.t} y2={pad.t + innerH} stroke={color} strokeWidth="0.5" strokeDasharray="2 3" opacity="0.6" />
          <circle cx={xs(mark)} cy={ys(data[mark])} r="3.5" fill={color} stroke="var(--bg)" strokeWidth="1.5" />
        </g>
      )}
    </svg>
  );
}

function Spark({ data, w = 80, h = 22, color }) {
  const min = Math.min(...data), max = Math.max(...data);
  const r = max - min || 1;
  const pts = data.map((v, i) => `${(i / (data.length - 1)) * w},${h - ((v - min) / r) * h}`).join(' ');
  return (
    <svg viewBox={`0 0 ${w} ${h}`} style={{ width: w, height: h, display: 'block' }}>
      <polyline points={pts} fill="none" stroke={color || 'var(--brass)'} strokeWidth="1.2" />
    </svg>
  );
}

function DonutChart({ data, size = 180, thickness = 14, centerLabel, centerValue }) {
  const total = data.reduce((s, d) => s + d.value, 0);
  const r = (size - thickness) / 2;
  const c = 2 * Math.PI * r;
  let offset = 0;
  return (
    <svg viewBox={`0 0 ${size} ${size}`} style={{ width: size, height: size }}>
      <circle cx={size/2} cy={size/2} r={r} fill="none" stroke="var(--rule)" strokeWidth={thickness} />
      {data.map((d, i) => {
        const len = (d.value / total) * c;
        const el = (
          <circle key={i} cx={size/2} cy={size/2} r={r} fill="none"
            stroke={`var(--${d.color})`} strokeWidth={thickness}
            strokeDasharray={`${len} ${c - len}`}
            strokeDashoffset={-offset}
            strokeLinecap="butt"
            transform={`rotate(-90 ${size/2} ${size/2})`} />
        );
        offset += len;
        return el;
      })}
      {centerValue && (
        <g>
          <text x={size/2} y={size/2 - 4} textAnchor="middle"
            fontFamily="var(--font-serif)" fontSize="22" fill="var(--ink)"
            style={{ fontVariantNumeric: 'tabular-nums' }}>{centerValue}</text>
          <text x={size/2} y={size/2 + 14} textAnchor="middle"
            fontFamily="var(--font-ui)" fontSize="9" fill="var(--ink-3)"
            letterSpacing="0.14em" style={{ textTransform: 'uppercase' }}>{centerLabel}</text>
        </g>
      )}
    </svg>
  );
}

// Stacked horizontal bar (for cash flow split)
function FlowBar({ segments, h = 14 }) {
  const total = segments.reduce((s, x) => s + x.v, 0);
  return (
    <div style={{ display: 'flex', height: h, borderRadius: 999, overflow: 'hidden',
      background: 'var(--surface-2)', border: '1px solid var(--rule)' }}>
      {segments.map((s, i) => (
        <div key={i} title={`${s.label}: ${(s.v/total*100).toFixed(0)}%`} style={{
          width: (s.v / total * 100) + '%', background: s.color, transition: 'width 240ms ease',
        }} />
      ))}
    </div>
  );
}

// Fragility gauge — 270° arc
function FragilityGauge({ value, size = 110 }) {
  const r = (size - 14) / 2;
  const c = 2 * Math.PI * r;
  const arcLen = (270 / 360) * c;
  const fill = (value * 270 / 360) * c;
  const tone = value < 0.4 ? 'var(--moss)' : value < 0.65 ? 'var(--lantern)' : 'var(--rust)';
  return (
    <div style={{ position: 'relative', width: size, height: size }}>
      <svg viewBox={`0 0 ${size} ${size}`} style={{ width: size, height: size, transform: 'rotate(135deg)' }}>
        <circle cx={size/2} cy={size/2} r={r} fill="none" stroke="var(--rule)" strokeWidth="6"
          strokeDasharray={`${arcLen} ${c}`} />
        <circle cx={size/2} cy={size/2} r={r} fill="none" stroke={tone} strokeWidth="6"
          strokeDasharray={`${fill} ${c}`} strokeLinecap="round" />
      </svg>
      <div style={{ position: 'absolute', inset: 0, display: 'flex', flexDirection: 'column',
        alignItems: 'center', justifyContent: 'center' }}>
        <span style={{ fontFamily: 'var(--font-serif)', fontSize: 28, lineHeight: 1, color: tone,
          fontVariantNumeric: 'tabular-nums' }}>{value.toFixed(2)}</span>
        <span style={{ fontFamily: 'var(--font-ui)', fontSize: 9, color: 'var(--ink-3)',
          letterSpacing: '0.16em', textTransform: 'uppercase', marginTop: 4, fontWeight: 600 }}>Fragility</span>
      </div>
    </div>
  );
}

// Generic small bar
function BarTrack({ value, max, color = 'var(--brass)', h = 4 }) {
  const w = Math.min(100, (value / max) * 100);
  return (
    <div style={{ height: h, background: 'var(--surface-2)', borderRadius: h/2, overflow: 'hidden',
      border: '1px solid var(--rule)' }}>
      <div style={{ width: w + '%', height: '100%', background: color, transition: 'width 240ms ease',
        boxShadow: `0 0 8px ${color}` }} />
    </div>
  );
}

// Mood chip
function Mood({ k }) {
  if (!k) return null;
  const noaccent = k.replace('ó', 'o').replace('í', 'i').replace('ú', 'u').replace('é', 'e').replace('á', 'a');
  return <span className={'k-mood ' + noaccent}>{k}</span>;
}

// IconBadge — circular accent
function IconBadge({ glyph, tone = 'brass', size = 36 }) {
  const colorMap = {
    brass: 'var(--brass)', moss: 'var(--moss)', rust: 'var(--rust)',
    lantern: 'var(--lantern)', sea: 'var(--sea)',
  };
  const c = colorMap[tone] || tone;
  return (
    <div style={{
      width: size, height: size, borderRadius: '50%',
      display: 'grid', placeItems: 'center',
      background: `color-mix(in oklab, ${c}, transparent 88%)`,
      color: c,
      border: `1px solid color-mix(in oklab, ${c}, transparent 60%)`,
      fontFamily: 'var(--font-mono)', fontSize: size * 0.4, fontWeight: 600,
      flexShrink: 0,
    }}>{glyph}</div>
  );
}

Object.assign(window, {
  Card, Kicker, Mono, Serif, SecHeader,
  AreaChart, Spark, DonutChart, FlowBar, FragilityGauge, BarTrack,
  Mood, IconBadge,
});
