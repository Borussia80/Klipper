// data.jsx — Klipper humanized data
// Centro do sistema: fluxo. Transações têm narrativa, mood, recorrência, contexto.

const brl = (v, opts = {}) => {
  const { compact = false, sign = false, cents = true } = opts;
  if (compact) {
    if (Math.abs(v) >= 1e6) return (sign && v > 0 ? '+' : '') + 'R$ ' + (v / 1e6).toFixed(2).replace('.', ',') + ' M';
    if (Math.abs(v) >= 1e3) return (sign && v > 0 ? '+' : '') + 'R$ ' + (v / 1e3).toFixed(1).replace('.', ',') + ' k';
  }
  const s = v.toLocaleString('pt-BR', {
    minimumFractionDigits: cents ? 2 : 0,
    maximumFractionDigits: cents ? 2 : 0,
  });
  return (sign && v > 0 ? '+' : '') + 'R$ ' + s;
};
const pct = (v, d = 1) => (v >= 0 ? '+' : '') + v.toFixed(d) + '%';

// price-path generator — seeded
function genPath(n, start, vol, drift) {
  const out = [start];
  let x = start, s = 1;
  for (let i = 1; i < n; i++) {
    s = (s * 9301 + 49297) % 233280;
    const r = (s / 233280 - 0.5) * 2;
    x = x * (1 + drift + r * vol);
    out.push(Math.max(x, start * 0.4));
  }
  return out;
}

// ─── MOOD tagging on transactions ───
// planejado · necessário · prazer · investimento · obrigatório · impulso · social · saúde
// emoji-less; uses descriptors that show up as chips

// ─── CARDS — wallet-style ───
const CARDS = [
  {
    id: 'plat',
    bank: 'Itaú',
    brand: 'Mastercard Black',
    label: 'Black · pessoal',
    last4: '4218',
    color: 'linear-gradient(135deg, #1A1A1A 0%, #2A2A2A 60%, #0A0A0A 100%)',
    accent: '#D9B26F',
    limit: 38000,
    used: 18420.40,
    closing: '18/jun',
    due: '25/jun',
    next: 4280.00,
  },
  {
    id: 'amex',
    bank: 'American Express',
    brand: 'Platinum',
    label: 'Platinum · viagens',
    last4: '1009',
    color: 'linear-gradient(135deg, #E5E5E5 0%, #B8B8B8 50%, #8E8E8E 100%)',
    accent: '#0A2540',
    limit: 80000,
    used: 6240.10,
    closing: '20/jun',
    due: '02/jul',
    next: 5100.00,
    ink: '#0A2540',
  },
  {
    id: 'nu',
    bank: 'Nubank',
    brand: 'Ultravioleta',
    label: 'Ultravioleta · digital',
    last4: '8821',
    color: 'linear-gradient(135deg, #8200FF 0%, #4A0099 60%, #1A003A 100%)',
    accent: '#F2EAD3',
    limit: 22000,
    used: 3120.80,
    closing: '14/jun',
    due: '21/jun',
    next: 2840.00,
  },
  {
    id: 'pj',
    bank: 'Inter PJ',
    brand: 'Empresarial',
    label: 'Empresarial · PJ',
    last4: '5503',
    color: 'linear-gradient(135deg, #FF7A00 0%, #FF4500 70%, #BB2200 100%)',
    accent: '#FFF',
    limit: 15000,
    used: 9840.20,
    closing: '10/jun',
    due: '17/jun',
    next: 8120.00,
  },
];

