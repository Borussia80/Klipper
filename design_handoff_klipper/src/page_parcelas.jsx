// page_parcelas.jsx — Parcelamento timeline

function PageParcelas() {
  const monthlyTotal = PARCELAS.reduce((s, p) => s + p.monthly, 0);
  const remaining = PARCELAS.reduce((s, p) => s + (p.n - p.paid) * p.monthly, 0);
  const principal = PARCELAS.reduce((s, p) => s + p.total, 0);
  const paid = PARCELAS.reduce((s, p) => s + p.paid * p.monthly, 0);

  return (
    <div className="k-page">
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 16, marginBottom: 22 }}>
        <StatCardP kicker="Parcela mensal · total" v={brl(monthlyTotal, { compact: false, cents: false })}
          sub={`${PARCELAS.length} ativas`} tone="brass" />
        <StatCardP kicker="Saldo a pagar" v={brl(remaining, { compact: true })}
          sub={`${PARCELAS.reduce((s,p) => s + (p.n - p.paid), 0)} parcelas restantes`} />
        <StatCardP kicker="Principal contratado" v={brl(principal, { compact: true })}
          sub={`${(paid / principal * 100).toFixed(0)}% quitado · ${brl(paid, { compact: true })}`} tone="pos" />
        <StatCardP kicker="% da renda mensal" v={(monthlyTotal / 32400 * 100).toFixed(1) + '%'}
          sub="dentro da margem · piso M2 < 30%" tone="pos" />
      </div>

      <SecHeader title="Compromissos parcelados" sub="timeline visual"
        action={<button className="k-btn primary">+ Novo parcelamento</button>} />

      <div style={{ marginBottom: 28 }}>
        {PARCELAS.map(p => (
          <ParcelaRow key={p.id} p={p} />
        ))}
      </div>

      {/* Monthly horizon */}
      <SecHeader title="Horizonte de pagamentos" sub="próximos 12 meses" />
      <Card padded={false}>
        <div style={{ padding: '20px 24px' }}>
          <HorizonChart />
        </div>
      </Card>
    </div>
  );
}

function StatCardP({ kicker, v, sub, tone }) {
  const color = tone === 'brass' ? 'var(--brass)' : tone === 'pos' ? 'var(--moss)' :
                tone === 'warn' ? 'var(--lantern)' : 'var(--ink)';
  return (
    <Card>
      <Kicker>{kicker}</Kicker>
      <div className="serif" style={{ fontSize: 26, lineHeight: 1.1, color,
        fontVariantNumeric: 'tabular-nums', marginTop: 4, letterSpacing: '-0.01em' }}>{v}</div>
      <Mono className="muted" style={{ fontSize: 11, marginTop: 4 }}>{sub}</Mono>
    </Card>
  );
}

