declare module '@edusites/bancos-brasil' {
  export const SvgBanco: unknown
  export function obterPreset(slug: string): {
    formato?: string
    fundo?: string
  } | null
  export function listarBancos(): string[]
}
