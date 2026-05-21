// page_consilium.jsx — AI Consilium (multi-provider)

const { useState: useStateO } = React;

function PageConsilium({ scenario, showEngines }) {
  const [active, setActive] = useStateO(['claude', 'gemini', 'openai', 'qwen']);
  const [view, setView] = useStateO('panel');
  const toggle = (id) => setActive(a => a.includes(id) ? a.filter(x => x !== id) : [...a, id]);

  return (
    <div className="k-page">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
        <div>
          <Kicker>M4 · AI Consilium</Kicker>
          <div className="serif" style={{ fontSize: 24, color: 'var(--ink)', marginTop: 4,
            letterSpacing: '-0.01em' }}>Conselho de modelos</div>
          <Mono className="muted" style={{ fontSize: 11.5, marginTop: 4 }}>
            auto-routing · LiteLLM · custo total hoje R$ 1,42
          </Mono>
        </div>
        <div className="k-tabs">
          <button className={'k-tab' + (view === 'panel' ? ' is-active' : '')} onClick={() => setView('panel')}>
            Painel
          </button>
          <button className={'k-tab' + (view === 'conversation' ? ' is-active' : '')} onClick={() => setView('conversation')}>
            Conversa
          </button>
        </div>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '12px 16px',
        background: 'var(--surface-1)', border: '1px solid var(--rule)',
        borderRadius: 'var(--radius)', marginBottom: 16, flexWrap: 'wrap' }}>
        <Mono className="muted" style={{ fontSize: 10, letterSpacing: '0.12em',
          textTransform: 'uppercase', fontWeight: 600 }}>providers</Mono>
        {Object.keys(PROVIDERS).map(id => (
          <ProviderPill key={id} id={id} active={active.includes(id)} onClick={() => toggle(id)} />
        ))}
        <Mono className="dim" style={{ marginLeft: 'auto', fontSize: 10 }}>
          ordem: Claude → Gemini → GPT-4o → Qwen
        </Mono>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 360px', gap: 16 }}>
        <Card padded={false} style={{ minHeight: 540 }}>
          <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
            <div style={{ flex: 1, minHeight: 0, overflowY: 'auto' }}>
              {view === 'panel' ? <PanelView active={active} /> : <ConversationView active={active} />}
            </div>
            <Composer />
          </div>
        </Card>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
          <Card title="Contexto enviado" kicker="M3 · snapshot">
            <ContextChips scenario={scenario} />
          </Card>
          {showEngines && (
            <Card title="Regras do Agente" kicker="KB WikiAgent">
              <ul style={{ margin: 0, paddingLeft: 18, fontFamily: 'var(--font-ui)',
                fontSize: 12, color: 'var(--ink-2)', lineHeight: 1.7 }}>
                <li>Matemática ancora · narrativa sem evidência não move decisão</li>
                <li>Contexto modula risco — nunca compra ativo</li>
                <li>Declarar incerteza sempre</li>
                <li>Sem verborreia</li>
                <li>M2 Beginner: ativo ≤ 10%, tese ≤ 25%, caixa ≥ 20%</li>
              </ul>
            </Card>
          )}
          <Card title="Custo & uso" kicker="hoje" padded={false}>
            <table className="k-tbl">
              <thead>
                <tr><th>Provider</th><th style={{ textAlign: 'right' }}>Calls</th>
                  <th style={{ textAlign: 'right' }}>Tokens</th>
                  <th style={{ textAlign: 'right' }}>Custo</th></tr>
              </thead>
              <tbody>
                {[
                  ['claude', 14, '24.8k', 0.682],
                  ['gemini', 22, '38.4k', 0.184],
                  ['openai', 8,  '12.1k', 0.421],
                  ['qwen',   31, '42.0k', 0.082],
                  ['kimi',   4,  '6.2k',  0.048],
                ].map(([p, c, t, $]) => {
                  const pr = PROVIDERS[p];
                  return (
                    <tr key={p}>
                      <td><span style={{ color: pr.color, marginRight: 6 }}>{pr.glyph}</span>{pr.name}</td>
                      <td className="num">{c}</td>
                      <td className="num">{t}</td>
                      <td className="num">R$ {$.toFixed(3)}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </Card>
        </div>
      </div>
    </div>
  );
}

function ProviderPill({ id, active, onClick }) {
  const p = PROVIDERS[id];
  return (
    <button onClick={onClick} className="k-prov" style={{
      borderColor: active ? p.color : 'var(--rule-2)',
      background: active ? `color-mix(in oklab, ${p.color}, transparent 85%)` : 'transparent',
      color: active ? p.color : 'var(--ink-3)',
      cursor: 'pointer',
    }}>
      <span style={{ color: p.color, fontSize: 13, lineHeight: 1 }}>{p.glyph}</span>
      <span>{p.name}</span>
      <span style={{ color: 'var(--ink-4)', fontSize: 9.5 }}>· {p.vendor}</span>
    </button>
  );
}

function PanelView({ active }) {
  const userMsg = CONSILIUM_THREAD[0];
  const responses = CONSILIUM_THREAD.filter(m => m.role === 'assistant' && active.includes(m.provider));
  return (
    <div>
      <div className="k-msg user">
        <div className="k-msg-h">
          <span style={{ width: 24, height: 24, borderRadius: '50%',
            background: 'var(--brass)', color: 'var(--bg)',
            display: 'grid', placeItems: 'center',
            fontFamily: 'var(--font-serif)', fontSize: 11, fontWeight: 700 }}>RM</span>
          <span style={{ color: 'var(--ink)' }}>Roberto</span>
          <span style={{ marginLeft: 'auto' }}>{userMsg.when}</span>
        </div>
        <div className="k-msg-b">"{userMsg.text}"</div>
      </div>
      <div style={{ display: 'grid',
        gridTemplateColumns: `repeat(${Math.min(2, responses.length) || 1}, 1fr)`,
        borderTop: '1px solid var(--rule)' }}>
        {responses.map((m, i) => {
          const p = PROVIDERS[m.provider];
          return (
            <div key={i} style={{
              padding: '16px 20px',
              borderRight: i % 2 === 0 && responses.length > 1 ? '1px solid var(--rule)' : 0,
              borderBottom: '1px solid var(--rule)',
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
                <span style={{ color: p.color, fontSize: 14 }}>{p.glyph}</span>
                <span style={{ color: 'var(--ink)', fontWeight: 500, fontSize: 13 }}>{p.name}</span>
                <span className="dim" style={{ fontSize: 10.5 }}>· {p.vendor}</span>
                <span style={{ marginLeft: 'auto', display: 'flex', gap: 8 }}>
                  <Mono className="dim" style={{ fontSize: 10 }}>R$ {m.cost.toFixed(3)}</Mono>
                  <Mono className="dim" style={{ fontSize: 10 }}>{m.tokens} tok</Mono>
                </span>
              </div>
              <div style={{ fontFamily: 'var(--font-sans)', fontSize: 12.5,
                color: 'var(--ink-2)', lineHeight: 1.6, whiteSpace: 'pre-wrap' }}>{m.text}</div>
              <div style={{ marginTop: 12, display: 'flex', gap: 8 }}>
                <button className="k-btn ghost" style={{ fontSize: 11 }}>★ marcar</button>
                <button className="k-btn ghost" style={{ fontSize: 11 }}>↳ aprofundar</button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function ConversationView({ active }) {
  return (
    <div>
      {CONSILIUM_THREAD.filter(m => m.role === 'user' || active.includes(m.provider)).map((m, i) => {
        if (m.role === 'user') {
          return (
            <div key={i} className="k-msg user">
              <div className="k-msg-h">
                <span style={{ color: 'var(--ink)' }}>Roberto</span>
                <span style={{ marginLeft: 'auto' }}>{m.when}</span>
              </div>
              <div className="k-msg-b">"{m.text}"</div>
            </div>
          );
        }
        const p = PROVIDERS[m.provider];
        return (
          <div key={i} className="k-msg">
            <div className="k-msg-h">
              <span style={{ color: p.color, fontSize: 14 }}>{p.glyph}</span>
              <span style={{ color: 'var(--ink)', fontWeight: 500 }}>{p.name}</span>
              <span>· {p.vendor}</span>
              <span style={{ marginLeft: 'auto', display: 'flex', gap: 10 }}>
                <Mono style={{ fontSize: 10 }}>R$ {m.cost.toFixed(3)} · {m.tokens} tok</Mono>
                <span>{m.when}</span>
              </span>
            </div>
            <div className="k-msg-b">{m.text}</div>
          </div>
        );
      })}
    </div>
  );
}

function Composer() {
  return (
    <div className="k-comp">
      <Mono className="dim" style={{ fontSize: 14 }}>›</Mono>
      <input placeholder="pergunta ao conselho · contexto da carteira anexado automaticamente" defaultValue="" />
      <button className="k-btn ghost" style={{ fontSize: 11 }}>⌬ contexto</button>
      <button className="k-btn primary">enviar →</button>
    </div>
  );
}

function ContextChips({ scenario }) {
  const d = SCENARIOS[scenario];
  const chips = [
    `patrimônio ${brl(d.total, { compact: true })}`,
    `caixa ${(d.cash * 100).toFixed(0)}%`,
    `fragility ${d.fragility.toFixed(2)}`,
    `anti-bs ${d.antiBs.score}/100`,
    `${d.theses.length} teses`,
    `cen. ${d.label.toLowerCase()}`,
    `selic 9.5%`, `ibov +6.1% YTD`,
  ];
  return (
    <div>
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
        {chips.map(c => <span key={c} className="k-chip">{c}</span>)}
      </div>
      <Mono className="dim" style={{ fontSize: 10, marginTop: 10, display: 'block' }}>
        ~ 1.842 tokens · enviado em todas as chamadas
      </Mono>
    </div>
  );
}

window.PageConsilium = PageConsilium;
