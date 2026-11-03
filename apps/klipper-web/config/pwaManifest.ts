// Manifest do PWA. Os ícones em public/icons/ têm exatamente as dimensões
// declaradas (o teste confere o cabeçalho PNG): o Android recusa ou deforma o
// ícone de instalação quando o arquivo não bate com `sizes`. O maskable fica
// separado do "any" porque a margem de segurança exigida pelo recorte do
// launcher deixaria o ícone comum pequeno demais.

export const APPLE_TOUCH_ICON = '/icons/apple-touch-icon.png'

export const pwaManifest = {
  name: 'Klipper — Wealth OS',
  short_name: 'Klipper',
  description: 'Seu sistema operacional financeiro pessoal',
  theme_color: '#07121E',
  background_color: '#07121E',
  display: 'standalone' as const,
  orientation: 'portrait' as const,
  icons: [
    { src: '/icons/icon-192.png', sizes: '192x192', type: 'image/png', purpose: 'any' },
    { src: '/icons/icon-512.png', sizes: '512x512', type: 'image/png', purpose: 'any' },
    { src: '/icons/icon-maskable-512.png', sizes: '512x512', type: 'image/png', purpose: 'maskable' },
  ],
}
