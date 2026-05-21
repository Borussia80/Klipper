// page_home.jsx — the new center: live financial feed

const { useState: useStateH } = React;

function PageHome({ scenario, showEngines }) {
  const d = SCENARIOS[scenario];
  const todayTx = TX.filter(t => t.d === 'hoje');
  const todayOut = todayTx.filter(t => t.v < 0 && t.k !== 'invest').reduce((s, t) => s + t.v, 0);
  const todayIn  = todayTx.filter(t => t.v > 0).reduce((s, t) => s + t.v, 0);

  return (
    <div className="k-page">
      {/* HERO STRIP — the day in money */}
      <div style={{ display: 'grid', gridTemplateColumns: '1.4fr 1fr 1fr', gap: 16, marginBottom: 16 }}>
        <Card gilt padded={false} style={{ overflow: 'hidden' }}>
          <div style={{ padding: '20px 22px 12px' }}>
            <Kicker>O dia em dinheiro · terça, 21 mai</Kicker>
            <div style={{ marginTop: 8, display: 'flex', alignItems: 'baseline', gap: 16 }}>
              <span style={{ fontFamily: 'var(--font-serif)', fontSize: 38, lineHeight: 1,
                letterSpacing: '-0.02em', color: 'var(--ink)' }}>
                {brl(todayOut + todayIn, { compact: false, cents: false }).replace('R$ ', 'R$ ')}
              </span>
              <span className="mono" style={{ fontSize: 12, color: 'var(--ink-3)' }}>
                líquido hoje
              </span>
            </div>
            <div style={{ display: 'flex', gap: 18, marginTop: 14, fontSize: 12 }}>
              <FlowStat label="entrou"   v={todayIn}    tone="pos"   icon="↗" />
              <FlowStat label="saiu"     v={todayOut}   tone="ink"   icon="↙" />
              <FlowStat label="investido" v={-3000}     tone="brass" icon="◈" />
            </div>
          </div>
          <div style={{ padding: '0 22px 14px' }}>
            <div style={{ fontFamily: 'var(--font-serif)', fontStyle: 'italic',
              fontSize: 14, color: 'var(--ink-2)', lineHeight: 1.5, marginTop: 4,
              borderTop: '1px solid var(--rule)', paddingTop: 14 }}>
              "Um vinho de R$ 480 não estava no plano — primeiro impulso do mês.
              Fora isso, fluxo respeitando o orçamento. Aporte programado executado às 09:15."
            </div>
            <div className="mono" style={{ fontSize: 10, color: 'var(--ink-4)', marginTop: 8 }}>
              ↳ narrativa Anti-BS · gerada às 16:20
            </div>
          </div>
        </Card>

        {/* Mês em curso */}
        <Card padded={false}>
          <div style={{ padding: '16px 18px 14px' }}>
            <Kicker>Maio · até hoje</Kicker>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginTop: 8 }}>
              <div className="k-metric">
                <span className="k-metric-l">Entradas</span>
                <span className="k-metric-v pos" style={{ fontSize: 22, color: 'var(--moss)' }}>{brl(monthIn, { compact: true })}</span>
                <Mono className="muted" style={{ fontSize: 11 }}>3 fontes ativas</Mono>
              </div>
              <div className="k-metric">
                <span className="k-metric-l">Saídas</span>
                <span className="k-metric-v" style={{ fontSize: 22, color: 'var(--ink)' }}>{brl(Math.abs(monthOut), { compact: true })}</span>
                <Mono className="muted" style={{ fontSize: 11 }}>{TX.filter(t => t.v < 0 && t.k !== 'invest').length} lançamentos</Mono>
              </div>
            </div>
            <div style={{ marginTop: 14 }}>
              <FlowBar segments={[
                { label: 'Necessário',  v: BEHAVIOR.thisMonth.necessario,  color: 'var(--sea)' },
                { label: 'Obrigatório', v: BEHAVIOR.thisMonth.obrigatorio, color: 'var(--ink-3)' },
                { label: 'Saúde',       v: BEHAVIOR.thisMonth.saude,        color: 'var(--lantern)' },
                { label: 'Social',      v: BEHAVIOR.thisMonth.social,       color: 'var(--sea)' },
                { label: 'Prazer',      v: BEHAVIOR.thisMonth.prazer,       color: 'var(--brass)' },
                { label: 'Impulso',     v: BEHAVIOR.thisMonth.impulso,      color: 'var(--copper)' },
              ]} />
              <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 8,
                fontFamily: 'var(--font-ui)', fontSize: 10, color: 'var(--ink-4)' }}>
                <span>composição dos gastos · por mood</span>
                <span className="mono">{brl(Math.abs(monthOut), { compact: true })}</span>
              </div>
            </div>
          </div>
        </Card>

        {/* Streak / behavior card */}
        <Card padded={false} hover>
          <div style={{ padding: '16px 18px 14px' }}>
            <Kicker>Comportamento · streak</Kicker>
            <div style={{ display: 'flex', alignItems: 'center', gap: 14, marginTop: 8 }}>
              <div style={{ position: 'relative', width: 56, height: 56, flexShrink: 0 }}>
                <svg viewBox="0 0 56 56" style={{ width: 56, height: 56 }}>
                  <circle cx="28" cy="28" r="24" fill="none" stroke="var(--rule)" strokeWidth="3" />
                  <circle cx="28" cy="28" r="24" fill="none" stroke="var(--brass)" strokeWidth="3"
                    strokeDasharray={`${(BEHAVIOR.streak.saved / 30) * 150.8} 150.8`}
                    strokeLinecap="round" transform="rotate(-90 28 28)" />
                </svg>
                <div style={{ position: 'absolute', inset: 0, display: 'grid', placeItems: 'center',
                  fontFamily: 'var(--font-serif)', fontSize: 18, color: 'var(--brass)' }}>
                  {BEHAVIOR.streak.saved}
                </div>
              </div>
              <div style={{ minWidth: 0, flex: 1 }}>
                <div style={{ fontFamily: 'var(--font-ui)', fontSize: 13, color: 'var(--ink)',
                  fontWeight: 500, lineHeight: 1.3 }}>
                  14 dias respeitando o orçamento de prazer
                </div>
                <div className="muted" style={{ fontSize: 11, marginTop: 4 }}>
                  Meta mensal: 30 dias · próximo marco em <Mono>16d</Mono>
                </div>
              </div>
            </div>
            <div style={{ marginTop: 14, paddingTop: 14, borderTop: '1px solid var(--rule)',
              display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
              <MiniStat label="prazer vs abr" v="+74%" tone="warn" />
              <MiniStat label="impulso" v="1 evento" tone="neg" />
            </div>
          </div>
        </Card>
      </div>

      {/* MAIN GRID — feed + side rail */}
      <div style={{ display: 'grid', gridTemplateColumns: '1.7fr 1fr', gap: 16 }}>
        {/* LIVE FEED */}
        <Card padded={false} title="Feed financeiro" kicker="ao vivo · todos os fluxos"
          action={
            <div style={{ display: 'flex', gap: 6 }}>
              <button className="k-btn ghost">filtrar</button>
              <button className="k-btn primary">+ Lançar</button>
            </div>
          }>
          <div style={{ padding: '4px 20px 18px' }}>
            <FeedTimeline />
          </div>
        </Card>

        {/* SIDE RAIL */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          {/* Insights */}
          <Card title="Insights" kicker="comportamento · 7d" gilt>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 12, marginTop: 2 }}>
              {BEHAVIOR.insights.map((i, k) => (
                <div key={k} style={{ display: 'grid', gridTemplateColumns: '24px 1fr',
                  gap: 10, alignItems: 'flex-start' }}>
                  <div style={{
                    width: 24, height: 24, borderRadius: '50%', display: 'grid', placeItems: 'center',
                    fontFamily: 'var(--font-mono)', fontSize: 13, fontWeight: 600,
                    color: i.tone === 'pos' ? 'var(--moss)' : i.tone === 'neg' ? 'var(--rust)' :
                           i.tone === 'warn' ? 'var(--lantern)' : 'var(--sea)',
                    background: i.tone === 'pos' ? 'rgba(123,198,138,0.08)' :
                                i.tone === 'neg' ? 'rgba(216,124,106,0.08)' :
                                i.tone === 'warn' ? 'rgba(244,213,141,0.08)' :
                                'rgba(127,179,200,0.08)',
                    border: '1px solid currentColor',
                  }}>{i.icon}</div>
                  <div>
                    <div style={{ fontFamily: 'var(--font-ui)', fontSize: 12.5,
                      color: 'var(--ink)', fontWeight: 500, lineHeight: 1.3 }}>{i.title}</div>
                    <div className="serif" style={{ fontSize: 12, fontStyle: 'italic',
                      color: 'var(--ink-3)', marginTop: 3, lineHeight: 1.45 }}>{i.body}</div>
                  </div>
                </div>
              ))}
            </div>
          </Card>

          {/* Agenda */}
          <Card title="Agenda" kicker="próximos eventos" padded={false}>
            <div style={{ padding: '4px 4px 12px' }}>
              {AGENDA.slice(0, 5).map((a, k) => (
                <div key={k} style={{
                  display: 'grid', gridTemplateColumns: '64px 1fr auto', gap: 12,
                  padding: '10px 16px', alignItems: 'center',
                  borderTop: k === 0 ? 0 : '1px solid var(--rule)',
                }}>
                  <div>
                    <div style={{ fontFamily: 'var(--font-ui)', fontSize: 10.5, fontWeight: 600,
                      letterSpacing: '0.1em', textTransform: 'uppercase', color: 'var(--ink-3)' }}>{a.d}</div>
                    <Mono style={{ fontSize: 10, color: 'var(--ink-4)' }}>{a.when}</Mono>
                  </div>
                  <div>
                    <div style={{ fontFamily: 'var(--font-ui)', fontSize: 12.5,
                      color: 'var(--ink)', lineHeight: 1.3 }}>{a.title}</div>
                    <div style={{ marginTop: 3 }}>
                      <span className="k-chip">{a.tag}</span>
                    </div>
                  </div>
                  <Mono style={{
                    fontSize: 12.5,
                    color: a.v >= 0 ? 'var(--moss)' : 'var(--ink)',
                    whiteSpace: 'nowrap',
                  }}>
                    {brl(a.v, { compact: true, sign: true })}
                  </Mono>
                </div>
              ))}
            </div>
          </Card>

          {/* Patrimônio glance */}
          <Card title="Patrimônio" kicker="snapshot · veja completo →" hover
            action={<Mono style={{ color: 'var(--brass)', fontSize: 11 }}>→</Mono>}>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 80px', gap: 14,
              alignItems: 'center' }}>
              <div>
                <div className="serif" style={{ fontSize: 26, lineHeight: 1,
                  letterSpacing: '-0.01em', color: 'var(--ink)', fontVariantNumeric: 'tabular-nums' }}>
                  {brl(d.total, { compact: true })}
                </div>
                <Mono style={{ fontSize: 11, color: d.delta30dPct >= 0 ? 'var(--moss)' : 'var(--rust)',
                  marginTop: 4 }}>
                  {brl(d.delta30d, { compact: true, sign: true })} · {pct(d.delta30dPct)} · 30d
                </Mono>
              </div>
              <Spark data={d.path.slice(-60)} w={80} h={36} color="var(--brass)" />
            </div>
            <div style={{ display: 'flex', gap: 8, marginTop: 14, flexWrap: 'wrap' }}>
              {d.allocation.slice(0, 4).map(a => (
                <div key={a.id} className="k-chip">
                  <span style={{ width: 6, height: 6, borderRadius: '50%',
                    background: `var(--${a.color})` }} />
                  {a.label.replace(' & equiv.', '')} <Mono className="muted">{(a.value*100).toFixed(0)}%</Mono>
                </div>
              ))}
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}

