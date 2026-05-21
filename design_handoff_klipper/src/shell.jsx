// shell.jsx — sidebar + topbar with live indicators

const NAV = [
  { id: 'home',         label: 'Home',         mark: '◉', section: 'fluxo' },
  { id: 'transactions', label: 'Movimento',    mark: '↹', section: 'fluxo' },
  { id: 'cards',        label: 'Cartões',      mark: '▤', section: 'fluxo' },
  { id: 'parcelas',     label: 'Parcelas',     mark: '⌗', section: 'fluxo' },
  { id: 'patrimonio',   label: 'Patrimônio',   mark: '◐', section: 'capital' },
  { id: 'positions',    label: 'Posições',     mark: '◧', section: 'capital' },
  { id: 'theses',       label: 'Teses',        mark: '◇', section: 'capital' },
  { id: 'consilium',    label: 'Consilium',    mark: '◈', section: 'mente' },
  { id: 'mobile',       label: 'Captura',      mark: '✎', section: 'mente' },
  { id: 'brand',        label: 'Marca',        mark: 'K', section: 'mente' },
];

function BrandMark({ size = 36, variant = 'dark' }) {
  // variants: 'dark' (default — dark navy badge w/ white K + blue blade)
  //         | 'light' (white badge w/ dark K)
  //         | 'gradient' (blue gradient badge)
  //         | 'black' (near-black badge)
  //         | 'mark' (just the K, no badge, for over-image)
  const src = variant === 'mark'    ? 'brand/klipper-mark.png'
            : variant === 'light'   ? 'brand/klipper-icon-light.png'
            : variant === 'gradient'? 'brand/klipper-icon-gradient.png'
            : variant === 'black'   ? 'brand/klipper-icon-black.png'
            : 'brand/klipper-icon-dark.png';
  return (
    <img src={src} width={size} height={size} alt="Klipper"
      style={{ display: 'block', borderRadius: Math.round(size * 0.22) }} />
  );
}

