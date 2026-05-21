// page_transactions.jsx — the full ledger view, the heart of the app

const { useState: useStateT } = React;

function PageTransactions() {
  const [filter, setFilter] = useStateT('todas');
  const [moodFilter, setMoodFilter] = useStateT(null);

  const moodCount = {};
  TX.forEach(t => { if (t.mood) moodCount[t.mood] = (moodCount[t.mood] || 0) + 1; });
  const moods = Object.entries(moodCount).sort((a, b) => b[1] - a[1]).slice(0, 8);

  const filtered = TX.filter(t => {
    if (filter === 'entradas') return t.v > 0;
    if (filter === 'saídas')   return t.v < 0 && t.k !== 'invest';
    if (filter === 'invest')   return t.k === 'invest';
    if (filter === 'auto')     return t.auto;
    return true;
  }).filter(t => !moodFilter || t.mood === moodFilter);

  return (
    <div className="k-page">
      {/* Summary strip */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 16, marginBottom: 22 }}>
        <Stat kicker="Entradas · mês" v={brl(monthIn, { compact: true })}
          sub="3 fontes" tone="pos" />
        <Stat kicker="Saídas · mês" v={brl(Math.abs(monthOut), { compact: true })}
          sub={TX.filter(t => t.v < 0 && t.k !== 'invest').length + ' lançamentos'} />
        <Stat kicker="Saldo líquido" v={brl(monthIn + monthOut, { compact: true, sign: true })}
          sub="poupança bruta · 76%" tone="pos" />
        <Stat kicker="Investido" v={brl(Math.abs(monthInvest), { compact: true })}
          sub="aporte mensal" tone="brass" />
      </div>

      {/* Filters bar */}
      <div style={{ display: 'flex', gap: 12, alignItems: 'center', marginBottom: 16, flexWrap: 'wrap' }}>
        <div className="k-tabs">
          {[
            ['todas',    'Tudo'],
            ['entradas', 'Entradas'],
            ['saídas',   'Saídas'],
            ['invest',   'Investimento'],
            ['auto',     'Recorrentes'],
          ].map(([k, l]) => (
            <button key={k} className={'k-tab' + (filter === k ? ' is-active' : '')}
              onClick={() => setFilter(k)}>{l}</button>
          ))}
        </div>
        <div style={{ marginLeft: 'auto', display: 'flex', gap: 6 }}>
          <button className="k-btn ghost">↧ CSV</button>
          <button className="k-btn primary">+ Lançar</button>
        </div>
      </div>

      {/* Mood chips */}
      <div style={{ display: 'flex', gap: 6, marginBottom: 18, flexWrap: 'wrap',
        alignItems: 'center' }}>
        <Mono className="dim" style={{ fontSize: 10, letterSpacing: '0.12em',
          textTransform: 'uppercase', fontWeight: 600 }}>mood</Mono>
        <button onClick={() => setMoodFilter(null)} className="k-chip"
          style={{ cursor: 'pointer', opacity: moodFilter === null ? 1 : 0.5 }}>tudo</button>
        {moods.map(([m, c]) => (
          <button key={m} onClick={() => setMoodFilter(moodFilter === m ? null : m)}
            style={{ cursor: 'pointer', opacity: moodFilter === m ? 1 : 0.7,
              background: 'transparent', padding: 0, border: 0 }}>
            <Mood k={m} />
            <Mono className="dim" style={{ marginLeft: 4, fontSize: 10 }}>{c}</Mono>
          </button>
        ))}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1.7fr 1fr', gap: 16 }}>
        <Card padded={false} title="Ledger" kicker={filtered.length + ' lançamentos'}>
          <div style={{ padding: '4px 20px 18px' }}>
            <FilteredFeed list={filtered} />
          </div>
        </Card>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          <Card title="Por categoria" kicker="mês corrente">
            <CategoryRanking list={TX} />
          </Card>
          <Card title="Por mood" kicker="comportamento · mês">
            <MoodComparison />
          </Card>
        </div>
      </div>
    </div>
  );
}

