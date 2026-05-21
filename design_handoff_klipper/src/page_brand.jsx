// page_brand.jsx — Identidade Klipper · marca oficial (assets PNG)

function PageBrand() {
  return (
    <div className="k-page">
      {/* HERO — official lockup, dark variant */}
      <Card padded={false} style={{ overflow: 'hidden', marginBottom: 16 }}>
        <div style={{ padding: 0, background: '#0A1626',
          display: 'grid', placeItems: 'center', minHeight: 340 }}>
          <img src="brand/klipper-lockup-dark.png"
            alt="Klipper · dark mode lockup"
            style={{ maxWidth: 640, width: '70%', height: 'auto', display: 'block' }} />
        </div>
      </Card>

      {/* Construction + intro */}
      <div style={{ display: 'grid', gridTemplateColumns: '1.4fr 1fr', gap: 16, marginBottom: 16 }}>
        <Card title="Klipper" kicker="identidade · v1.0" gilt>
          <p style={{ margin: 0, fontFamily: '"Instrument Serif", serif', fontStyle: 'italic',
            fontSize: 18, color: 'var(--ink-2)', lineHeight: 1.55, marginBottom: 16 }}>
            "Ordem, fluxo e decisão inteligente — uma marca pensada para um wealth OS,
            não para um banco."
          </p>
          <div style={{ display: 'grid', gridTemplateColumns: '120px 1fr', gap: 18,
            alignItems: 'center' }}>
            <img src="brand/klipper-icon-dark.png" alt="Klipper mark"
              style={{ width: 120, height: 120, borderRadius: 26, display: 'block' }} />
            <ul style={{ margin: 0, paddingLeft: 16, fontSize: 12.5,
              color: 'var(--ink-2)', lineHeight: 1.7,
              fontFamily: '"General Sans","Inter",sans-serif' }}>
              <li>Monograma K · stem sólido + lâmina diagonal</li>
              <li>Lâmina azul-gradiente · proa do clipper · decisão</li>
              <li>Geometria modular · ângulos 45°</li>
              <li>Funciona em dark, light, gradiente</li>
              <li>Squircle (iOS-style) para favicon/app icon</li>
            </ul>
          </div>
        </Card>

        <Card title="Lockup horizontal" kicker="marca + wordmark · escalas">
          <div style={{ display: 'flex', flexDirection: 'column', gap: 18 }}>
            {[64, 44, 28].map(s => (
              <div key={s} style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
                <img src="brand/klipper-icon-dark.png" alt=""
                  style={{ width: s, height: s, borderRadius: Math.round(s * 0.22),
                    display: 'block' }} />
                <span style={{ fontFamily: '"General Sans","Inter",sans-serif',
                  fontSize: s * 0.92, fontWeight: 600, letterSpacing: '-0.025em',
                  lineHeight: 1, color: 'var(--ink)' }}>
                  Klipper
                </span>
                <Mono className="dim" style={{ fontSize: 10, marginLeft: 'auto' }}>{s}px</Mono>
              </div>
            ))}
          </div>
        </Card>
      </div>

      {/* Icon variants — 4 backgrounds */}
      <SecHeader title="Variações do app icon" sub="sistema modular · 4 backgrounds" />
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 16, marginBottom: 20 }}>
        {[
          { label: 'Light',     src: 'brand/klipper-icon-light.png',    bg: '#EEEEEE' },
          { label: 'Dark',      src: 'brand/klipper-icon-dark.png',     bg: '#0A1626' },
          { label: 'Gradient',  src: 'brand/klipper-icon-gradient.png', bg: '#1E5BD3' },
          { label: 'Black',     src: 'brand/klipper-icon-black.png',    bg: '#0A0A0A' },
        ].map((v, i) => (
          <Card key={i} padded={false}>
            <div style={{ padding: 22, background: v.bg, display: 'grid',
              placeItems: 'center', borderRadius: 'var(--radius) var(--radius) 0 0' }}>
              <img src={v.src} alt={v.label}
                style={{ width: 168, height: 168, borderRadius: 38, display: 'block',
                  boxShadow: '0 12px 28px rgba(0,0,0,0.35)' }} />
            </div>
            <div style={{ padding: '12px 16px', display: 'flex',
              justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontFamily: '"General Sans","Inter",sans-serif',
                fontSize: 12.5, color: 'var(--ink)', fontWeight: 500 }}>{v.label}</span>
              <Mono className="dim" style={{ fontSize: 10 }}>{v.bg}</Mono>
            </div>
          </Card>
        ))}
      </div>

      {/* Lockup banners */}
      <SecHeader title="Lockups · banners" sub="dark mode · gradient background" />
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 20 }}>
        <Card padded={false}>
          <img src="brand/klipper-lockup-dark.png" alt="dark mode lockup"
            style={{ width: '100%', height: 'auto', display: 'block',
              borderRadius: 'var(--radius)' }} />
        </Card>
        <Card padded={false}>
          <img src="brand/klipper-lockup-gradient.png" alt="gradient lockup"
            style={{ width: '100%', height: 'auto', display: 'block',
              borderRadius: 'var(--radius)' }} />
        </Card>
      </div>

      {/* Legibility scale */}
      <SecHeader title="Legibilidade · escalas" sub="16 → 128 px" />
      <Card style={{ marginBottom: 20 }}>
        <div style={{ display: 'flex', alignItems: 'flex-end', gap: 28, padding: '14px 4px',
          flexWrap: 'wrap' }}>
          {[16, 24, 32, 48, 64, 96, 128].map(s => (
            <div key={s} style={{ display: 'flex', flexDirection: 'column',
              alignItems: 'center', gap: 8 }}>
              <img src="brand/klipper-icon-dark.png" alt=""
                style={{ width: s, height: s, borderRadius: Math.round(s * 0.22),
                  display: 'block' }} />
              <Mono className="dim" style={{ fontSize: 9.5 }}>{s}px</Mono>
            </div>
          ))}
        </div>
      </Card>

      {/* Palette */}
      <SecHeader title="Paleta" sub="náutico · base + acentos" />
      <Card padded={false} style={{ marginBottom: 16 }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(6, 1fr)', gap: 0 }}>
          {[
            { name: 'Bg deep',   hex: '#08161F', token: '--bg',     ink: '#F2EAD3' },
            { name: 'Bg ambient',hex: '#0C1E2B', token: '--bg-2',   ink: '#F2EAD3' },
            { name: 'Parchment', hex: '#F2EAD3', token: '--ink',    ink: '#08161F' },
            { name: 'Brass',     hex: '#D9B26F', token: '--brass',  ink: '#08161F' },
            { name: 'Sea',       hex: '#7FB3C8', token: '--sea',    ink: '#08161F' },
            { name: 'Moss',      hex: '#7BC68A', token: '--moss',   ink: '#08161F' },
            { name: 'Lantern',   hex: '#F4D58D', token: '--lantern',ink: '#08161F' },
            { name: 'Copper',    hex: '#E08855', token: '--copper', ink: '#08161F' },
            { name: 'Rust',      hex: '#D87C6A', token: '--rust',   ink: '#08161F' },
            { name: 'Ink-2',     hex: '#C9BC9E', token: '--ink-2',  ink: '#08161F' },
            { name: 'Ink-3',     hex: '#8F8770', token: '--ink-3',  ink: '#F2EAD3' },
            { name: 'Rule',      hex: 'rgba(255,255,255,.06)', token: '--rule', ink: '#F2EAD3' },
          ].map((c, i) => (
            <div key={i} style={{ background: c.hex.startsWith('rgba') ? '#0C1E2B' : c.hex,
              padding: '18px 16px', minHeight: 100, color: c.ink,
              display: 'flex', flexDirection: 'column', justifyContent: 'space-between',
              borderRight: i % 6 !== 5 ? '1px solid var(--rule)' : 0,
              borderBottom: i < 6 ? '1px solid var(--rule)' : 0 }}>
              <div style={{ fontFamily: '"General Sans","Inter",sans-serif',
                fontSize: 11.5, fontWeight: 600, letterSpacing: '-0.01em' }}>{c.name}</div>
              <div>
                <div style={{ fontFamily: '"Geist Mono", monospace', fontSize: 10,
                  opacity: 0.85 }}>{c.token}</div>
                <div style={{ fontFamily: '"Geist Mono", monospace', fontSize: 10,
                  opacity: 0.6, marginTop: 2 }}>{c.hex}</div>
              </div>
            </div>
          ))}
        </div>
      </Card>

      {/* Type stack */}
      <SecHeader title="Tipografia" sub="3 famílias · 1 personalidade" />
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 16, marginBottom: 16 }}>
        <Card title="General Sans" kicker="ui · body">
          <div style={{ fontFamily: '"General Sans","Inter",sans-serif',
            fontSize: 56, fontWeight: 600, lineHeight: 0.95, color: 'var(--ink)',
            letterSpacing: '-0.025em' }}>Aa</div>
          <div style={{ marginTop: 14, color: 'var(--ink-2)', fontSize: 12.5,
            fontFamily: '"General Sans","Inter",sans-serif', lineHeight: 1.5 }}>
            Toda a interface — navegação, tabelas, chips, botões. Geométrica,
            premium, sem clichê fintech.
          </div>
          <Mono className="dim" style={{ fontSize: 10, marginTop: 12, display: 'block' }}>
            200 · 300 · 400 · 500 · 600 · 700
          </Mono>
        </Card>
        <Card title="Instrument Serif" kicker="hero · editorial">
          <div style={{ fontFamily: '"Instrument Serif", serif',
            fontSize: 64, lineHeight: 0.95, color: 'var(--ink)',
            letterSpacing: '-0.02em' }}>Aa</div>
          <div style={{ marginTop: 14, color: 'var(--ink-2)', fontSize: 12.5,
            fontFamily: '"General Sans","Inter",sans-serif', lineHeight: 1.5 }}>
            Patrimônio hero, narrativas, citações Anti-BS. Itálico fino para
            momentos editoriais.
          </div>
          <div style={{ fontFamily: '"Instrument Serif", serif', fontStyle: 'italic',
            fontSize: 14, color: 'var(--ink-3)', marginTop: 12 }}>
            "matemática ancora"
          </div>
        </Card>
        <Card title="Geist Mono" kicker="data · timestamps">
          <div style={{ fontFamily: '"Geist Mono", monospace',
            fontSize: 56, fontWeight: 500, lineHeight: 0.95, color: 'var(--ink)',
            letterSpacing: '-0.02em' }}>Aa</div>
          <div style={{ marginTop: 14, color: 'var(--ink-2)', fontSize: 12.5,
            fontFamily: '"General Sans","Inter",sans-serif', lineHeight: 1.5 }}>
            Números, deltas, horários, tickers, custo IA. Tabular para colunas
            alinhadas pixel a pixel.
          </div>
          <Mono className="dim" style={{ fontSize: 11, marginTop: 12, display: 'block' }}>
            R$ 1.847.500 · +0.81% · 09:42
          </Mono>
        </Card>
      </div>

      {/* Voice */}
      <SecHeader title="Voz" sub="o que o Klipper diz" />
      <Card>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24, fontSize: 13,
          fontFamily: '"General Sans","Inter",sans-serif' }}>
          <div>
            <Kicker style={{ color: 'var(--moss)' }}>Diz</Kicker>
            <ul style={{ paddingLeft: 18, margin: '8px 0 0', color: 'var(--ink-2)',
              lineHeight: 1.7 }}>
              <li>"matemática ancora"</li>
              <li>"vacância projetada Q3: 8.1% — kill-switch ativado"</li>
              <li>"incerteza: alta"</li>
              <li>"impulso detectado · primeiro do mês"</li>
            </ul>
          </div>
          <div>
            <Kicker style={{ color: 'var(--rust)' }}>Não diz</Kicker>
            <ul style={{ paddingLeft: 18, margin: '8px 0 0', color: 'var(--ink-3)',
              lineHeight: 1.7, fontStyle: 'italic' }}>
              <li>"momento ideal para comprar"</li>
              <li>"oportunidade imperdível 🚀"</li>
              <li>"você está rico!" / "você está mal"</li>
              <li>verborreia, hype, certezas vazias</li>
            </ul>
          </div>
        </div>
      </Card>
    </div>
  );
}

window.PageBrand = PageBrand;
