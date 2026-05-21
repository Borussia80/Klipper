// app.jsx — Klipper root

const { useState: useStateA, useEffect: useEffectA } = React;

const TWEAK_DEFAULTS = /*EDITMODE-BEGIN*/{
  "mood": "default",
  "scenario": "realista",
  "showEngines": true
}/*EDITMODE-END*/;

const PAGE_META = {
  home:         { title: 'Home',         sub: 'fluxo · comportamento · feed' },
  transactions: { title: 'Movimento',    sub: 'ledger completo · filtros · mood' },
  cards:        { title: 'Cartões',      sub: 'carteira · faturas · saúde' },
  parcelas:     { title: 'Parcelas',     sub: 'compromissos · timeline · horizonte' },
  patrimonio:   { title: 'Patrimônio',   sub: 'wealth · M1 quant · M2 governance' },
  positions:    { title: 'Posições',     sub: 'carteira · marcação a mercado' },
  theses:       { title: 'Teses',        sub: 'apostas firmes · âncora quant' },
  consilium:    { title: 'AI Consilium', sub: 'M4 · multi-provider · auto-routing' },
  mobile:       { title: 'Captura',      sub: 'fase 6 · bot Telegram · zero-fricção' },
  brand:        { title: 'Marca',        sub: 'identidade Klipper · v1.0' },
};

function App() {
  const [t, setTweak] = useTweaks(TWEAK_DEFAULTS);
  const [page, setPage] = useStateA('brand');

  useEffectA(() => { applyMood(t.mood); }, [t.mood]);

  const data = SCENARIOS[t.scenario];
  const pm = PAGE_META[page];

  return (
    <div className="k-app">
      <Sidebar page={page} setPage={setPage}
        snapshot={data}
        governance={data.governance}
        showEngines={t.showEngines}
        scenario={data.label}
        agenda={AGENDA} />

      <main className="k-main">
        <TopBar title={pm.title} sub={pm.sub} mood={t.mood} dataDate="21 mai 2026"
          action={
            <div style={{ display: 'flex', gap: 6 }}>
              <button className="k-btn ghost" title="atualizar">↻</button>
              <button className="k-btn primary">+ Lançar</button>
            </div>
          } />

        {page === 'home'         && <PageHome scenario={t.scenario} showEngines={t.showEngines} />}
        {page === 'transactions' && <PageTransactions />}
        {page === 'cards'        && <PageCards />}
        {page === 'parcelas'     && <PageParcelas />}
        {page === 'patrimonio'   && <PagePatrimonio scenario={t.scenario} showEngines={t.showEngines} />}
        {page === 'positions'    && <PagePositions scenario={t.scenario} showEngines={t.showEngines} />}
        {page === 'theses'       && <PageTheses scenario={t.scenario} showEngines={t.showEngines} />}
        {page === 'consilium'    && <PageConsilium scenario={t.scenario} showEngines={t.showEngines} />}
        {page === 'mobile'       && <PageMobile />}
        {page === 'brand'        && <PageBrand />}
      </main>

      <TweaksPanel title="Tweaks · Klipper">
        <TweakSection label="Mood" />
        <TweakRadio label="Lente"
          value={t.mood}
          options={['default', 'terminal', 'editorial']}
          onChange={(v) => setTweak('mood', v)} />
        <div style={{ fontSize: 10.5, color: 'rgba(41,38,27,0.55)',
          marginTop: -4, lineHeight: 1.4 }}>
          {MOODS[t.mood].blurb}
        </div>

        <TweakSection label="Cenário de dados" />
        <TweakRadio label="Mercado"
          value={t.scenario}
          options={['otimista', 'realista', 'estressado']}
          onChange={(v) => setTweak('scenario', v)} />
        <div style={{ fontSize: 10.5, color: 'rgba(41,38,27,0.55)',
          marginTop: -4, lineHeight: 1.4 }}>
          {data.blurb}
        </div>

        <TweakSection label="Engines WikiAgent" />
        <TweakToggle label="Mostrar Fragility, Anti-BS, M2"
          value={t.showEngines} onChange={(v) => setTweak('showEngines', v)} />

        <TweakSection label="Navegação" />
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 4 }}>
          {NAV.map(n => (
            <button key={n.id} onClick={() => setPage(n.id)} style={{
              padding: '5px 8px', fontSize: 10.5, textAlign: 'left',
              background: page === n.id ? 'rgba(0,0,0,0.08)' : 'rgba(0,0,0,0.03)',
              border: '1px solid ' + (page === n.id ? 'rgba(0,0,0,0.25)' : 'rgba(0,0,0,0.08)'),
              borderRadius: 4, color: '#29261b', cursor: 'pointer',
            }}>{n.mark}  {n.label}</button>
          ))}
        </div>
      </TweaksPanel>
    </div>
  );
}

window.App = App;
ReactDOM.createRoot(document.getElementById('root')).render(<App />);
