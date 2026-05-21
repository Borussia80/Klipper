// page_mobile.jsx — Captura (Telegram bot mockup)

function PageMobile() {
  return (
    <div className="k-page">
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 380px', gap: 32, alignItems: 'start' }}>
        <div style={{ display: 'flex', justifyContent: 'center', padding: '12px 0' }}>
          <PhoneFrame><TelegramChat /></PhoneFrame>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
          <div>
            <Kicker>Fase 6 · captura zero-fricção</Kicker>
            <h2 className="serif" style={{ fontSize: 22, color: 'var(--ink)',
              margin: '6px 0 8px', fontWeight: 500, lineHeight: 1.25,
              letterSpacing: '-0.005em' }}>
              Bot do Telegram alimenta o Klipper sem fricção.
            </h2>
            <p className="ui" style={{ fontSize: 13, color: 'var(--ink-2)',
              lineHeight: 1.6, margin: 0 }}>
              Fale com o bot em linguagem natural. Lançamentos, perguntas ao Consilium
              e snapshots da carteira são processados e gravados no Supabase, respeitando
              as regras M2 e Anti-BS.
            </p>
          </div>

          <Card title="Comandos suportados" kicker="exemplos">
            <ul style={{ margin: 0, paddingLeft: 0, listStyle: 'none',
              display: 'flex', flexDirection: 'column', gap: 8, fontSize: 12.5 }}>
              {[
                ['/gastei',  'gastei 86,40 ifood'],
                ['/comprei', 'comprei 200 wege3 a 41,30'],
                ['/recebi',  'recebi 4800 aluguel'],
                ['/saldo',   'snapshot atual'],
                ['/tese',    'status das teses'],
                ['/?',       'pergunta livre ao Consilium'],
              ].map(([cmd, ex]) => (
                <li key={cmd} style={{ display: 'grid',
                  gridTemplateColumns: '90px 1fr', gap: 12, alignItems: 'baseline' }}>
                  <Mono style={{ color: 'var(--brass)' }}>{cmd}</Mono>
                  <span style={{ color: 'var(--ink-3)', fontFamily: 'var(--font-ui)' }}>{ex}</span>
                </li>
              ))}
            </ul>
          </Card>

          <Card title="Stack" kicker="produção">
            <ul style={{ margin: 0, paddingLeft: 18, fontFamily: 'var(--font-ui)',
              fontSize: 12, color: 'var(--ink-2)', lineHeight: 1.7 }}>
              <li>python-telegram-bot 21 (webhook)</li>
              <li>Supabase RPC para escrita atômica</li>
              <li>LiteLLM com fallback Claude → Gemini → Qwen</li>
              <li>Validação M2 antes do commit</li>
            </ul>
            <div className="k-chip warn" style={{ marginTop: 12 }}>
              ● status: pendente · pronto para deploy
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}

function PhoneFrame({ children }) {
  return (
    <div style={{
      width: 340, height: 700,
      background: '#06080A',
      borderRadius: 42, padding: 8,
      boxShadow: '0 40px 100px rgba(0,0,0,0.6), 0 0 0 1px rgba(217,178,111,0.18) inset, 0 0 28px rgba(217,178,111,0.08)',
      position: 'relative',
    }}>
      <div style={{ position: 'absolute', top: 14, left: '50%', transform: 'translateX(-50%)',
        width: 96, height: 24, background: '#000', borderRadius: 12, zIndex: 2 }} />
      <div style={{ width: '100%', height: '100%', background: '#0A1722',
        borderRadius: 34, overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
        {children}
      </div>
    </div>
  );
}

function TelegramChat() {
  return (
    <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
      <div style={{ height: 30, display: 'flex', justifyContent: 'space-between',
        alignItems: 'flex-end', padding: '0 22px 4px', fontSize: 11,
        color: 'var(--ink)', fontFamily: 'var(--font-mono)', fontWeight: 600 }}>
        <span>09:42</span>
        <span style={{ opacity: 0.7 }}>●●●● 5G  ▣</span>
      </div>

      <div style={{ background: '#0F1F2E', padding: '10px 16px',
        display: 'flex', alignItems: 'center', gap: 10,
        borderBottom: '1px solid rgba(255,255,255,0.06)' }}>
        <button style={{ background: 'none', border: 0,
          color: 'var(--brass)', fontSize: 18 }}>‹</button>
        <div style={{ width: 32, height: 32, borderRadius: '50%',
          background: 'var(--brass)', color: '#1A1106',
          display: 'grid', placeItems: 'center', fontSize: 14,
          fontFamily: 'var(--font-serif)', fontWeight: 700 }}>K</div>
        <div style={{ flex: 1 }}>
          <div style={{ color: 'var(--ink)', fontSize: 13, fontWeight: 600 }}>Klipper Bot</div>
          <div style={{ color: 'var(--ink-3)', fontSize: 10 }}>online · respondendo</div>
        </div>
        <span style={{ color: 'var(--ink-3)', fontSize: 16 }}>⋮</span>
      </div>

      <div style={{ flex: 1, padding: '14px 12px', overflowY: 'auto',
        background:
          'radial-gradient(circle at 10% 20%, rgba(217,178,111,0.06), transparent 50%),' +
          'radial-gradient(circle at 90% 80%, rgba(127,179,200,0.06), transparent 50%), #0A1722',
        display: 'flex', flexDirection: 'column', gap: 8 }}>
        <Bubble muted>terça-feira · hoje</Bubble>
        <Bubble side="right" time="09:38">gastei 86,40 ifood</Bubble>
        <Bubble side="left" time="09:38">
          <Mono style={{ fontSize: 10, color: 'var(--ink-3)' }}>✓ lançado · #alimentação</Mono>
          <div style={{ marginTop: 4 }}>
            <strong style={{ color: 'var(--ink)' }}>R$ -86,40</strong>
            <div style={{ fontSize: 10.5, color: 'var(--ink-3)', marginTop: 2 }}>
              maio até hoje: R$ -1.842 (-12% vs abr)
            </div>
          </div>
        </Bubble>
        <Bubble side="right" time="09:40">comprei 200 wege3 a 41,30</Bubble>
        <Bubble side="left" time="09:40">
          <Mono style={{ fontSize: 10, color: 'var(--lantern)' }}>▲ M2 check · ok</Mono>
          <div style={{ marginTop: 4, fontSize: 12 }}>
            +200 WEGE3 · <strong>R$ -8.260,00</strong><br />
            <span style={{ color: 'var(--ink-3)' }}>tese "BR dividendos" → 22.4% (limite 25%)</span>
          </div>
          <button style={{ marginTop: 10, padding: '6px 12px',
            border: '1px solid var(--brass)', background: 'transparent',
            color: 'var(--brass)', borderRadius: 18, fontSize: 11,
            fontFamily: 'var(--font-ui)', fontWeight: 600, cursor: 'pointer' }}>
            confirmar →
          </button>
        </Bubble>
        <Bubble side="right" time="09:42">/? vale aumentar fii logística agora?</Bubble>
        <Bubble side="left" time="09:42">
          <Mono style={{ fontSize: 10, color: 'var(--ink-3)' }}>↳ Consilium · 3 modelos</Mono>
          <div style={{ marginTop: 4, fontSize: 12, color: 'var(--ink)', lineHeight: 1.5 }}>
            Aumentar dentro de tolerância em DCA de 2 parcelas. Vacância projetada Q3 (8.1%)
            é o kill-switch. <span style={{ color: 'var(--ink-3)' }}>incerteza: alta</span>.
          </div>
          <Mono style={{ fontSize: 10, color: 'var(--ink-4)', marginTop: 6, display: 'block' }}>
            R$ 0,034 · 3.290 tok · ver completo no app →
          </Mono>
        </Bubble>
        <Bubble muted>Klipper está digitando…</Bubble>
      </div>

      <div style={{ padding: '8px 10px', background: '#0F1F2E',
        borderTop: '1px solid rgba(255,255,255,0.06)',
        display: 'flex', alignItems: 'center', gap: 8 }}>
        <span style={{ color: 'var(--ink-3)', fontSize: 18 }}>+</span>
        <div style={{ flex: 1, padding: '8px 14px', background: '#0A1722',
          borderRadius: 18, fontSize: 12, color: 'var(--ink-4)' }}>mensagem</div>
        <span style={{ color: 'var(--brass)', fontSize: 18 }}>◎</span>
      </div>
    </div>
  );
}

function Bubble({ children, side, time, muted }) {
  if (muted) {
    return (
      <div style={{ alignSelf: 'center', padding: '3px 10px',
        background: 'rgba(255,255,255,0.04)',
        borderRadius: 10, fontSize: 10, color: 'var(--ink-3)' }}>{children}</div>
    );
  }
  const right = side === 'right';
  return (
    <div style={{ alignSelf: right ? 'flex-end' : 'flex-start',
      maxWidth: '80%',
      background: right ? 'rgba(217,178,111,0.18)' : 'rgba(255,255,255,0.05)',
      color: 'var(--ink)',
      padding: '8px 12px',
      borderRadius: right ? '14px 14px 4px 14px' : '14px 14px 14px 4px',
      fontSize: 12.5, lineHeight: 1.4,
      border: '1px solid ' + (right ? 'rgba(217,178,111,0.3)' : 'rgba(255,255,255,0.06)'),
    }}>
      {children}
      {time && <span style={{ display: 'block', textAlign: 'right',
        fontSize: 9, color: 'var(--ink-3)', marginTop: 4,
        fontFamily: 'var(--font-mono)' }}>{time}</span>}
    </div>
  );
}

window.PageMobile = PageMobile;
