// page_capital.jsx — Patrimônio, Posições, Teses (capital trio)

const { useState: useStateK } = React;

function PagePatrimonio({ scenario, showEngines }) {
  const d = SCENARIOS[scenario];
  const isUp = d.delta30d >= 0;
  return (
    <div className="k-page">
      {/* HERO */}
      <div style={{ display: 'grid', gridTemplateColumns: '1.8fr 1fr 1fr 1fr', gap: 16, marginBottom: 16 }}>
        <Card gilt padded={false}>
          <div style={{ padding: '20px 22px 6px' }}>
            <Kicker>Patrimônio líquido · {d.label.toLowerCase()}</Kicker>
            <div style={{ display: 'flex', alignItems: 'baseline', justifyContent: 'space-between',
              gap: 14, marginTop: 6, flexWrap: 'wrap' }}>
              <div className="serif" style={{ fontSize: 40, lineHeight: 1, color: 'var(--ink)',
                fontVariantNumeric: 'tabular-nums', letterSpacing: '-0.02em', whiteSpace: 'nowrap' }}>
                {brl(d.total, { compact: false, cents: false })}
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 2, alignItems: 'flex-end' }}>
                <Mono style={{ color: isUp ? 'var(--moss)' : 'var(--rust)', fontSize: 13 }}>
                  {brl(d.delta30d, { compact: true, sign: true })} · {pct(d.delta30dPct)} · 30d
                </Mono>
                <Mono className="muted" style={{ fontSize: 11 }}>
                  {brl(d.delta12m, { compact: true, sign: true })} · {pct(d.delta12mPct)} · 12m
                </Mono>
              </div>
            </div>
          </div>
          <div style={{ padding: '0 8px' }}>
            <AreaChart data={d.path} h={160} color="var(--brass)" mark={d.path.length - 1} />
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', padding: '4px 22px 16px',
            fontFamily: 'var(--font-mono)', fontSize: 10, color: 'var(--ink-4)',
            letterSpacing: '0.05em' }}>
            {['180d','120d','90d','60d','30d','hoje'].map(s => <span key={s}>{s}</span>)}
          </div>
        </Card>

        <Card>
          <Kicker>Caixa & liquidez</Kicker>
          <div className="serif" style={{ fontSize: 28, color: 'var(--ink)',
            fontVariantNumeric: 'tabular-nums', marginTop: 4 }}>{(d.cash * 100).toFixed(1)}%</div>
          <Mono className="muted" style={{ fontSize: 11 }}>{brl(d.total * d.cash, { compact: true })}</Mono>
          <div style={{ marginTop: 14 }}>
            <Mono className="muted" style={{ fontSize: 10 }}>limite M2 ≥ 20%</Mono>
            <div style={{ marginTop: 6 }}>
              <BarTrack value={d.cash} max={0.30} h={6}
                color={d.cash >= 0.20 ? 'var(--moss)' : 'var(--rust)'} />
            </div>
          </div>
        </Card>

        {showEngines && (
          <Card>
            <div style={{ display: 'flex', gap: 14, alignItems: 'center' }}>
              <FragilityGauge value={d.fragility} size={96} />
              <div>
                <Kicker>Fragility</Kicker>
                <div className="ui" style={{ fontSize: 12.5, color: 'var(--ink-2)', lineHeight: 1.4, marginTop: 4 }}>
                  Resiliência a choques.<br />
                  <strong style={{ color: 'var(--ink)' }}>
                    {d.fragility < 0.4 ? 'Robusta' : d.fragility < 0.65 ? 'Vigilância' : 'Frágil'}
                  </strong>
                </div>
              </div>
            </div>
          </Card>
        )}

        {showEngines && (
          <Card>
            <Kicker>Anti-BS · M1</Kicker>
            <div style={{ display: 'flex', alignItems: 'baseline', gap: 8, marginTop: 4 }}>
              <span className="serif" style={{ fontSize: 30, fontVariantNumeric: 'tabular-nums',
                color: d.antiBs.score >= 80 ? 'var(--moss)' : d.antiBs.score >= 50 ? 'var(--lantern)' : 'var(--rust)' }}>
                {d.antiBs.score}
              </span>
              <Mono className="muted" style={{ fontSize: 11 }}>/100</Mono>
            </div>
            <Mono className="muted" style={{ fontSize: 11, marginTop: 4, display: 'block' }}>
              {d.antiBs.flags} {d.antiBs.flags === 1 ? 'flag ativa' : 'flags ativas'}
            </Mono>
            {d.antiBs.flags > 0 && (
              <div style={{ marginTop: 10, padding: '8px 10px',
                background: 'rgba(216,124,106,0.08)', border: '1px solid rgba(216,124,106,0.3)',
                borderRadius: 'var(--radius-xs)', color: 'var(--rust)', fontSize: 11 }}>
                ▲ tese "watch" sem downgrade
              </div>
            )}
          </Card>
        )}
      </div>

      {/* allocation + governance + theses */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 16 }}>
        <Card title="Alocação por classe" kicker="snapshot · hoje">
          <div style={{ display: 'flex', alignItems: 'center', gap: 22 }}>
            <DonutChart data={d.allocation} size={160} thickness={16}
              centerValue={brl(d.total, { compact: true })} centerLabel="patrimônio" />
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8, flex: 1 }}>
              {d.allocation.map(a => (
                <div key={a.id} style={{ display: 'grid', gridTemplateColumns: '10px 1fr auto',
                  alignItems: 'center', gap: 10, fontSize: 12 }}>
                  <span style={{ width: 10, height: 10, borderRadius: 2,
                    background: `var(--${a.color})` }} />
                  <span className="muted">{a.label}</span>
                  <Mono>{(a.value * 100).toFixed(0)}%</Mono>
                </div>
              ))}
            </div>
          </div>
        </Card>

        {showEngines && (
          <Card title="Governance · M2" kicker="beginner mode · limites duros">
            <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
              <GovRow label="Max por ativo"   ok={d.governance.maxAsset.ok}
                v={d.governance.maxAsset.value} lim={d.governance.maxAsset.limit}
                top={d.governance.maxAsset.top} />
              <GovRow label="Max por tese"    ok={d.governance.maxThesis.ok}
                v={d.governance.maxThesis.value} lim={d.governance.maxThesis.limit}
                top={d.governance.maxThesis.top} />
              <GovRow label="Caixa mínimo"     ok={d.governance.minCash.ok}
                v={d.governance.minCash.value} lim={d.governance.minCash.limit} />
              <div style={{ padding: '10px 12px',
                background: 'var(--surface-1)', border: '1px solid var(--rule)',
                borderRadius: 'var(--radius-xs)',
                fontFamily: 'var(--font-ui)', fontSize: 11.5, color: 'var(--ink-3)' }}>
                {[d.governance.maxAsset, d.governance.maxThesis, d.governance.minCash].every(g => g.ok)
                  ? '✓ Carteira dentro dos limites M2.'
                  : '▲ Violações detectadas. Próxima ordem exigirá rebal ou override.'}
              </div>
            </div>
          </Card>
        )}
      </div>

      <Card title="Teses ativas" kicker="apostas firmes · M3 contexto"
        action={<button className="k-btn">+ Tese</button>} padded={false}>
        <table className="k-tbl">
          <thead>
            <tr>
              <th>Tese</th><th>Status</th><th>Conviction</th>
              <th style={{ textAlign: 'right' }}>Alocação</th>
              <th style={{ textAlign: 'right' }}>Perf 12m</th>
              <th>Risco</th><th style={{ width: '30%' }}>Âncora (M1)</th>
            </tr>
          </thead>
          <tbody>
            {d.theses.map(th => (
              <tr key={th.id}>
                <td style={{ color: 'var(--ink)', fontWeight: 500 }}>{th.name}</td>
                <td>
                  <span className={'k-chip ' + (th.status === 'on-track' ? 'pos' : th.status === 'breach' ? 'neg' : 'warn')}>
                    <StatusDot status={th.status} />
                    {th.status === 'on-track' ? 'on track' : th.status === 'watch' ? 'watch' :
                     th.status === 'over-limit' ? 'over-limit' : 'breach'}
                  </span>
                </td>
                <td><Conviction value={th.conviction} /></td>
                <td className="num">{(th.alloc * 100).toFixed(1)}%</td>
                <td className={'num ' + (th.perf12m >= 0 ? 'pos' : 'neg')}>{pct(th.perf12m)}</td>
                <td><RiskBar v={th.risk} /></td>
                <td className="serif muted" style={{ fontSize: 12, fontStyle: 'italic' }}>{th.anchor}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </Card>
    </div>
  );
}

function GovRow({ label, ok, v, lim, top }) {
  const ratio = v / lim;
  const fillPct = Math.min(100, ratio * 100);
  const tone = ok ? 'var(--moss)' : 'var(--rust)';
  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between',
        fontFamily: 'var(--font-ui)', fontSize: 11.5 }}>
        <span style={{ color: 'var(--ink-2)' }}>{label}</span>
        <Mono style={{ color: tone }}>
          {ok ? '✓' : '✕'} {(v*100).toFixed(1)}% / {(lim*100).toFixed(0)}%
        </Mono>
      </div>
      {top && <Mono className="dim" style={{ fontSize: 10, marginTop: 2, display: 'block' }}>
        top: {top}
      </Mono>}
      <div style={{ marginTop: 6, height: 4, background: 'var(--surface-2)',
        borderRadius: 2, overflow: 'hidden', border: '1px solid var(--rule)' }}>
        <div style={{ width: fillPct + '%', height: '100%', background: tone, opacity: 0.7 }} />
      </div>
    </div>
  );
}