function Sidebar({ page, setPage, snapshot, governance, showEngines, scenario, agenda }) {
  // build live indicators
  const nextEvent = agenda[0];
  const violations = [
    governance.maxAsset.ok ? 0 : 1,
    governance.maxThesis.ok ? 0 : 1,
    governance.minCash.ok ? 0 : 1,
  ].reduce((a, b) => a + b, 0);

  // group nav by section
  const sections = [
    { key: 'fluxo',   label: 'Fluxo' },
    { key: 'capital', label: 'Capital' },
    { key: 'mente',   label: 'Mente' },
  ];

  return (
    <aside className="k-side">
      <div className="k-side-h">
        <div className="k-brand">
          <BrandMark size={36} variant="dark" />
          <span>Klipper</span>
        </div>
        <div className="k-tagline">Wealth · operating system</div>
      </div>

      {/* live snapshot */}
      <button className="k-side-snap" style={{ textAlign: 'left', cursor: 'pointer' }}
        onClick={() => setPage('patrimonio')}>
        <div className="lbl">Patrimônio · {scenario}</div>
        <div className="v">{brl(snapshot.total, { compact: true })}</div>
        <div className="d">
          <span className={snapshot.delta30d >= 0 ? 'pos' : 'neg'}>
            {brl(snapshot.delta30d, { compact: true, sign: true })} · {pct(snapshot.delta30dPct)}
          </span>
          <span style={{ color: 'var(--ink-4)', marginLeft: 6 }}>30d</span>
        </div>
        <div style={{ display: 'flex', gap: 6, marginTop: 4, alignItems: 'center', fontSize: 10,
          color: 'var(--ink-3)', fontFamily: 'var(--font-ui)' }}>
          <span style={{ width: 4, height: 4, borderRadius: '50%', background: 'var(--moss)' }} />
          <span>caixa <Mono>{(snapshot.cash * 100).toFixed(0)}%</Mono></span>
          <span style={{ width: 4, height: 4, borderRadius: '50%', background: 'var(--brass)', marginLeft: 6 }} />
          <span>{snapshot.positions.length || 9} posições</span>
        </div>
      </button>

      <nav className="k-nav">
        {sections.map(s => (
          <React.Fragment key={s.key}>
            <div className="k-nav-section">{s.label}</div>
            {NAV.filter(n => n.section === s.key).map(n => {
              let tag = null;
              if (n.id === 'parcelas') tag = <span className="k-nav-tag">5</span>;
              if (n.id === 'cards') tag = <span className="k-nav-tag warn">4d</span>;
              if (n.id === 'theses' && violations > 0) tag = <span className="k-nav-tag neg">{violations}</span>;
              if (n.id === 'consilium') tag = <span className="k-nav-tag">4</span>;
              return (
                <button key={n.id} className={'k-nav-i' + (page === n.id ? ' is-active' : '')}
                  onClick={() => setPage(n.id)}>
                  <span className="k-nav-mark">{n.mark}</span>
                  <span>{n.label}</span>
                  {tag}
                </button>
              );
            })}
          </React.Fragment>
        ))}

        {showEngines && (
          <>
            <div className="k-nav-section" style={{ marginTop: 6 }}>WikiAgent · M·</div>
            <div className="k-engines">
              {[
                ['M1', 'Quant',      'ok'],
                ['M2', 'Governance', violations === 0 ? 'ok' : 'neg'],
                ['M3', 'Context',    'ok'],
                ['AB', 'Anti-BS',    'ok'],
                ['FR', 'Fragility',  'ok'],
              ].map(([id, name, tone]) => (
                <div key={id} className={'k-engine-row ' + tone}>
                  <span className="id">{id}</span>
                  <span>{name}</span>
                  <span className="pulse" />
                </div>
              ))}
            </div>
          </>
        )}

        {/* upcoming */}
        <div className="k-nav-section" style={{ marginTop: 6 }}>Agenda</div>
        <div style={{ margin: '0 12px', padding: '10px 12px',
          background: 'var(--surface-1)', border: '1px solid var(--rule)',
          borderRadius: 'var(--radius-sm)', display: 'flex', flexDirection: 'column', gap: 6 }}>
          <div style={{ fontFamily: 'var(--font-ui)', fontSize: 9.5, letterSpacing: '0.14em',
            textTransform: 'uppercase', color: 'var(--ink-3)' }}>{nextEvent.d}</div>
          <div style={{ fontFamily: 'var(--font-ui)', fontSize: 12, color: 'var(--ink)' }}>
            {nextEvent.title}
          </div>
          <div className="mono" style={{ fontSize: 11,
            color: nextEvent.v >= 0 ? 'var(--moss)' : 'var(--ink-2)' }}>
            {brl(nextEvent.v, { compact: true, sign: true })}
          </div>
        </div>
      </nav>

      <div className="k-side-f">
        <div className="k-user">
          <div className="av">RM</div>
          <div style={{ minWidth: 0, flex: 1 }}>
            <div className="name">Roberto Milet</div>
            <div className="meta">cenário · {scenario.toLowerCase()}</div>
          </div>
          <button className="k-btn ghost" style={{ padding: '4px 6px' }}>⚙</button>
        </div>
      </div>
    </aside>
  );
}

function TopBar({ title, sub, action, mood, dataDate }) {
  return (
    <header className="k-top">
      <div className="k-top-l">
        <h1 className="k-top-title">{title}</h1>
        {sub && <span className="k-top-sub">{sub}</span>}
      </div>
      <div className="k-top-r">
        <span className="k-coord narrow-hide">
          <span className="k-coord-dot" />
          <span>22°54′S · 43°10′W</span>
          <span style={{ color: 'var(--ink-4)' }}>·</span>
          <span>{dataDate}</span>
        </span>
        {action}
      </div>
    </header>
  );
}

Object.assign(window, { Sidebar, TopBar, BrandMark, NAV });