// ─── PARCELAMENTOS — timeline visual ───
const PARCELAS = [
  { id:'mac',  title: 'MacBook Pro 14" M3',  store: 'Apple', total: 18900, n: 12, paid: 4,
    monthly: 1575, card: 'plat', start: '02/2026', end: '02/2027', tag: 'trabalho' },
  { id:'kit',  title: 'Cozinha planejada',    store: 'Todeschini', total: 24000, n: 24, paid: 9,
    monthly: 1000, card: 'plat', start: '08/2025', end: '08/2027', tag: 'casa' },
  { id:'cur',  title: 'Curso Quant (Insper)', store: 'Insper', total: 8400, n: 8, paid: 5,
    monthly: 1050, card: 'amex', start: '01/2026', end: '09/2026', tag: 'educação' },
  { id:'tv',   title: 'Smart TV LG 65"',      store: 'Magalu', total: 6800, n: 10, paid: 7,
    monthly: 680, card: 'nu', start: '11/2025', end: '09/2026', tag: 'casa' },
  { id:'odon', title: 'Implante odontológico', store: 'Sorria', total: 9600, n: 6, paid: 1,
    monthly: 1600, card: 'plat', start: '04/2026', end: '10/2026', tag: 'saúde' },
];

// ─── TRANSACTIONS — rich feed with narrative + mood ───
// k = tipo: in (entrada) | out (saída) | invest | parcela | recorrente
// mood: planejado | necessário | prazer | investimento | obrigatório | impulso | renda | saúde
function tx(d, time, t, k, v, opts = {}) {
  return { d, time, t, k, v, ...opts };
}

const TX = [
  // ── hoje · 21 mai
  tx('hoje', '14:32', 'Pão de Açúcar · feira semanal', 'out', -342.18,
     { cat: 'alimentação', mood: 'necessário', card: 'plat', note: 'compra normal, dentro da média' }),
  tx('hoje', '13:14', 'Uber para Faria Lima', 'out', -38.40,
     { cat: 'transporte', mood: 'necessário', card: 'nu' }),
  tx('hoje', '11:02', 'Vinho · Saint-Émilion 2019', 'out', -480.00,
     { cat: 'prazer', mood: 'impulso', card: 'amex', note: 'visita do Lucas no fim de semana' }),
  tx('hoje', '09:15', 'Aporte programado · TESOURO Selic 2029', 'invest', -3000.00,
     { cat: 'investimento', mood: 'planejado', auto: true }),

  // ── ontem · 20 mai
  tx('ontem', '18:42', 'Salário CLT · Acmecorp', 'in', 32400.00,
     { cat: 'renda', mood: 'renda', auto: true, note: 'líquido após IR + INSS' }),
  tx('ontem', '17:12', 'Aluguel apto Faria Lima', 'in', 4800.00,
     { cat: 'renda passiva', mood: 'renda', auto: true }),
  tx('ontem', '14:58', 'Consulta Dra. Helena · psicoterapia', 'out', -380.00,
     { cat: 'saúde', mood: 'saúde', card: 'amex' }),
  tx('ontem', '12:31', 'Almoço Tartar · com Mariana', 'out', -184.50,
     { cat: 'prazer', mood: 'social', card: 'nu' }),

  // ── 19 mai
  tx('19/05', '20:18', 'iFood · jantar família', 'out', -126.40,
     { cat: 'alimentação', mood: 'prazer', card: 'nu' }),
  tx('19/05', '15:00', 'Mensalidade escola · Maria', 'out', -3850.00,
     { cat: 'família', mood: 'obrigatório', card: 'plat', auto: true }),
  tx('19/05', '10:22', 'Spotify family', 'out', -34.90,
     { cat: 'assinaturas', mood: 'recorrente', card: 'nu', auto: true }),

  // ── 18 mai
  tx('18/05', '16:40', 'BTC · venda parcial 0,02', 'invest', 5282.00,
     { cat: 'rebalanceamento', mood: 'planejado', note: 'M2 alertou over-limit; corrigido para 5.8%' }),
  tx('18/05', '11:00', 'Academia Bodytech', 'out', -289.00,
     { cat: 'saúde', mood: 'saúde', auto: true, card: 'plat' }),

  // ── 17 mai
  tx('17/05', '21:14', 'Cinema Reserva · The Brutalist', 'out', -78.00,
     { cat: 'prazer', mood: 'prazer', card: 'nu' }),
  tx('17/05', '13:50', 'Pet Center · Lupin (banho+ração)', 'out', -312.20,
     { cat: 'pet', mood: 'necessário', card: 'plat' }),

  // ── 16 mai
  tx('16/05', '19:30', 'Restaurante Maní · aniv. Mariana', 'out', -842.00,
     { cat: 'prazer', mood: 'social', card: 'amex', note: 'planejado · presente já incluso' }),
  tx('16/05', '08:30', 'NF-e Consultoria · cliente Borealis', 'in', 18400.00,
     { cat: 'renda PJ', mood: 'renda', note: 'projeto Q1 entregue · 30d para o pagto seguinte' }),

  // ── 15 mai
  tx('15/05', '14:00', 'Conta de luz · Light', 'out', -348.20,
     { cat: 'casa', mood: 'obrigatório', auto: true }),
  tx('15/05', '13:50', 'Internet · Vivo Fibra', 'out', -189.00,
     { cat: 'casa', mood: 'obrigatório', auto: true }),

  // ── 14 mai
  tx('14/05', '20:12', 'AWS · servidor pessoal', 'out', -240.18,
     { cat: 'assinaturas', mood: 'recorrente', auto: true, card: 'pj' }),
  tx('14/05', '11:20', 'WEGE3 · compra mensal', 'invest', -8260.00,
     { cat: 'investimento', mood: 'planejado', auto: true }),

  // ── 12 mai
  tx('12/05', '09:00', 'BBAS3 · dividendos', 'in', 1620.00,
     { cat: 'provento', mood: 'renda', auto: true }),

  // ── 10 mai
  tx('10/05', '15:34', 'Livraria Cultura · 3 livros', 'out', -218.40,
     { cat: 'educação', mood: 'investimento', card: 'amex' }),
  tx('10/05', '12:00', 'Capybara espresso · café diário', 'out', -18.50,
     { cat: 'café', mood: 'prazer', card: 'nu' }),

  // ── 08 mai
  tx('08/05', '22:00', 'Apple One · família', 'out', -49.90,
     { cat: 'assinaturas', mood: 'recorrente', auto: true, card: 'plat' }),
];

