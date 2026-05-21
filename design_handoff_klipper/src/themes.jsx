// themes.jsx — Nautical base + 3 moods (default / terminal / editorial)
// Mood é uma lente sobre o náutico: muda densidade, glow, tipografia secundária.
// A paleta base (azul profundo + latão) permanece.

const NAUTICAL_BASE = {
  // canvas / surfaces
  '--bg':          '#08161F',                  // deep open-sea
  '--bg-2':        '#0C1E2B',                  // ambient ink
  '--surface-1':   'rgba(255, 255, 255, 0.025)', // glass elev 1
  '--surface-2':   'rgba(255, 255, 255, 0.045)', // glass elev 2
  '--surface-3':   'rgba(255, 255, 255, 0.07)',  // glass elev 3
  '--surface-tint':'rgba(200, 163, 100, 0.04)',  // brass warmth in glass
  '--ink':         '#F2EAD3',                  // parchment
  '--ink-2':       '#C9BC9E',                  // muted parchment
  '--ink-3':       '#8F8770',                  // dim
  '--ink-4':       '#5C5746',                  // very dim
  '--rule':        'rgba(255, 255, 255, 0.06)',
  '--rule-2':      'rgba(255, 255, 255, 0.10)',
  '--rule-brass':  'rgba(200, 163, 100, 0.22)',

  // brand colors
  '--brass':       '#D9B26F',                  // primary accent — refined brass
  '--brass-soft':  'rgba(217, 178, 111, 0.18)',
  '--brass-glow':  'rgba(217, 178, 111, 0.35)',
  '--sea':         '#7FB3C8',                  // secondary — sea blue
  '--copper':      '#E08855',                  // alert / spend
  '--moss':        '#7BC68A',                  // income / positive
  '--rust':        '#D87C6A',                  // negative / loss
  '--lantern':     '#F4D58D',                  // warn

  // semantic
  '--pos':         '#7BC68A',
  '--neg':         '#D87C6A',
  '--warn':        '#F4D58D',
  '--accent':      '#D9B26F',
  '--accent-2':    '#7FB3C8',
  '--cash':        '#D9B26F',

  // depth — used by .elev-N classes
  '--shadow-1':    '0 1px 0 rgba(255,255,255,0.04) inset, 0 6px 18px rgba(0,0,0,0.35)',
  '--shadow-2':    '0 1px 0 rgba(255,255,255,0.05) inset, 0 12px 32px rgba(0,0,0,0.42)',
  '--shadow-3':    '0 1px 0 rgba(255,255,255,0.06) inset, 0 24px 60px rgba(0,0,0,0.5)',
  '--glow-brass':  '0 0 0 1px rgba(217,178,111,0.15), 0 0 32px rgba(217,178,111,0.10)',

  // typography — General Sans (UI) + Instrument Serif (hero) + Geist Mono (data)
  '--font-serif':  '"Instrument Serif", "Spectral", Georgia, serif',
  '--font-sans':   '"General Sans", "Inter", ui-sans-serif, system-ui, sans-serif',
  '--font-ui':     '"General Sans", "Inter", ui-sans-serif, system-ui, sans-serif',
  '--font-mono':   '"Geist Mono", "IBM Plex Mono", ui-monospace, Menlo, monospace',

  // shape
  '--radius-xs':   '6px',
  '--radius-sm':   '10px',
  '--radius':      '16px',
  '--radius-lg':   '20px',
  '--radius-xl':   '28px',
  '--radius-pill': '999px',

  // motion
  '--ease':        'cubic-bezier(0.2, 0.7, 0.2, 1)',
};

const MOODS = {
  default: {
    label: 'Bordo',
    blurb: 'Equilíbrio · uso diário',
    overrides: {
      '--bg':          '#08161F',
      '--ink':         '#F2EAD3',
      // hint of brass glow
      '--ambient':     'radial-gradient(circle at 18% -10%, rgba(217,178,111,0.07), transparent 45%), radial-gradient(circle at 90% 110%, rgba(127,179,200,0.06), transparent 55%)',
    },
  },
  terminal: {
    label: 'Terminal',
    blurb: 'Quant · análise · foco',
    overrides: {
      '--bg':          '#040A0F',
      '--bg-2':        '#06111A',
      '--ink':         '#E7EFF5',
      '--ink-2':       '#A8B5C0',
      '--brass':       '#39E0B0',          // green-quant accent
      '--accent':      '#39E0B0',
      '--brass-soft':  'rgba(57, 224, 176, 0.18)',
      '--brass-glow':  'rgba(57, 224, 176, 0.40)',
      '--glow-brass':  '0 0 0 1px rgba(57,224,176,0.20), 0 0 28px rgba(57,224,176,0.18)',
      '--font-ui':     '"Geist Mono", "IBM Plex Mono", ui-monospace, monospace',
      '--font-sans':   '"Geist Mono", "IBM Plex Mono", ui-monospace, monospace',
      '--ambient':     'radial-gradient(circle at 50% -20%, rgba(57,224,176,0.04), transparent 45%)',
      '--radius':      '8px',
      '--radius-lg':   '10px',
    },
  },
  editorial: {
    label: 'Editorial',
    blurb: 'Review · journaling · reflexão',
    overrides: {
      '--bg':          '#0F1B23',
      '--ink':         '#F8EFD7',
      '--font-sans':   '"Instrument Serif", Georgia, serif',
      '--font-ui':     '"General Sans", "Inter", ui-sans-serif, sans-serif',
      '--ambient':     'radial-gradient(circle at 50% 30%, rgba(244,213,141,0.06), transparent 55%)',
      '--radius':      '20px',
      '--radius-lg':   '28px',
    },
  },
};

function applyMood(moodKey) {
  const root = document.documentElement;
  // base nautical
  Object.entries(NAUTICAL_BASE).forEach(([k, v]) => root.style.setProperty(k, v));
  // mood overlay
  const m = MOODS[moodKey] || MOODS.default;
  Object.entries(m.overrides).forEach(([k, v]) => root.style.setProperty(k, v));
  document.body.dataset.mood = moodKey;
}

Object.assign(window, { NAUTICAL_BASE, MOODS, applyMood });