function StatusDot({ status }) {
  const c = status === 'on-track' ? 'var(--moss)' :
            status === 'watch' || status === 'over-limit' ? 'var(--lantern)' : 'var(--rust)';
  return <span style={{ display: 'inline-block', width: 6, height: 6, borderRadius: '50%', background: c }} />;
}

function Conviction({ value }) {
  return (
    <div style={{ display: 'flex', gap: 2 }}>
      {[1,2,3,4,5].map(i => (
        <span key={i} style={{ width: 6, height: 11, borderRadius: 1,
          background: i <= value ? 'var(--brass)' : 'var(--rule-2)',
          boxShadow: i <= value ? '0 0 4px var(--brass-glow)' : 'none' }} />
      ))}
    </div>
  );
}

function RiskBar({ v }) {
  const tone = v < 0.35 ? 'var(--moss)' : v < 0.6 ? 'var(--lantern)' : 'var(--rust)';
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
      <div style={{ width: 56, height: 4, background: 'var(--surface-2)',
        borderRadius: 2, border: '1px solid var(--rule)', overflow: 'hidden' }}>
        <div style={{ width: (v * 100) + '%', height: '100%', background: tone }} />
      </div>
      <Mono style={{ fontSize: 10.5, color: 'var(--ink-3)' }}>{v.toFixed(2)}</Mono>
    </div>
  );
}