function FlowStat({ label, v, tone, icon }) {
  const color = tone === 'pos' ? 'var(--moss)' : tone === 'brass' ? 'var(--brass)' : 'var(--ink)';
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
      <span style={{ width: 22, height: 22, borderRadius: '50%', display: 'grid', placeItems: 'center',
        background: `color-mix(in oklab, ${color}, transparent 88%)`, color,
        fontFamily: 'var(--font-mono)', fontSize: 12, fontWeight: 600 }}>{icon}</span>
      <div>
        <div className="ui" style={{ fontSize: 9.5, letterSpacing: '0.14em', textTransform: 'uppercase',
          color: 'var(--ink-3)', fontWeight: 600 }}>{label}</div>
        <Mono style={{ fontSize: 13, color, fontWeight: 500 }}>{brl(Math.abs(v), { compact: true })}</Mono>
      </div>
    </div>
  );
}

function MiniStat({ label, v, tone }) {
  const color = tone === 'pos' ? 'var(--moss)' : tone === 'neg' ? 'var(--rust)' :
                tone === 'warn' ? 'var(--lantern)' : 'var(--ink)';
  return (
    <div>
      <div className="ui muted" style={{ fontSize: 10, letterSpacing: '0.1em', textTransform: 'uppercase',
        fontWeight: 600 }}>{label}</div>
      <div style={{ fontFamily: 'var(--font-serif)', fontSize: 16, color }}>{v}</div>
    </div>
  );
}