// pre-compute totals from the rich feed (current month)
const monthIn = TX.filter(x => x.v > 0 && x.k !== 'invest').reduce((s, x) => s + x.v, 0);
const monthOut = TX.filter(x => x.v < 0 && x.k !== 'invest').reduce((s, x) => s + x.v, 0);
const monthInvest = TX.filter(x => x.k === 'invest').reduce((s, x) => s + x.v, 0);

// ─── BEHAVIOR insights (computed-ish, for narrative) ───
const BEHAVIOR = {
  thisMonth: {
    prazer: 1709.30,
    necessario: 4290.18,
    obrigatorio: 4387.20,
    impulso: 480.00,
    social: 1026.50,
    saude: 669.00,
  },
  lastMonth: {
    prazer: 980.40,
    necessario: 4180.20,
    obrigatorio: 4187.20,
    impulso: 0,
    social: 540.00,
    saude: 380.00,
  },
  streak: { saved: 14, label: '14 dias respeitando o orçamento de prazer' },
  insights: [
    { icon: '↑', tone: 'warn', title: 'Prazer +74% vs abril',
      body: '“visita Lucas + aniv. Mariana”. Compatível com o mês, mas vale notar.' },
    { icon: '✓', tone: 'pos',  title: 'Caixa atingiu meta M2',
      body: '22% do PL líquido em RF pós-fixada · acima do piso de 20%.' },
    { icon: '↳', tone: 'info', title: 'Parcelamento MacBook entrou no 4º mês',
      body: 'R$ 1.575/mês · 8 restantes · pré-pagar economiza R$ 240 em juros.' },
    { icon: '▲', tone: 'neg',  title: 'Vinho · impulso detectado',
      body: 'R$ 480 não estava no plano. Mood "impulso" · primeiro do mês.' },
  ],
};

