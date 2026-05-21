// page_cards.jsx — Cartões (Apple Wallet / Amex / Nubank vibe)

const { useState: useStateC } = React;

function PageCards() {
  const [active, setActive] = useStateC(CARDS[0].id);
  const card = CARDS.find(c => c.id === active);
  const cardTx = TX.filter(t => t.card === active).slice(0, 8);
  const total = CARDS.reduce((s, c) => s + c.used, 0);
  const limit = CARDS.reduce((s, c) => s + c.limit, 0);
  const next = CARDS.reduce((s, c) => s + c.next, 0);

  return (
    <div className="k-page">
      {/* Summary strip */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 16, marginBottom: 22 }}>
        <StatCard kicker="Limite usado · total" v={brl(total, { compact: true })}
          sub={`${(total / limit * 100).toFixed(0)}% de ${brl(limit, { compact: true })}`} />
        <StatCard kicker="Próximas faturas · 30d" v={brl(next, { compact: true })}
          sub="4 vencimentos" tone="brass" />
        <StatCard kicker="Cartões ativos" v={String(CARDS.length)} sub="2 PF · 1 viagem · 1 PJ" />
        <StatCard kicker="Próximo vencimento" v="17/jun" sub="Inter PJ · R$ 8,1k" tone="warn" />
      </div>

      <SecHeader title="Carteira" sub="seus cartões" action={
        <button className="k-btn primary">+ Novo cartão</button>
      } />

      <div className="k-wallet" style={{ marginBottom: 28 }}>
        {CARDS.map(c => (
          <CardObject key={c.id} c={c} active={c.id === active} onClick={() => setActive(c.id)} />
        ))}
      </div>

      {/* Selected detail */}
      <SecHeader title={card.bank + ' · ' + card.brand}
        sub={'detalhes · últimos lançamentos'}
        action={<button className="k-btn ghost">configurar →</button>} />

      <div style={{ display: 'grid', gridTemplateColumns: '320px 1fr', gap: 16 }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
          <Card padded={false}>
            <div style={{ padding: '14px 18px' }}>
              <Kicker>Próxima fatura</Kicker>
              <div className="serif" style={{ fontSize: 30, color: 'var(--ink)',
                fontVariantNumeric: 'tabular-nums', marginTop: 4 }}>
                {brl(card.next, { compact: false, cents: false })}
              </div>
              <Mono className="muted" style={{ fontSize: 11 }}>fecha {card.closing} · vence {card.due}</Mono>
              <div style={{ marginTop: 14 }}>
                <BarTrack value={card.used} max={card.limit} h={6} />
                <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 6,
                  fontFamily: 'var(--font-mono)', fontSize: 10, color: 'var(--ink-3)' }}>
                  <span>{brl(card.used, { compact: true })} usado</span>
                  <span>{brl(card.limit, { compact: true })} limite</span>
                </div>
              </div>
            </div>
          </Card>
          <Card title="Saúde do uso" kicker="comportamento">
            <ul style={{ margin: 0, padding: 0, listStyle: 'none', display: 'flex', flexDirection: 'column', gap: 8 }}>
              {[
                ['Categoria dominante', 'alimentação · 38%'],
                ['Lançamentos no mês',  '14'],
                ['Maior compra',        'R$ 480 · vinho'],
                ['Recorrentes',         '4 ativos'],
              ].map(([l, v]) => (
                <li key={l} style={{ display: 'flex', justifyContent: 'space-between',
                  fontFamily: 'var(--font-ui)', fontSize: 12 }}>
                  <span className="muted">{l}</span>
                  <Mono style={{ color: 'var(--ink)' }}>{v}</Mono>
                </li>
              ))}
            </ul>
          </Card>
        </div>

        <Card title="Lançamentos · 30d" kicker={card.bank} padded={false}>
          <div style={{ padding: '0 16px 16px' }}>
            {cardTx.length === 0 && (
              <div style={{ padding: '40px 0', textAlign: 'center', color: 'var(--ink-4)' }}>
                sem lançamentos recentes neste cartão
              </div>
            )}
            {cardTx.map((t, i) => <FeedRow key={i} tx={t} />)}
          </div>
        </Card>
      </div>
    </div>
  );
}

function StatCard({ kicker, v, sub, tone }) {
  const color = tone === 'brass' ? 'var(--brass)' : tone === 'warn' ? 'var(--lantern)' :
                tone === 'pos' ? 'var(--moss)' : 'var(--ink)';
  return (
    <Card>
      <Kicker>{kicker}</Kicker>
      <div className="serif" style={{ fontSize: 26, lineHeight: 1.1, color,
        fontVariantNumeric: 'tabular-nums', marginTop: 4 }}>{v}</div>
      <Mono className="muted" style={{ fontSize: 11, marginTop: 4 }}>{sub}</Mono>
    </Card>
  );
}

function CardObject({ c, active, onClick }) {
  return (
    <button onClick={onClick}
      className="k-cardobj"
      style={{
        background: c.color,
        color: c.ink || 'white',
        border: active ? '1px solid var(--brass)' : '1px solid rgba(255,255,255,0.06)',
        boxShadow: active
          ? '0 22px 56px rgba(0,0,0,0.55), 0 0 0 2px var(--brass-glow), 0 0 24px var(--brass-glow)'
          : undefined,
        transform: active ? 'translateY(-3px)' : undefined,
        cursor: 'pointer',
      }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <div className="bank">{c.bank}</div>
          <div className="brand">{c.brand}</div>
        </div>
        {/* brand mark / logo placeholder */}
        <div style={{ textAlign: 'right', fontFamily: 'var(--font-serif)', fontSize: 14,
          opacity: 0.9, letterSpacing: '0.04em' }}>
          {c.bank === 'American Express' ? 'AMEX' :
           c.bank === 'Nubank' ? 'nu' :
           c.bank.includes('Inter') ? 'INTER' : '◆◆◆'}
        </div>
      </div>
      <div className="k-card-chip" style={{ position: 'absolute', top: 56, left: 22, right: 'auto' }} />
      <div className="num">•••• •••• •••• {c.last4}</div>
      <div className="row">
        <span className="holder">ROBERTO MILET</span>
        <span style={{ textAlign: 'right' }}>
          <div style={{ fontSize: 9, opacity: 0.7 }}>VENCE</div>
          <Mono style={{ fontSize: 12, opacity: 0.95 }}>{c.due}</Mono>
        </span>
      </div>
    </button>
  );
}

window.PageCards = PageCards;