// ─── POSITIONS ──────────────────────────────────────────────
function PagePositions({ scenario, showEngines }) {
  const d = SCENARIOS[scenario];
  const rows = d.positions.map(p => ({
    ...p, total: p.qty * p.price, cost_total: p.qty * p.cost,
    pl: p.qty * (p.price - p.cost), plpct: (p.price / p.cost - 1) * 100,
  }));
  if (rows.length === 0) {
    return (
      <div className="k-page">
        <Card>
          <div style={{ padding: 24, textAlign: 'center', color: 'var(--ink-3)' }}>
            Posições disponíveis apenas no cenário realista (demo).
          </div>
        </Card>
      </div>
    );
  }
  const totalPL = rows.reduce((s, r) => s + r.pl, 0);
  const totalNow = rows.reduce((s, r) => s + r.total, 0);

  return (
    <div className="k-page">
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 16, marginBottom: 16 }}>
        <StatNum kicker="Valor de mercado" v={brl(totalNow, { compact: true })} />
        <StatNum kicker="P&L total" v={brl(totalPL, { compact: true, sign: true })}
          tone={totalPL >= 0 ? 'pos' : 'neg'} />
        <StatNum kicker="Var dia (pond.)"
          v={pct(rows.reduce((s, r) => s + r.chg * r.total, 0) / totalNow)}
          tone="pos" />
        <StatNum kicker="Beta vs IBOV" v="0.72" />
      </div>

      <Card title="Posições" kicker="market-mark · live"
        action={
          <div style={{ display: 'flex', gap: 6 }}>
            <button className="k-btn ghost">↧ CSV</button>
            <button className="k-btn primary">+ Posição</button>
          </div>
        }
        padded={false}>
        <table className="k-tbl">
          <thead>
            <tr>
              <th>Ativo</th><th>Classe</th>
              <th style={{ textAlign: 'right' }}>Qtd</th>
              <th style={{ textAlign: 'right' }}>Preço</th>
              <th style={{ textAlign: 'right' }}>Custo médio</th>
              <th style={{ textAlign: 'right' }}>Valor</th>
              <th style={{ textAlign: 'right' }}>P&L</th>
              <th style={{ textAlign: 'right' }}>Var dia</th>
            </tr>
          </thead>
          <tbody>
            {rows.map(r => (
              <tr key={r.t}>
                <td><span className="ticker">{r.t}</span></td>
                <td className="muted">{r.cls}</td>
                <td className="num">{r.qty.toLocaleString('pt-BR', { maximumFractionDigits: 4 })}</td>
                <td className="num">{r.price.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</td>
                <td className="num muted">{r.cost.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</td>
                <td className="num">{brl(r.total, { compact: true })}</td>
                <td className={'num ' + (r.pl >= 0 ? 'pos' : 'neg')}>{brl(r.pl, { compact: true, sign: true })}</td>
                <td className={'num ' + (r.chg >= 0 ? 'pos' : 'neg')}>{pct(r.chg, 2)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </Card>
    </div>
  );
}

// ─── THESES ────────────────────────────────────────────────
function PageTheses({ scenario, showEngines }) {
  const d = SCENARIOS[scenario];
  const [active, setActive] = useStateK(d.theses[0].id);
  const th = d.theses.find(x => x.id === active) || d.theses[0];

  return (
    <div className="k-page">
      <div style={{ display: 'grid', gridTemplateColumns: '320px 1fr', gap: 16 }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
          <SecHeader title="Teses ativas" sub={d.theses.length + ' apostas'}
            action={<button className="k-btn primary" style={{ padding: '5px 12px' }}>+ Tese</button>} />
          {d.theses.map(t => (
            <button key={t.id} onClick={() => setActive(t.id)} style={{
              textAlign: 'left', padding: '14px 16px',
              background: active === t.id ? 'var(--surface-3)' : 'var(--surface-1)',
              border: '1px solid ' + (active === t.id ? 'var(--rule-brass)' : 'var(--rule)'),
              borderRadius: 'var(--radius-sm)',
              cursor: 'pointer', display: 'flex', flexDirection: 'column', gap: 8,
              boxShadow: active === t.id ? '0 0 16px var(--brass-glow)' : 'none',
              transition: 'all 160ms ease',
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <StatusDot status={t.status} />
                <span style={{ fontFamily: 'var(--font-ui)', fontSize: 13.5, color: 'var(--ink)',
                  fontWeight: 500 }}>{t.name}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                fontSize: 11 }}>
                <Conviction value={t.conviction} />
                <Mono style={{ color: t.perf12m >= 0 ? 'var(--moss)' : 'var(--rust)' }}>
                  {pct(t.perf12m)} · 12m
                </Mono>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between',
                fontFamily: 'var(--font-mono)', fontSize: 11, color: 'var(--ink-3)' }}>
                <span>{(t.alloc * 100).toFixed(1)}% PL</span>
                <span>risco {t.risk.toFixed(2)}</span>
              </div>
            </button>
          ))}
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          <Card title={th.name} kicker="tese · M3 contexto" gilt
            action={<div style={{ display: 'flex', gap: 6 }}>
              <button className="k-btn ghost">editar</button>
              <button className="k-btn">encerrar</button>
            </div>}>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 20 }}>
              <div className="k-metric">
                <span className="k-metric-l">Alocação</span>
                <span className="k-metric-v">{(th.alloc * 100).toFixed(1)}<span style={{ fontSize: 18, color: 'var(--ink-3)' }}>%</span></span>
                <Mono className="muted" style={{ fontSize: 11 }}>{brl(d.total * th.alloc, { compact: true })}</Mono>
              </div>
              <div className="k-metric">
                <span className="k-metric-l">Perf 12m</span>
                <span className="k-metric-v" style={{ color: th.perf12m >= 0 ? 'var(--moss)' : 'var(--rust)' }}>{pct(th.perf12m)}</span>
                <Mono className="muted" style={{ fontSize: 11 }}>vs CDI {pct(th.perf12m - 9.4)}</Mono>
              </div>
              <div className="k-metric">
                <span className="k-metric-l">Conviction</span>
                <div style={{ marginTop: 8 }}><Conviction value={th.conviction} /></div>
                <Mono className="muted" style={{ fontSize: 11 }}>{th.conviction}/5</Mono>
              </div>
              <div className="k-metric">
                <span className="k-metric-l">Risco</span>
                <span className="k-metric-v" style={{ color: th.risk < 0.4 ? 'var(--moss)' : th.risk < 0.6 ? 'var(--lantern)' : 'var(--rust)' }}>{th.risk.toFixed(2)}</span>
                <Mono className="muted" style={{ fontSize: 11 }}>vol normalizada</Mono>
              </div>
            </div>
            <div style={{ height: 1, background: 'var(--rule)', margin: '18px 0' }} />
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24 }}>
              <div>
                <Kicker>Âncora quant (M1)</Kicker>
                <p className="serif" style={{ marginTop: 4, color: 'var(--ink-2)', fontSize: 13.5,
                  lineHeight: 1.55, fontStyle: 'italic' }}>
                  "{th.anchor}"
                </p>
                <div style={{ marginTop: 10, padding: '10px 12px',
                  background: 'var(--surface-1)', border: '1px solid var(--rule)',
                  borderRadius: 'var(--radius-xs)' }}>
                  <Mono className="muted" style={{ fontSize: 10 }}>condições verificadas hoje</Mono>
                  <Mono style={{ fontSize: 11.5,
                    color: th.status === 'on-track' ? 'var(--moss)' : 'var(--lantern)',
                    display: 'block', marginTop: 4 }}>
                    {th.status === 'on-track' ? '✓ todas as condições satisfeitas' : '▲ 1 de 3 próximas do limite'}
                  </Mono>
                </div>
              </div>
              <div>
                <Kicker>Contexto macro (M3)</Kicker>
                <ul style={{ marginTop: 4, paddingLeft: 18, color: 'var(--ink-2)', fontSize: 12.5,
                  lineHeight: 1.7, fontFamily: 'var(--font-ui)' }}>
                  <li>Selic terminal 9.5% precificada na curva DI</li>
                  <li>Inflação implícita 2y: 4.18%</li>
                  <li>Carry vs T-bond 10y: +5.2pp</li>
                  <li>Score sentimento: <Mono style={{ color: 'var(--moss)' }}>+0.34</Mono></li>
                </ul>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}

function StatNum({ kicker, v, sub, tone }) {
  const color = tone === 'pos' ? 'var(--moss)' : tone === 'neg' ? 'var(--rust)' :
                tone === 'brass' ? 'var(--brass)' : 'var(--ink)';
  return (
    <Card>
      <Kicker>{kicker}</Kicker>
      <div className="serif" style={{ fontSize: 26, lineHeight: 1.1, color,
        fontVariantNumeric: 'tabular-nums', marginTop: 4 }}>{v}</div>
      {sub && <Mono className="muted" style={{ fontSize: 11, marginTop: 4 }}>{sub}</Mono>}
    </Card>
  );
}

Object.assign(window, { PagePatrimonio, PagePositions, PageTheses });