// ─── AGENDA — próximos eventos financeiros ───
const AGENDA = [
  { d: 'amanhã',   when: '22/05', title: 'Fatura Nubank · Ultravioleta', v: -2840.00, tag: 'cartão', tone: 'warn' },
  { d: '24/05',    when: '24/05', title: 'IPVA · 3ª parcela',            v: -1240.00, tag: 'obrigatório', tone: 'neg' },
  { d: '27/05',    when: '27/05', title: 'Aporte programado · ITSA4',    v: -2000.00, tag: 'investimento', tone: 'pos' },
  { d: '01/06',    when: '01/06', title: 'Aluguel apto Vila Madalena',   v: -4800.00, tag: 'casa', tone: 'neg' },
  { d: '02/06',    when: '02/06', title: 'NF-e Borealis · 2ª tranche',   v: 18400.00, tag: 'renda PJ', tone: 'pos' },
];

// ─── PATRIMÔNIO snapshot (background data) ───
const SCENARIOS = {
  realista: {
    label: 'Realista', blurb: 'Carteira balanceada · mercado neutro',
    total: 1847500, delta30d: 14820, delta30dPct: 0.81,
    delta12m: 142340, delta12mPct: 8.34,
    cash: 0.22, fragility: 0.34,
    antiBs: { score: 91, flags: 0 },
    governance: {
      maxAsset:  { ok: true,  top: 'ITSA4',           value: 0.082, limit: 0.10 },
      maxThesis: { ok: true,  top: 'Brasil divid.',   value: 0.21,  limit: 0.25 },
      minCash:   { ok: true,  value: 0.22, limit: 0.20 },
    },
    path: genPath(180, 1705160, 0.018, 0.0005),
    allocation: [
      { id:'cash',  label: 'Caixa & equiv.', value: 0.22, color: 'cash' },
      { id:'rf',    label: 'Renda fixa',     value: 0.31, color: 'pos' },
      { id:'br',    label: 'Ações BR',       value: 0.18, color: 'accent' },
      { id:'us',    label: 'Ações US',       value: 0.14, color: 'accent-2' },
      { id:'fii',   label: 'Fundos imob.',   value: 0.09, color: 'warn' },
      { id:'crypto',label: 'Cripto',         value: 0.06, color: 'neg' },
    ],
    theses: [
      { id:'div',  name: 'Brasil dividendos',     alloc: 0.21, conviction: 4, perf12m: 11.2, status:'on-track', anchor: 'Yield > Selic real + 3pp · payout sustentável > 5y', risk: 0.32 },
      { id:'tech', name: 'Tech megacaps EUA',     alloc: 0.14, conviction: 5, perf12m: 18.7, status:'on-track', anchor: 'Free-cash-flow yield > Treasury 10y por nome', risk: 0.41 },
      { id:'rf',   name: 'Renda fixa pós-fixada', alloc: 0.24, conviction: 3, perf12m: 9.1,  status:'on-track', anchor: 'CDI + 1.5% · duration < 2y', risk: 0.12 },
      { id:'fii',  name: 'FII tijolo logística',  alloc: 0.09, conviction: 3, perf12m: -2.1, status:'watch',    anchor: 'Vacância < 8% · cap rate > IPCA + 6pp', risk: 0.38 },
      { id:'btc',  name: 'BTC seco',              alloc: 0.06, conviction: 2, perf12m: 24.3, status:'on-track', anchor: 'Cold storage · ≤ 6% PL · sem alavanc.', risk: 0.62 },
    ],
    positions: [
      { t:'ITSA4',  cls:'Ações BR', qty:4200, price:12.42, cost:9.86,  chg: 0.31 },
      { t:'BBAS3',  cls:'Ações BR', qty:1800, price:28.74, cost:24.10, chg:-0.62 },
      { t:'VALE3',  cls:'Ações BR', qty:900,  price:64.18, cost:70.22, chg: 1.04 },
      { t:'WEGE3',  cls:'Ações BR', qty:1200, price:41.30, cost:32.80, chg: 0.18 },
      { t:'MSFT',   cls:'Ações US', qty:80,   price:2412.10,cost:1980.40,chg: 0.42 },
      { t:'BRKB',   cls:'Ações US', qty:60,   price:2168.40,cost:1804.20,chg: 0.08 },
      { t:'HGLG11', cls:'FII',      qty:700,  price:152.80, cost:148.10, chg: 0.22 },
      { t:'TESOURO Selic 2029', cls:'RF', qty:1, price:572725, cost:534800, chg: 0.04 },
      { t:'BTC',    cls:'Cripto',   qty:0.42, price:264100, cost:198200, chg:-1.42 },
    ],
  },
  otimista: {
    label: 'Otimista', blurb: 'Bull run · exposição em risco crescendo',
    total: 2380400, delta30d: 184200, delta30dPct: 8.39,
    delta12m: 612800, delta12mPct: 34.7,
    cash: 0.14, fragility: 0.58,
    antiBs: { score: 64, flags: 2 },
    governance: {
      maxAsset:  { ok: false, top: 'BTC',                 value: 0.142, limit: 0.10 },
      maxThesis: { ok: false, top: 'Tech megacaps EUA',   value: 0.31,  limit: 0.25 },
      minCash:   { ok: false, value: 0.14, limit: 0.20 },
    },
    path: genPath(180, 1762000, 0.022, 0.0018),
    allocation: [
      { id:'cash',value: 0.14, label:'Caixa & equiv.', color:'cash'},
      { id:'rf',  value: 0.18, label:'Renda fixa',     color:'pos'},
      { id:'br',  value: 0.21, label:'Ações BR',       color:'accent'},
      { id:'us',  value: 0.24, label:'Ações US',       color:'accent-2'},
      { id:'fii', value: 0.09, label:'Fundos imob.',   color:'warn'},
      { id:'crypto',value:0.14,label:'Cripto',          color:'neg'},
    ],
    theses: [
      { id:'div',  name:'Brasil dividendos',     alloc:0.16, conviction:3, perf12m:18.4, status:'on-track',   anchor:'Yield > Selic real + 3pp', risk:0.34 },
      { id:'tech', name:'Tech megacaps EUA',     alloc:0.31, conviction:5, perf12m:42.1, status:'over-limit', anchor:'FCF yield > Treasury 10y', risk:0.52 },
      { id:'rf',   name:'Renda fixa pós-fixada', alloc:0.15, conviction:2, perf12m:9.4,  status:'on-track',   anchor:'CDI + 1.5%', risk:0.12 },
      { id:'fii',  name:'FII tijolo logística',  alloc:0.09, conviction:3, perf12m:4.8,  status:'on-track',   anchor:'Vacância < 8%', risk:0.38 },
      { id:'btc',  name:'BTC seco',              alloc:0.14, conviction:4, perf12m:78.6, status:'over-limit', anchor:'Cold storage', risk:0.74 },
    ],
    positions: [],
  },
  estressado: {
    label: 'Estressado', blurb: 'Drawdown · volatilidade alta · violações M2',
    total: 1520200, delta30d: -98400, delta30dPct: -6.08,
    delta12m: -184600, delta12mPct: -10.83,
    cash: 0.11, fragility: 0.82,
    antiBs: { score: 38, flags: 4 },
    governance: {
      maxAsset:  { ok: false, top: 'VALE3',          value: 0.121, limit: 0.10 },
      maxThesis: { ok: false, top: 'Brasil divid.',  value: 0.34,  limit: 0.25 },
      minCash:   { ok: false, value: 0.11, limit: 0.20 },
    },
    path: genPath(180, 1704800, 0.028, -0.0009),
    allocation: [
      { id:'cash',value:0.11, label:'Caixa & equiv.', color:'cash'},
      { id:'rf',  value:0.24, label:'Renda fixa',     color:'pos'},
      { id:'br',  value:0.34, label:'Ações BR',       color:'accent'},
      { id:'us',  value:0.12, label:'Ações US',       color:'accent-2'},
      { id:'fii', value:0.11, label:'Fundos imob.',   color:'warn'},
      { id:'crypto',value:0.08,label:'Cripto',         color:'neg'},
    ],
    theses: [
      { id:'div',  name:'Brasil dividendos',     alloc:0.34, conviction:4, perf12m:-8.4,  status:'over-limit', anchor:'Yield real positivo', risk:0.58 },
      { id:'tech', name:'Tech megacaps EUA',     alloc:0.12, conviction:4, perf12m:-12.2, status:'on-track',   anchor:'FCF yield > Treasury', risk:0.62 },
      { id:'rf',   name:'Renda fixa pós-fixada', alloc:0.21, conviction:5, perf12m: 8.9,  status:'on-track',   anchor:'CDI + 1.5%', risk:0.12 },
      { id:'fii',  name:'FII tijolo logística',  alloc:0.11, conviction:2, perf12m:-14.8, status:'breach',     anchor:'Vacância < 8% — REVISAR', risk:0.71 },
      { id:'btc',  name:'BTC seco',              alloc:0.08, conviction:2, perf12m:-32.1, status:'watch',      anchor:'Cold storage', risk:0.84 },
    ],
    positions: [],
  },
};