function FeedTimeline({ limit = 999 }) {
  // group by day label
  const days = [];
  const byDay = {};
  TX.slice(0, limit).forEach(t => {
    if (!byDay[t.d]) { byDay[t.d] = []; days.push(t.d); }
    byDay[t.d].push(t);
  });

  return (
    <div className="k-feed">
      {days.map((day, di) => (
        <div key={day} className="k-feed-day">
          <div className="k-feed-day-h">
            {day}
            <span className="sub">
              {byDay[day].length} {byDay[day].length === 1 ? 'lançamento' : 'lançamentos'}
            </span>
            <span className="sub mono" style={{ color: 'var(--ink-3)' }}>
              {(() => {
                const net = byDay[day].reduce((s, t) => s + t.v, 0);
                return brl(net, { compact: true, sign: true });
              })()}
            </span>
          </div>
          <div className="k-feed-list">
            {byDay[day].map((t, ti) => <FeedRow key={ti} tx={t} />)}
          </div>
        </div>
      ))}
    </div>
  );
}

function FeedRow({ tx }) {
  const icon = tx.k === 'in' ? '↗' : tx.k === 'invest' ? '◈' : tx.cat === 'transporte' ? '➜' :
               tx.cat === 'alimentação' ? '◉' : tx.cat === 'saúde' ? '♥' : tx.cat === 'prazer' ? '✦' :
               tx.cat === 'casa' ? '⌂' : tx.cat === 'família' ? '◐' : tx.cat === 'assinaturas' ? '↻' :
               tx.cat === 'educação' ? '✎' : tx.cat === 'pet' ? '♣' : '·';
  const iconClass = tx.k === 'in' ? 'in' : tx.k === 'invest' ? 'invest' : 'out';
  return (
    <div className="k-feed-row">
      <div className={'icon ' + iconClass}>{icon}</div>
      <div className="body">
        <div className="top">
          <span className="t">{tx.t}</span>
          {tx.auto && <span className="k-chip" style={{ padding: '1px 6px', fontSize: 9.5 }}>auto</span>}
        </div>
        <div className="meta">
          <Mono style={{ fontSize: 10.5 }}>{tx.time}</Mono>
          <span className="dot" />
          <span>{tx.cat}</span>
          {tx.mood && <Mood k={tx.mood} />}
          {tx.card && (
            <>
              <span className="dot" />
              <span style={{ color: 'var(--ink-4)' }}>·{CARDS.find(c => c.id === tx.card)?.brand.split(' ')[0]}</span>
            </>
          )}
        </div>
        {tx.note && <div className="note">"{tx.note}"</div>}
      </div>
      <div style={{ textAlign: 'right' }}>
        <div className={'v ' + (tx.v > 0 && tx.k !== 'invest' ? 'pos' : tx.k === 'invest' ? 'invest' : '')}>
          {brl(tx.v, { compact: false, sign: tx.v > 0, cents: Math.abs(tx.v) < 1000 })}
        </div>
      </div>
    </div>
  );
}

Object.assign(window, { PageHome, FeedTimeline, FeedRow });
