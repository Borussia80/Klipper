import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { describe, expect, it } from 'vitest'
import { APPLE_TOUCH_ICON, pwaManifest } from '../pwaManifest'

const publicDir = resolve(__dirname, '../../public')

function pngSize(publicPath: string): string {
  const png = readFileSync(resolve(publicDir, publicPath.replace(/^\//, '')))
  expect(png.subarray(1, 4).toString('ascii'), `${publicPath} não é PNG`).toBe('PNG')
  return `${png.readUInt32BE(16)}x${png.readUInt32BE(20)}`
}

describe('pwaManifest', () => {
  it('declara ícones 192 e 512 de propósito "any" para a instalação no Android', () => {
    const anySizes = pwaManifest.icons.filter((icon) => icon.purpose === 'any').map((icon) => icon.sizes)
    expect(anySizes).toEqual(expect.arrayContaining(['192x192', '512x512']))
  })

  it('tem ícone maskable separado, sem misturar "any maskable"', () => {
    expect(pwaManifest.icons.some((icon) => icon.purpose === 'maskable')).toBe(true)
    expect(pwaManifest.icons.every((icon) => !icon.purpose.includes(' '))).toBe(true)
  })

  it.each(pwaManifest.icons.map((icon) => [icon.src, icon.sizes]))(
    '%s tem exatamente as dimensões declaradas (%s)',
    (src, sizes) => {
      expect(pngSize(src)).toBe(sizes)
    },
  )

  it('apple-touch-icon é PNG 180x180 para o iPhone', () => {
    expect(pngSize(APPLE_TOUCH_ICON)).toBe('180x180')
  })
})