// ─── AI Consilium ───
const PROVIDERS = {
  claude:  { name: 'Claude',  vendor: 'Anthropic', color: '#D97757', glyph: '◇' },
  gemini:  { name: 'Gemini',  vendor: 'Google',    color: '#4285F4', glyph: '✦' },
  openai:  { name: 'GPT-4o',  vendor: 'OpenAI',    color: '#1ABC9C', glyph: '◉' },
  qwen:    { name: 'Qwen',    vendor: 'Alibaba',   color: '#B47AFF', glyph: '◈' },
  kimi:    { name: 'Kimi',    vendor: 'Moonshot',  color: '#FF9A4D', glyph: '◊' },
};

const CONSILIUM_THREAD = [
  { role: 'user', when: 'hoje · 09:42',
    text: 'Estou 22% em caixa e o FII logística está pingando há 3 meses (-2.1%). Vale aumentar exposição agora ou esperar Q3?' },
  { role: 'assistant', provider: 'claude', when: '09:42', cost: 0.018, tokens: 1240,
    text: 'Dois eixos: (1) caixa 22% está acima do piso M2 (20%) — há folga. (2) "-2.1%/12m" é narrativa: o que conta é vacância e cap rate.\n\nDados objetivos hoje:\n• Vacância setor logístico: 7.4% (limite tese: 8%)\n• Cap rate médio: IPCA + 6.8pp (limite: IPCA + 6pp)\n• Sua alocação: 9% (espaço até 25%/tese)\n\nVeredito: aumentar dentro de tolerância em DCA de 4 parcelas mensais. Não justifica all-in. Incerteza: alta — taxa real pode rondar 6.5% por mais 2 trimestres.' },
  { role: 'assistant', provider: 'gemini', when: '09:43', cost: 0.004, tokens: 980,
    text: 'Contexto macro: BCB sinaliza Selic terminal 9.5% até Q4. Curva DI precifica corte de 75bp em 6m. FII logística reage 60–90d antes do ciclo (correlação histórica -0.62 c/ Selic real).\n\nJanela > 18m: setup favorável. Risco: novos lançamentos no eixo Cajamar/Extrema. Vacância projetada Q3: 8.1% — acima do trigger.' },
  { role: 'assistant', provider: 'openai', when: '09:43', cost: 0.011, tokens: 870,
    text: 'Segunda opinião: concordo com a direção (aumentar gradual) mas discordo do tamanho. A tese está em "watch" há 90d — Anti-BS exige downgrade de conviction antes de novo aporte. Conviction atual 3/5 já é mediana. Sugiro 2 parcelas, não 4, e reavaliar após Q2.' },
  { role: 'assistant', provider: 'qwen', when: '09:43', cost: 0.0008, tokens: 540,
    text: 'Resumo (3 modelos): aumentar em DCA, tamanho controverso (2–4 parcelas), monitorar vacância Q3 (8% kill-switch). Custo total análise: R$ 0,17.' },
];

Object.assign(window, {
  CARDS, PARCELAS, TX, BEHAVIOR, AGENDA,
  SCENARIOS, CONSILIUM_THREAD, PROVIDERS,
  brl, pct,
  monthIn, monthOut, monthInvest,
});