function ParcelaRow({ p }) {
  const progress = p.paid / p.n;
  const remaining = p.n - p.paid;
  const card = CARDS.find(c => c.id === p.card);

  return (
    <div className="k-parcela">
      <div className="k-parcela-h">
        <div style={{ display: 'flex', alignItems: 'center', gap: 12, minWidth: 0 }}>
          <IconBadge glyph={p.tag === 'casa' ? '⌂' : p.tag === 'trabalho' ? '⌘' :
            p.tag === 'educação' ? '✎' : p.tag === 'saúde' ? '♥' : '◆'} tone="brass" />
          <div>
            <div className="k-parcela-t">{p.title}</div>
            <div className="k-parcela-s">
              {p.store} · <Mono>{p.start} → {p.end}</Mono> · #{p.tag}
              {card && <span style={{ marginLeft: 8 }}>· {card.bank}</span>}
            </div>
          </div>
        </div>
        <div style={{ textAlign: 'right' }}>
          <div className="serif" style={{ fontSize: 18, color: 'var(--brass)',
            fontVariantNumeric: 'tabular-nums', letterSpacing: '-0.01em' }}>
            {brl(p.monthly, { compact: false, cents: false }).replace('R$ ', 'R$ ')}<span style={{
              fontFamily: 'var(--font-mono)', fontSize: 11, color: 'var(--ink-3)' }}> /mês</span>
          </div>
          <Mono className="muted" style={{ fontSize: 11 }}>
            {p.paid}/{p.n} pagas · faltam {remaining}
          </Mono>
        </div>
      </div>
      {/* Visual timeline: per-installment dots */}
      <div style={{ marginTop: 14, display: 'grid',
        gridTemplateColumns: `repeat(${p.n}, 1fr)`, gap: 2 }}>
        {Array.from({ length: p.n }, (_, i) => (
          <div key={i} style={{
            height: 8,
            borderRadius: 2,
            background: i < p.paid ? 'var(--brass)' : 'var(--surface-2)',
            border: '1px solid ' + (i < p.paid ? 'transparent' : 'var(--rule)'),
            boxShadow: i === p.paid ? '0 0 8px var(--brass-glow)' : 'none',
            opacity: i < p.paid ? 1 : 0.7,
          }} />
        ))}
      </div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 8,
        fontFamily: 'var(--font-mono)', fontSize: 10, color: 'var(--ink-4)' }}>
        <span>total contratado: <span style={{ color: 'var(--ink-3)' }}>{brl(p.total, { compact: true })}</span></span>
        <span>já pago: <span style={{ color: 'var(--moss)' }}>{brl(p.paid * p.monthly, { compact: true })}</span></span>
        <span>restante: <span style={{ color: 'var(--ink-2)' }}>{brl(remaining * p.monthly, { compact: true })}</span></span>
      </div>
    </div>
  );
}

function HorizonChart() {
  // 12 months from current. Build per-month sum across all parcelas.
  const months = ['mai','jun','jul','ago','set','out','nov','dez','jan','fev','mar','abr'];
  // simplified: ParcelaRow tracks start month index 0..; we just count which still active
  // For demo: just show monthly total decreasing as parcelas close
  const series = months.map((m, i) => {
    // some parcelas drop off mid-horizon (curso 4mo away, etc)
    let v = PARCELAS.reduce((s, p) => {
      const remaining = p.n - p.paid;
      return s + (i < remaining ? p.monthly : 0);
    }, 0);
    return { m, v };
  });
  const max = Math.max(...series.map(s => s.v));

  return (
    <div>
      <div style={{ display: 'grid', gridTemplateColumns: `repeat(${months.length}, 1fr)`,
        alignItems: 'flex-end', gap: 8, height: 180 }}>
        {series.map((s, i) => {
          const h = (s.v / max) * 150;
          const isCurrent = i === 0;
          return (
            <div key={i} style={{ display: 'flex', flexDirection: 'column',
              alignItems: 'center', gap: 6, height: '100%', justifyContent: 'flex-end' }}>
              <Mono style={{ fontSize: 10, color: isCurrent ? 'var(--brass)' : 'var(--ink-3)' }}>
                {brl(s.v, { compact: true })}
              </Mono>
              <div style={{
                width: '100%',
                height: h,
                background: isCurrent
                  ? 'linear-gradient(180deg, var(--brass), color-mix(in oklab, var(--brass), black 30%))'
                  : 'var(--surface-3)',
                borderRadius: 4,
                boxShadow: isCurrent ? '0 0 14px var(--brass-glow)' : 'none',
                border: '1px solid ' + (isCurrent ? 'var(--brass)' : 'var(--rule)'),
                transition: 'all 200ms ease',
              }} />
            </div>
          );
        })}
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: `repeat(${months.length}, 1fr)`,
        gap: 8, marginTop: 10 }}>
        {series.map((s, i) => (
          <div key={i} style={{ textAlign: 'center', fontFamily: 'var(--font-ui)',
            fontSize: 10, fontWeight: 600, letterSpacing: '0.06em',
            color: i === 0 ? 'var(--brass)' : 'var(--ink-3)',
            textTransform: 'uppercase' }}>{s.m}</div>
        ))}
      </div>
    </div>
  );
}

Object.assign(window, { PageParcelas, ParcelaRow });