function Stat({ kicker, v, sub, tone }) {
  const color = tone === 'pos' ? 'var(--moss)' : tone === 'neg' ? 'var(--rust)' :
                tone === 'brass' ? 'var(--brass)' : 'var(--ink)';
  return (
    <Card>
      <Kicker>{kicker}</Kicker>
      <div className="serif" style={{ fontSize: 26, lineHeight: 1.1, color,
        fontVariantNumeric: 'tabular-nums', marginTop: 4 }}>{v}</div>
      <Mono className="muted" style={{ fontSize: 11, marginTop: 4 }}>{sub}</Mono>
    </Card>
  );
}

function FilteredFeed({ list }) {
  const days = [];
  const byDay = {};
  list.forEach(t => {
    if (!byDay[t.d]) { byDay[t.d] = []; days.push(t.d); }
    byDay[t.d].push(t);
  });

  if (list.length === 0) {
    return <div style={{ padding: '40px 0', textAlign: 'center', color: 'var(--ink-4)' }}>
      sem lançamentos com esse filtro
    </div>;
  }

  return (
    <div className="k-feed">
      {days.map(day => (
        <div key={day} className="k-feed-day">
          <div className="k-feed-day-h">
            {day}
            <span className="sub">{byDay[day].length} lanc.</span>
          </div>
          <div className="k-feed-list">
            {byDay[day].map((t, i) => <FeedRow key={i} tx={t} />)}
          </div>
        </div>
      ))}
    </div>
  );
}

function CategoryRanking({ list }) {
  const byCat = {};
  list.filter(t => t.v < 0 && t.k !== 'invest').forEach(t => {
    byCat[t.cat] = (byCat[t.cat] || 0) + Math.abs(t.v);
  });
  const rows = Object.entries(byCat).sort((a, b) => b[1] - a[1]).slice(0, 7);
  const max = rows[0]?.[1] || 1;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
      {rows.map(([cat, v]) => (
        <div key={cat} style={{ display: 'grid', gridTemplateColumns: '1fr auto',
          gap: 10, alignItems: 'center' }}>
          <div style={{ minWidth: 0 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between',
              fontFamily: 'var(--font-ui)', fontSize: 12 }}>
              <span style={{ color: 'var(--ink)' }}>{cat}</span>
              <Mono className="muted">{brl(v, { compact: true })}</Mono>
            </div>
            <div style={{ marginTop: 6 }}>
              <BarTrack value={v} max={max} h={4} color="var(--brass)" />
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}

function MoodComparison() {
  const m = BEHAVIOR.thisMonth, l = BEHAVIOR.lastMonth;
  const keys = ['necessario', 'obrigatorio', 'prazer', 'social', 'saude', 'impulso'];
  const max = Math.max(...keys.flatMap(k => [m[k] || 0, l[k] || 0]));
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
      {keys.map(k => {
        const a = m[k] || 0, b = l[k] || 0;
        const change = b === 0 ? (a > 0 ? 100 : 0) : ((a - b) / b * 100);
        const isUp = a >= b;
        return (
          <div key={k}>
            <div style={{ display: 'flex', justifyContent: 'space-between',
              fontFamily: 'var(--font-ui)', fontSize: 12, marginBottom: 6 }}>
              <Mood k={k} />
              <Mono style={{ color: isUp && change > 20 ? 'var(--copper)' : 'var(--ink-3)',
                fontSize: 11 }}>
                {brl(a, { compact: true })} · {pct(change, 0)}
              </Mono>
            </div>
            <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
              <div style={{ flex: 1 }}>
                <BarTrack value={a} max={max} h={4} color={isUp && change > 20 ? 'var(--copper)' : 'var(--brass)'} />
              </div>
            </div>
          </div>
        );
      })}
      <div style={{ marginTop: 4, fontFamily: 'var(--font-ui)', fontSize: 10,
        color: 'var(--ink-4)' }}>
        comparado a abril · barras proporcionais ao mês atual
      </div>
    </div>
  );
}

window.PageTransactions = PageTransactions;
